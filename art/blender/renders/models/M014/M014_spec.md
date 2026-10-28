# 014 Starstone — spec

Reference: `art/blender/assets/references/014.png` (STARSTONE, "Individual Asset Production Reference"; the sheet
footer says "PAGE 15/132", INDEX.md lists it as 14, "Starstone Low-Poly Construction Study"; 1024 × 1536 px).
Builder: `art/blender/kit/mcp/m014.py` → `build()` (stage 1: see "Stage 1 — Modelling").

User direction for every model: shapes must match the sheet; colours "need to match the master reference and blend
into the colors nearby. please ensure all color and textures are being made and applied." VFX and glow ship wherever
the sheet shows them.

All pixel boxes are sheet pixels `(x0, y0, x1, y1)`, top-left origin. Measurements come from the sheet's own pixels
with two masks (paper is #F3EDE5):
- **cyan** (the crystal): max > 90, b > r + 45, g > r + 35, sat > 0.28;
- **rock**: not paper (within 16 of #F3EDE5), max < 235, sat < 0.25, not cyan.

The scripts are in the session scratchpad, `m014_study/` (`measure.py`, `prof.py`, `samp.py`, `grade.py`, `haze.py`,
`extra.py`; `png.py` is the pure-Python PNG reader). Crops of every view are there too (`f34.png`, `front.png`,
`core_ex.png`, `lshell_ex.png`, …).

## Study (2a)

### 1. Classification, size and scale

- **Classification:** full asset (resource node). Hero budget 4000 tris; each part 1000.
- **What it is:** a cyan faceted gem ("Starlight Core") wedged in the cleft between **two big leaning rock shells**,
  with **a ring of faceted dome rocks** round the foot. WorldModeling §12.5: crystals are a faceted shaft with a short
  broad tip, quieter than the host rock's facets; §12.4: leave substantial host rock visible. Four labelled parts:
  Left Rock Shell, Starlight Core, Right Rock Shell, Base Rocks, each "(Reusable Part)".
- **Target size: about 11.8 W × 9.0 D × 7.8 H studs** (H ≈ 1.42× the 5.5-stud character; a rare node, between M013
  Sulfur's 7.0 H and M011 Amethyst's 9.45 H; the old R04 kit Starstone was 9.1 × 7.2 × 9.0). Tolerances: W ±0.5,
  D ±0.6, H ±0.3.
  - The sheet's front, side and rear views look down about **13°** (the far ground contact at the left and right ends
    sits 0.07–0.09 H above the front-most rock's), so their apparent heights include about 1 stud of depth.
    Corrected: front W ≈ 1.41 × 8.7 ≈ 12.3, rear W ≈ 1.32 × 8.4 ≈ 11.1 (mean 11.7); side D ≈ 1.03 × 8.8 ≈ 9.0.
  - The kit's front, side and rear cameras sit at 4° (`M.VIEWS`), so our renders will read a little wider and lower
    than the sheet. For a like-for-like check, also render at elevation 13° (see §4.2).

**Measured views** (bbox of cyan ∪ rock):

| View (search box) | bbox (px) | W : H | Crystal share of silhouette | Crystal spans (W fraction) | Crystal spans (H fraction) |
| --- | --- | --- | --- | --- | --- |
| Front three-quarter (40,106,530,430) | 45–522 × 107–428 | 1.49 | 15.4 % | 0.43–0.74 | 0.20–0.76 |
| "Rear" three-quarter (565,106,1000,430) | 565–984 × 110–426 | 1.33 | 3.6 % | 0.59–0.81 | 0.35–0.83 |
| Front (18,525,282,718) | 18–277 × 531–715 | 1.41 | 16.0 % | 0.43–0.74 | 0.18–0.75 |
| Side (287,525,508,718) | 295–493 × 525–717 | 1.03 (D : H) | 8.5 % | 0.57–0.84 | 0.21–0.80 |
| Rear (512,525,768,718) | 512–760 × 528–716 | 1.32 | 0 % | — | — |
| Top (776,522,995,718) | 792–981 × 526–715 | 1.00 (W : D) | 17.9 % | 0.31–0.74 | 0.26–0.77 (from the front edge) |

- **Reading:** a tall, peaked rock pile, its two shells rising like a split boulder. From the front, a big cyan gem
  shows in the V between them (about 1/6 of the silhouette); from the side only its front flank; from the back
  none of it.
- **Verifier check:** crystal share per view (±3 points), crystal spans, and the top profiles below (±0.05).

### 2. Silhouette and proportions per view

All heights are fractions of the view's apparent H; all widths of W. Build frame: front −Y, +X right, ground z 0.
Mappings used below: front view X = −5.9 + 11.8 f; rear view X = +5.9 − 11.8 f (screen right = −X); side view
Y = +4.5 − 9.0 f (camera at +X, screen right = front).

**Top profiles** (highest silhouette point per column; `prof.py`):

| f | 0.00 | 0.05 | 0.10 | 0.15 | 0.20 | 0.25 | 0.30 | 0.35 | 0.40 | 0.45 | 0.50 | 0.55 | 0.60 | 0.65 | 0.70 | 0.75 | 0.80 | 0.85 | 0.90 | 0.95 | 1.00 |
| --- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- |
| Front | .12 | .24 | .38 | .57 | .71 | .83 | .85 | .79 | .80 | .98 | 1.0 | .97 | .93 | .90 | .86 | .82 | .79 | .75 | .39 | .27 | .12 |
| Side | .08 | .17 | .25 | .47 | .65 | .76 | .86 | .93 | .99 | .99 | .92 | .85 | .80 | .76 | .71 | .67 | .62 | .38 | .29 | .23 | .09 |
| Rear | .09 | .18 | .24 | .59 | .65 | .71 | .77 | .82 | .88 | .94 | .99 | .96 | .84 | .81 | .85 | .79 | .71 | .62 | .44 | .25 | .12 |

**Front (and front three-quarter: the same picture, see §4.1):**
- **Left shell:** a lopsided pyramid, peak at f 0.27–0.30 (X ≈ −2.5), h 0.85. Its left flank falls at about 65° to
  (0.16, 0.56) and (0.09, 0.33); its right flank at about 60° through (0.41, 0.67), (0.43, 0.50) to (0.52, 0.27),
  hugging the crystal's left side all the way down. A ridge runs down its front from the peak, splitting a
  blue-grey shade face (left, about 1/3 of its width) from a big beige lit face (right).
- **Right shell:** the model's top, peak at f 0.47–0.52 (X ≈ 0), h 1.0. Its top edge (the "roof") runs down to the
  right at about 25° to (0.85, 0.75), then a near-vertical right end face drops to about 0.45, where base rocks cover
  it. From the peak its upper-left end falls steeply left to about (0.40, 0.80), behind the left shell's peak.
  Between the crystal's top edge and the right shell's lower-left edge a **dark inner face** shows (f 0.40–0.60,
  h 0.75–0.97): the underside of the right shell's upper end, hanging over the crystal.
- **Crystal:** in the V, f 0.43–0.74 × h 0.18–0.75. Top edge near-level from (0.45, 0.72) to (0.62, 0.74); right
  shoulder (0.72, 0.62); lowest visible point (0.65, 0.19), behind the front-centre rock. Its long axis tips about
  12° to the left (top towards −X).
- **Base rocks** (x fractions, top h): far-left 0.02–0.14 (0.24); left-mid 0.11–0.32 (0.21); front-centre 0.33–0.70
  (0.24, the widest, a low broad dome in front of the crystal's foot); right dome 0.66–0.89 (0.41, the tallest);
  far-right 0.89–1.0 (0.32); a tiny one at 0.90–0.98 (0.12).

**Side (camera +X):**
- One broad peaked mass: the right shell, nearest the camera, peak at f 0.40–0.45 (Y ≈ +0.7), h 0.99.
- Its back flank falls fast (0.15 → 0.47, 0.10 → 0.25). The gentler front slope (f 0.60 → 0.80, h 0.80 → 0.62) is
  **the crystal itself**: the crystal top-back corner is at (0.60, 0.80) (Y ≈ −0.9), its sloped cap runs down to the
  front shoulder at (0.80, 0.62), and its front flank is near-vertical down to (0.80, 0.26) (Y ≈ −2.7 to −3.1).
  So **the crystal leans back** (top towards +Y) about 13°, and the right shell does not reach forward past Y ≈ −0.5.
- Shade (blue-grey) face on the back half, lit beige face on the front half of the shell.
- **Base rocks:** back 0.03–0.20 (top 0.27); a broad one 0.20–0.54 (0.31); low front ones 0.56–0.88 (0.17); the
  tall right dome at the front, 0.82–0.99 (0.36).

**Rear (camera +Y; screen right = −X):**
- Mirrors the front: right shell peak at f 0.50 (X ≈ 0, h 0.99), its roof falling to screen left (+X) to 0.59 at
  f 0.15; the left shell's peak at f 0.70 (X ≈ −2.4, h 0.85); a valley between them at f 0.65 (h 0.81). **No crystal
  shows** (its top, about 0.76 H, stays below that valley).
- A **big back rock** fills the centre-right: f 0.35–0.89 (X +1.8 … −4.6), top h 0.55, covering both shells' lower
  halves. It is the exploded view's tall back rock (§3.4).
- Base rocks: 0.03–0.15 (0.23), 0.12–0.36 (0.25), 0.87–1.0 (0.24), a tiny one at 0.80–0.92 (0.12).
- The right shell's roof end is lower here (0.59 at X +4.1) than from the front (0.75): with a 13° camera that puts
  it **towards the back** (Y ≈ +2 … +3). The top view agrees (§2, Top).

**Top (front at the bottom):**
- Crystal in the middle, a rounded triangle pointing to the front (we see its sloped cap, so the top camera is tilted
  a little from the front).
- Left shell: the front-left mass, a long diamond from the back-left (f 0.06, d 0.7) to the front-centre (f 0.45,
  d 0.05) (d = depth fraction from the front edge): its long horizontal extent runs diagonally, broad face towards
  the front-right.
- Right shell: the back-right mass, f 0.39–0.95, d 0.57–0.96, roof lit.
- A big front-right mass (f 0.49–0.98, d 0–0.59) with a peak at about (0.74, 0.45): the tall right dome plus the
  far-right rocks.
- Small base rocks peek out at the back-left (two) and the right.
- The top view's crystal is proportionally larger (0.43 W) than the front's (0.31 W): use the top view for
  arrangement only (§4.3).

**Underside (close-up, (690,1050,960,1235)):** a cluster of 6 faceted rock bottoms; the big central one shows a broad
flat planar bottom ("Flat base for ground placement"). Everything is floor-cut flat at z 0.

**Core junction (close-up, (685,790,880,1005)):** the crystal's facets run straight into the shell's dark inner face
with a thin dark crease, "Tight fit, clean junction". No gap, no fillet, no rim. The inner face is a broad flat
plane parallel to the crystal's contact facet, darker and cooler (#69686B) than the shell's lit outer face (#B49E93).

**VFX overlay (panel (395,1280,690,1450)):** a pale cyan starburst halo of soft rays behind the whole model, about
1.3× the model's width, centred on the crystal's upper half. "Separate effect. Not part of model geometry." The main
views show no halo; they show only a teal spill on the rock next to the crystal (§5.4).

### 3. Parts (exploded view, box (30,790,665,1240))

The sheet's shared language: "chunky, low-poly … broad flat faces, clean silhouette", "Simple, solid colors. No
texture detail or noise", "Maintain clean junctions and consistent thickness". The rock faces are broad planes
(1.5–3 studs) with only very faint secondary faceting; no crumbs, no spikes. The arrows lift the left shell off the
left dome, the core out of the gap between the tall back rock and the right dome, and the right shell off the right
dome: the shells and the core stand **inside** the ring of base rocks, their feet hidden by it.

Exploded scale: the exploded left shell (245 px tall) equals the hero's left shell (6.6–6.7 studs), so about
**37 px per stud** in the exploded cell.

#### 3.1 Starlight Core: exploded (285,860,420,1065); hero close-ups (240,180,420,370), (110,560,220,700)

- **Shape: an elongated, slightly skewed hexagonal gem.** Not a long prism, not a sphere-like ball of triangles.
  - Exploded bbox 122 × 205 px: **W : H 0.60–0.63**, about **3.3 W × 2.8 D × 5.6 long** in studs (depth : width
    about 0.85, as M012's nodule).
  - **Cap (top 30–35 %):** a short slanted pyramid. The apex sits **off-centre, at 0.27 of the width** (the left
    side in the exploded drawing), and a long ridge runs from the apex down to the opposite shoulder, so the cap
    reads as one big sloped top face plus 3–4 smaller cap facets. The left shoulder is at 0.70 of the length from the
    bottom, the right one at 0.64 (the cap is tilted about 20–25°).
  - **Belt (0.40–0.70 of the length):** the widest part, 6 broad near-vertical facets; the front one is a big kite
    under the ridge (about 1/3 of the width), the side ones long trapezoids.
  - **Taper (bottom 40 %):** 6 long facets converging to a **blunt bottom point** about 0.55 of the width across
    (right of centre), with 2–3 small facets at the very tip.
  - Silhouette (exploded, fractions of the bbox): apex (0.27, 1.0); left shoulder (0.0, 0.70); right shoulder
    (1.0, 0.64); left flank to (0.04, 0.36); right flank to (0.88, 0.22); bottom point (0.51, 0.0).
  - **About 22–30 broad facets in all** (14–18 visible from one side), each 1.0–2.2 studs across. Edges meet in
    Y-junctions. 30–56 tris.
- **Construction:** convex hull of staggered rings, then `bmesh.ops.dissolve_limit` at 3–4° to merge coplanar hull
  triangles into broad facets, then BEAUTY triangulation (as M012's nodule). Check the merged facet count lands at
  22–30.

| Ring | Height (fraction of the length) | Points | Radius (fraction of the half-width) | Notes |
| --- | --- | --- | --- | --- |
| Apex ridge | 0.97–1.0 | 2 | — | apex at −0.45 of the half-width (towards −X in the part frame), second ridge point at (−0.1, 0.93) |
| Cap shoulders | 0.64–0.72 | 6 | 0.92–1.0 | the ring itself tilted ~22° (high on the apex side) |
| Belt low | 0.40 | 6 | 0.95 | aligned with the shoulders (same sector jitter), so the belt facets are planar trapezoids |
| Taper | 0.15 | 5–6 | 0.50 | half a step |
| Bottom point | 0.0–0.03 | 2–3 | 0.12 | offset +0.1 of the half-width |

  - Broad sector jitter only (±5 % radius, ±3 % height), never per-vertex noise.
- **Hero placement:** axis bottom (+1.6, −2.1, 0.35) → top (+0.4, −0.8, 5.85): leans **12° to −X and 13° back
  (+Y)**. The apex side of the cap points to −X/back, so the long cap ridge falls towards the front-right shoulder,
  as the hero close-up shows (ridge from the top-left corner down to the right shoulder). Front-most facet at
  Y ≈ −2.9; top at z ≈ 5.85–6.0 (0.75–0.77 H).
- **Fit:** its left flank sits flush on the left shell's right face, its upper back under the right shell's
  overhanging upper end, its foot down among the base rocks (the front-centre rock covers it below h 0.19 in the
  front view). The hero union makes the "tight, clean" junction; overlap the crystal 0.05–0.15 into each shell so the
  union leaves a crisp crease and no gap.

#### 3.2 Left Rock Shell: exploded (85,815,250,1060)

- **Shape:** a thick, tall, chunky slab. Exploded bbox 165 × 245 px → about **4.5 W × 2.6 D × 6.7 H** (W : H 0.67).
  - The **cross-section is a lopsided diamond / hexagon**: two broad faces meet in a ridge on the front (shade face
    about 1/3, lit face about 2/3 of the front width), with two narrower back faces.
  - **Top:** a blunt chisel wedge about 0.35 of the width, its short ridge sloping back, chamfered.
  - **Bottom:** the broadest part (just above the floor), with a chamfered lower ring; hidden in the hero.
  - The long faces are broken into 3–4 broad planes along the height (the exploded shows a clear break at about
    0.45 of the height, where the lower third steps out).
  - The exploded draws it leaning about 15° (top to the right).
- **Construction:** hull of 5 rings (bottom 0.0 r 0.90; lower 0.15 r 1.0; waist 0.45 r 0.95; upper 0.78 r 0.70;
  top chisel 0.97–1.0, 2–3 points r 0.30), 6–7 points per ring on a diamond-hexagon footprint (4.5 × 2.6), broad
  sector jitter ±6 %. Merge at 3–4°; 30–45 facets, 60–100 tris.
- **Hero placement:** base centre about (−2.4, −0.3), peak at (−2.5, 0.0, 6.6) (front view 0.85 H after the camera
  correction). **Yaw about −35°**, so the ridge points front-left and the broad lit face faces front-right, towards
  the crystal and the camera; lean 6–8° towards +X (into the crystal), 3° back. Front-view extent X −4.9 … +0.3;
  its lower part is hidden behind the left-mid and far-left rocks.

#### 3.3 Right Rock Shell: exploded (405,785,580,1005)

- **Shape:** a long, thick slab, the largest single piece. Long axis about 255 px → **7.2–7.4 long × 3.3 wide ×
  2.2–2.4 thick** (length about 2.2× its width).
  - One **broad, nearly flat upper face** (the lit "roof"), a narrower lower face, and two long side faces; the
    long edges are chamfered by a broad facet row.
  - **Ends:** the upper end is a chamfered wedge (the peak); the lower end a blunt, chamfered square-ish cut.
  - **The underside has a broad shallow concave step** at about 0.4 of its length from the lower end (the exploded
    shows a dent on the lower face). Build it as two faceted hull lobes unioned, not a carve, so the slab keeps clean
    broad planes. This is where the crystal tucks in; it reads as the dark inner face in the hero.
  - Drawn at about 50° (upper end to the upper-left).
- **Construction:** hull of a 6-point chamfered rectangle section at 4 stations along the length (ends at 0.0 and
  1.0 scaled to 0.75 and 0.60 for the end wedges; inner stations ±0.08 offset and ±3° twist so each long face breaks
  into 2–3 planes). 30–45 facets, 70–110 tris.
- **Hero placement:** long axis from the upper end (−0.2, +0.5, 7.8) down to the lower end (+4.6, +2.6, 0.6): about
  **55° from horizontal, falling to the right and to the back**. Roll it so the broad roof faces up, front and
  right (the front view sees the roof as a big lit face; the top view sees it at the back-right). Its upper end
  overhangs the crystal's top by about 0.5–0.8 stud (the dark inner face strip above the crystal). It must not reach
  forward of Y ≈ −0.5 (the side view's front slope is the crystal). Its lower end is hidden by the back-right rocks.

#### 3.4 Base Rocks: cluster (110,1030,520,1235); loose (65,1065,150,1135), (440,990,600,1110), (515,1095,595,1150)

- **One reusable rock part:** a faceted **dome / rounded cone**, H : W 0.6–0.85 for the domes and about 1.0 for the
  tall back rock (scale z).
  - A small off-centre crown (3–4 facets meeting at a blunt apex), 6–7 sloped facets, a near-vertical lower ring,
    flat bottom. About 16–24 broad facets, 32–50 tris.
  - Rings (fractions of height, radius): (0.0, 0.92, 7), (0.30, 1.0, 7), (0.65, 0.72, 6), (0.90, 0.30, 3),
    apex (1.0, 0.0–0.1, 1). Broad sector jitter ±7 %, apex offset 0.1–0.2 of the radius.
  - Loose rocks in the exploded: 2.7 × 3.0, 2.2 × 1.8, 2.1 × 1.5, 1.6 × 1.5 studs (W × H); cluster domes 4.0 × 3.2,
    4.6 × 2.4, 2.7 × 2.5; tall back rock 3.6 × 3.8.
- **Hero instances** (copies of the finished part mesh, as M013's `SulfurFootRock`; vary scale, yaw and a mirror so
  no two read as clones; floor-cut at z 0; sink 0.2–0.4 into neighbours):

| Rock | Centre (x, y) | W × D × H | Seen in |
| --- | --- | --- | --- |
| F1 front-centre (largest low dome) | (+0.2, −3.5) | 4.4 × 3.0 × 2.1 | front 0.33–0.70 (0.24); in front of the crystal's foot |
| F2 front left-mid | (−3.3, −3.1) | 2.5 × 2.2 × 1.8 | front 0.11–0.32 |
| F3 far left | (−5.0, −1.6) | 1.6 × 1.5 × 1.7 | front 0.02–0.14 |
| F4 right dome (tall) | (+3.3, −2.7) | 2.7 × 2.6 × 3.1 | front 0.66–0.89 (0.41); side front (0.36); top front-right |
| F5 far right | (+5.2, −1.2) | 1.4 × 1.6 × 1.9 | front 0.89–1.0 (0.32); side low front |
| F6 tiny front right | (+4.7, −3.3) | 0.8 × 0.7 × 0.6 | front 0.90–0.98 (0.12) |
| B1 big back rock | (−1.4, +2.6) | 5.0 × 3.8 × 4.2 | rear 0.35–0.89 (0.55); exploded tall back rock |
| B2 back right | (+3.4, +1.8) | 2.8 × 2.6 × 2.2 | rear 0.12–0.36 (0.25); side 0.20–0.54 (0.31) |
| B3 back right small | (+4.5, +3.3) | 1.5 × 1.5 × 1.8 | rear 0.03–0.15; side 0.03–0.20 |
| B4 back left | (−5.1, +1.8) | 1.5 × 1.5 × 1.8 | rear 0.87–1.0 (0.24); top back-left |
| B5 tiny back left | (−4.1, +3.4) | 0.9 × 0.8 × 0.7 | rear 0.80–0.92 (0.12); top back-left |

- No rock at the front between X −2.0 and +2.4 except F1 (the crystal must show above it), and none in front of the
  left shell's lit face above h 0.25.

#### 3.5 Starting layout summary (build frame, front −Y, ground z 0)

| Piece | Part | Anchor | Size | Orientation |
| --- | --- | --- | --- | --- |
| Left shell | `StarstoneShellLeft` | base (−2.4, −0.3, 0), peak (−2.5, 0.0, 6.6) | 4.5 × 2.6 × 6.7 | yaw −35°, lean 7° to +X, 3° back |
| Right shell | `StarstoneShellRight` | upper end (−0.2, +0.5, 7.8), lower end (+4.6, +2.6, 0.6) | 7.3 × 3.3 × 2.3 | long axis 55° from horizontal; roof rolled to face up-front-right |
| Core | `StarlightCore` | axis (+1.6, −2.1, 0.35) → (+0.4, −0.8, 5.85) | 3.3 × 2.8 × 5.6 | leans 12° to −X, 13° to +Y; apex side to −X/back |
| Base rocks | `StarstoneFootRock` × 11 | §3.4 table | | |

- **Expected hero:** about 11.8 W × 9.0 D × 7.8 H; right-shell peak is the top; crystal top about 0.75 H.
- **Tune against:** the top profiles (§2), the crystal shares and spans (§1), and the rear view's big back rock.
- **Triangles:** core 30–56, shells 60–110 each, rock part 32–50 (× 11 ≈ 450); the hero after union should land
  around 900–1800, well under 4000.

### 4. View conflicts and resolutions

1. **The sheet's front three-quarter is the front view.** Their top profiles, crystal spans (0.43–0.74 W both) and
   crystal shares (15.4 % / 16.0 %) are the same within 0.02; only W : H differs (1.49 / 1.41), i.e. the f34 is at
   most about 10° off the front.
   - **Resolution:** build to the front. Compare the sheet's f34 and front with an **extra render at azimuth 0 (or
     −8), elevation 13**. The kit's front34 (−28, 12) will show more of the left shell's shade face and less crystal
     (expect a share of about 10–13 %); judge it for sanity, not against the sheet's f34 outline.
2. **Camera elevation.** The sheet's front, side and rear look down about 13°; the kit's look down 4°. Render extras
   `{"front_sheet": (0, 13), "side_sheet": (90, 13), "rear_sheet": (180, 13)}` through `M.views(..., extra=...)`
   and compare the top profiles with those.
3. **Top view.** It is tilted (we see the crystal's sloped cap and the shells' faces), and its crystal is
   proportionally larger (0.43 W against the front's 0.31 W), its footprint square (W : D 1.0) against the front and
   side's 1.31. **Resolution:** front and side govern the sizes (W : D ≈ 1.31); the top view governs the arrangement
   only (crystal central, left shell front-left on a diagonal, right shell back-right, tall dome front-right, small
   rocks back-left and right). Compare it with an extra render at (0, 75) as well as the kit's (0, 89).
4. **The "rear three-quarter" cannot be a rear view.** Its outline repeats the front's (peaks at 0.27 / 0.40 against
   the front's 0.30 / 0.50, a long roof falling to the right, a low broad centre dome at 0.29 H against the front's
   0.24), with an extra slab drawn over the crystal. The real rear view has a big back rock to 0.55 H, the tall peak
   at the centre and no crystal.
   - **Resolution:** build to the rear view. From the sheet's r34 keep only: "from behind and the back-oblique, the
     crystal shows at most as a thin sliver near the top (≤ 5 %), against the sky past a shell edge". Check the
     kit's rear34 (152, 12) for crystal share ≤ 5 % and the rock composition, and also flip the sheet's r34
     horizontally when comparing it (it then matches a rear-right camera's peak order: tall at 0.60, lower at 0.73).
5. **Right shell orientation.** The side view's gentle front slope is the crystal, not the shell, and the rear view's
   lower roof end puts the shell's lower end at the back-right. **Resolution:** the right shell falls to the right
   **and back** (§3.3); it never reaches the front half.
6. **Exploded vs hero leans.** The exploded draws the left shell 15° off vertical and the right shell at 50°; the hero
   uses about 7° and 55° (the front view's flanks). The hero views govern.
7. **Size of the crystal.** The exploded crystal (W : H 0.62) is narrower than its front-view footprint (W : H 0.77);
   that difference is its 12° lean plus its cap tilt. Keep the part's own W : H at 0.60–0.63.

## 5. Colour plan for stage 4

### 5.1 Swatches (flat; medians of the inner 50 × 50 px)

| Swatch | Box | Hex | HSV |
| --- | --- | --- | --- |
| Starlight Core | (50,1310,100,1360) | #8CF8FD | 183°, 0.45, 0.99 |
| Rock Shell | (165,1310,215,1360) | #B6A69E | 20°, 0.13, 0.71 |
| Base Rock | (280,1310,330,1360) | #666262 | 0°, 0.04, 0.40 |

### 5.2 Rendered regions (pre-measured; `samp.py`)

Re-sample with `K.sample(..., "vivid")` for the crystal (note: vivid needs sat > 0.35, so the palest 10 % of the
crystal, sat 0.33, drops out; use the cyan mask above as a fallback) and `M.sample(..., "stone")` for the rock.
Median, lit quartile (top 25 % by luminance), shade quartile (low 25 %).

| Region | Box | Mask | Median | Lit | Shade |
| --- | --- | --- | --- | --- | --- |
| Crystal, f34 all | (249,183,398,363) | cyan | #48E3EC | #94FCFE | #1A8FA2 |
| Crystal, f34 cap (upper) | (265,185,370,265) | cyan | #58F1FA | #AAFDFE | #4D8FA0 |
| Crystal, f34 belt | (280,265,395,315) | cyan | #4AE8EE | #7DFBFE | #1DA5B5 |
| Crystal, f34 taper (lower) | (290,315,390,363) | cyan | #22B4C4 | #7CFAFD | #0F8397 |
| Crystal, front view | (129,577,210,681) | cyan | #47E3EC | #97FCFE | #1A8E9F |
| Crystal, side view | (408,563,462,677) | cyan | #73F8FB | #ABFDFD | #39D2D9 |
| Crystal, top view | (850,570,931,665) | cyan | #63E9F2 | #91FCFE | #168FA1 |
| Crystal, exploded all | (285,860,420,1065) | cyan | #47E8F0 | #79FCFE | #30C7D3 |
| Crystal, exploded upper third | (285,860,420,928) | cyan | #71FBFD | #91FCFE | #32E0F1 |
| Crystal, exploded middle third | (285,928,420,996) | cyan | #55F4F6 | #76FCFE | #33D3DE |
| Crystal, exploded lower third | (285,996,420,1065) | cyan | #38CDD5 | #43E6EA | #27BCC7 |
| Crystal, junction close-up | (688,795,800,1000) | cyan | #73F4F6 | #91FBFD | #2DBECC |
| Shells, front view | (40,535,250,650) | rock | #AF9A90 | #D2BFB5 | #68676D |
| Shell, side view | (320,530,450,650) | rock | #AA9A97 | #D1BCB1 | #6D6972 |
| Shells, rear view | (540,530,740,640) | rock | #968786 | #C2ACA3 | #786E6E |
| Left shell, f34 lit face | (170,170,250,300) | rock | #C3AFA6 | #D6C3B8 | #777178 |
| Left shell, f34 shade face | (105,200,160,320) | rock | #77727A | #888186 | #65636D |
| Right shell, f34 roof | (320,120,440,220) | rock | #CFBCB2 | #DBC9BD | #C3B1A8 |
| Right shell, f34 inner face above the crystal | (240,150,300,200) | rock | #616068 | #7B777D | #403F43 |
| Rock right of the crystal, f34 | (400,180,440,280) | rock | #B09A90 | #D1BEB3 | #5D5E63 |
| Left shell, exploded | (85,815,250,1060) | rock | #817A7F | #D2BCB0 | #696161 |
| Right shell, exploded | (405,785,580,1005) | rock | #948887 | #D1BCB0 | #5D5758 |
| Junction, shell inner face | (762,823,825,950) | rock | #69686B | #747075 | #5B5D60 |
| Junction, shell outer lit face | (815,800,872,880) | rock | #B49E93 | #CBB4A7 | #777172 |
| Base rocks, front view | (20,655,277,715) | rock | #93827E | #D1BCB0 | #605858 |
| Base rocks, side view | (295,655,493,717) | rock | #8D7C77 | #C1ACA3 | #5D5454 |
| Base rocks, rear view | (512,650,760,716) | rock | #91817C | #BCA69B | #625858 |
| Base rock, f34 front centre | (225,350,385,420) | rock | #9C8983 | #DAC5B8 | #6C6261 |
| Base rock, f34 right dome | (375,295,470,400) | rock | #BBA295 | #D7C3B6 | #6E625F |
| Base cluster, exploded | (110,1030,520,1235) | rock | #98857E | #D3BDAF | #685D5C |
| Loose rocks, exploded | (440,990,600,1110) | rock | #8A7E7C | #C4AC9F | #655C5B |
| Underside, flat bottom | (785,1135,870,1215) | rock | #6A5F5D | #6D6261 | #685C59 |

### 5.3 The crystal: how its colour works

Luminance deciles, dark → light (`grade.py`):

```
f34 (in the cleft):  #117A8B #1A96A9 #22AFC0 #2CC3D1 #36D7E4 #48E8F0 #59F4FB #79FBFE #83FCFD #AAFDFE
  hue/sat            188/.88 188/.85 186/.82 185/.79 184/.76 183/.70 183/.65 181/.52 180/.48 181/.33
exploded (free):     #28BFCB #31CAD4 #35D6DF #3ADBE2 #41E4E9 #56F4F7 #64FAFD #6DFBFD #76FCFE #92FDFE
  hue/sat            184/.80 184/.77 183/.76 183/.74 182/.72 181/.65 181/.60 181/.57 181/.54 181/.43
```

- **One hue family, 180–188°.** Light tones desaturate towards a pale aqua (sat 0.33–0.5); dark tones deepen to
  saturated teal (sat 0.8–0.9, hue 186–188). No green, no blue-violet.
- **It reads self-lit.** In the exploded view (no rock shadow) the darkest decile #28BFCB is still 0.70 of the
  lightest decile's luminance; the rock's ratio is 0.45. Shade facets stay bright cyan. Only inside the cleft
  (f34 p05 #117A8B) do they go deep teal.
- **No white facets.** p99 #D1FEFF; only thin ridge highlights reach #E2FEFF–#EAFFFF (under 0.5 % of the crystal),
  along the cap ridge and the belt's upper edges.
- **Top-to-bottom gradient.** Exploded bands (5, top first): #7AFBFD #6EFBFD #53F4F6 #3CDBE2 #30C7D2. The cap is the
  palest, the taper the deepest. In the hero the lowest visible facets drop to #22B4C4. That is painted region plus
  the cleft's shadow; paint the region, let the cleft shade the rest.
- **Facet-to-facet steps** are the gem read: neighbouring facets differ by one step (light ↔ mid ↔ deep), never a
  jump from the palest to the deepest.

### 5.4 The rock: how its colour works

- **Lit faces:** warm pinkish beige, hue 19–23°, sat 0.14–0.18 (#C6B2A7–#DBC8BD). **Shade faces:** cool violet-grey,
  hue 280–310°, sat 0.05–0.07 (#69666A–#837C82). That warm/cool split is the studio's warm key and cool fill, i.e.
  lighting: **do not paint it by facing.** Paint only a mild, broad warm/cool weathering.
- **Shells vs base rocks:** base rocks render about 10 % darker and browner (hue 11–16°, sat 0.14–0.16; medians
  #8D7C77–#9C8983) than the shells (#968786–#AF9A90). The Base Rock swatch (#666262) is far darker than any render:
  it is the foot tone, used for ground contact, crevices and the underside (#6A5F5D), not the rocks' body.
- **Inner faces:** where a shell faces the crystal or hangs over it, the rock is dark and cool (#616068 in the f34,
  #69686B in the close-up). That is occlusion by position (inside the cleft, under the overhang), which may be
  painted as a position field.
- **Teal spill:** 3432 rock pixels round the crystal in the f34 are tinted teal, median **#69828D** (198°, 0.26). They
  sit within 5 px (median), 17 px (p90), 22 px (p95) of the crystal, i.e. about **0.12 / 0.4 / 0.55 stud**. The
  junction close-up's crease is #3F545D. That is the crystal's light on the rock.
- **Exploded bands** (top → bottom): left shell #D1BCAF #B2A099 #A2908B #7D7377 #6A6060; right shell #C8B2A6
  #988C8D #998C89 #6C6364 #6B5F5E. Mostly lighting (their undersides), but the feet sitting among the base rocks
  are allowed a mild occlusion darkening.

### 5.5 Keys (start from these; `K.calibrate`; write the calibrated hexes into `palette()`)

Calibration targets are rendered medians, not swatches.

| Key | Calibration target | Where |
| --- | --- | --- |
| `m014_core_glow` | #7AFBFD (exploded top band); emissive, see §6 | the cap facets (the slanted top: apex, ridge face and 3–4 cap facets) |
| `m014_core_light` | #6EFBFD | the upper belt facets (just under the cap) and the front kite |
| `m014_core` | #53F4F6 (exploded middle; hero median #47E3EC–#48E3EC) | the belt |
| `m014_core_deep` | #30C7D2 (exploded bottom band; hero lower #22B4C4) | the taper and the bottom tip; contact faces against the rock |
| `m014_shell` | #A5948F (mean of front / side / rear shell medians) | both shells' bodies |
| `m014_shell_cool` | #8A8388 (about 320°, 0.05; half-way to the shade-face tone) | broad cool weathering patches on the shells, level 0.3 |
| `m014_shell_inner` | #66646A (inner faces #616068 / #69686B) | shell faces inside the cleft and under the right shell's overhang |
| `m014_spill` | #69828D (measured spill) | rock faces within about 0.4 stud of the crystal (both shells and F1 / B1 where they touch it) |
| `m014_foot` | #93827D (base medians #8D7C77–#9C8983) | the 11 base rocks |
| `m014_foot_dark` | #6A605E (between the Base Rock swatch #666262 and the underside #6A5F5D) | ground-contact rows, crevices between rocks, the underside, the shells' feet |

- **Calibration warnings:**
  - The crystal's lit tones have g and b near the clip (#xxFCFE), so calibrated crystal keys will sit near full
    saturation in g/b. Lower specular rather than raising brightness if the dome washes to white.
  - `K.sample`'s stone mask (sat < 0.18) drops some warm lit rock pixels (sat up to 0.20); use `M.sample`'s stone
    mask, as M011 and M013 did.
  - The spill and inner keys are small regions; calibrate them on their own dome, and re-measure in the hero with
    the light socket realised (`vfx=True`), since the crystal_glow light also tints the cleft.

### 5.6 Blending (mode `"blend"`, steps 3, over explicit face lists; fields are positions, never facing)

- **Crystal, in the core's own frame:** u = (height fraction along the axis) + 0.12 × (lateral position towards the
  apex side) + 0.08 × broad noise.
  - deep → core over u 0.15–0.40; core → light over u 0.48–0.66; the cap (above the shoulder ring) is the emissive
    `m014_core_glow` and meets the belt along a real geometric edge (a material boundary, hard by definition).
  - Contact: crystal faces within 0.3 of a shell or rock get at least a 50 % mix towards `core_deep` (the cleft's
    teal, f34 p05 #117A8B).
  - Keep the correlation with facing below 0.5 (`K.check`). The cap is bright and faces up, so the lateral and noise
    terms on the belt matter; M012's height-only bands scored 0.65.
- **Shells:**
  - body `shell`; broad weathering noise (scale about 0.2, patches 4–5 studs) shell ↔ shell_cool, level 0.3, width 0.5;
  - **inner field:** distance from the crystal surface d (plus the region under the right shell's overhang): 75 %
    `shell_inner` for d < 0.3, 50 % to 0.8, 25 % to 1.2;
  - **spill field:** on top of that, d < 0.15 → 75 % `spill`, < 0.3 → 50 %, < 0.45 → 25 %;
  - feet: the bottom 20 % of each shell's height → 25–50 % towards `foot_dark`.
- **Base rocks:** body `foot`; crown (top 30 % of each rock) 25 % towards `shell`, so they blend with the shells;
  the ground-contact row and faces within 0.3 of a neighbouring rock or shell → 25–50 % `foot_dark`; underside
  `foot_dark`.
- **Hard edges only where crystal meets rock.** They are separate keys, so this is automatic; the spill is on the rock
  side only.

### 5.7 Texture (Tint) and finish

**Tint:** per piece `tint_var` about 0.04 (neighbouring rocks and the two shells differ slightly). `K.texture` rock:
amp 0.05, patches about 2 studs (scale 0.45), jitter ±0.015. Crystal: amp 0.02 or none (the sheet: "No texture
detail or noise"; emissive keys ignore Tint in the export anyway). Broad and calm, never confetti.

**Finish:**

| Material | Roughness | Specular | Metal | Notes |
| --- | --- | --- | --- | --- |
| Crystal (core, light, deep) | 0.25–0.3 | moderate-low | 0 | glossy; lit facets pale aqua, ridge glints only, never white facets |
| Crystal cap (`core_glow`) | 0.3 | low | 0 | emissive (§6) |
| Shells | 0.9 | normal | 0 | matte |
| Base rocks | 0.92 | normal | 0 | matte |

## 6. Lighting and VFX plan (stages 5 and 6)

**What the sheet shows:**
- The crystal reads self-lit (shade facets stay bright, §5.3) and is called "Starlight".
- A separate "Starlight Glow (VFX)" panel: a pale cyan starburst halo behind the whole model (rays #C5F0ED,
  about 1.3× the model's width). "Not part of model geometry."
- A teal spill on the rock right round the crystal (§5.4) in every assembled view.
- Bright pale ridge glints on the crystal's cap ridge and belt edges (#E2FEFF–#EAFFFF).
- No smoke, dust, embers or motes.

**Stage 5 (lighting):**
- **Emissive part: the cap only.** Give `m014_core_glow` emission ≥ 1.0 (start 1.0–1.5) on the cap facets, so it
  exports as a Neon piece. Reasons:
  - The user's standing rule: glowing crystals ship an emissive part and a socket ([[kit-vfx-always]]).
  - **Not the whole crystal:** `export_kit_roblox.py` makes every face with emission ≥ `GLOW_EMISSION` (1.0) a Neon
    part, one per key, unlit and in one flat colour. Neon on the belt and taper would erase the facet-to-facet steps
    that make it read as a cut gem (the sheet's "flat shaded" core). Neon pieces also get no collision, which is fine
    for a cap 5–6 studs up.
  - Emission between 0 and 1 does nothing in Roblox except drop the Tint; don't use it as a "subtle glow".
  - Pick the key so the kit render's cap median lands near #8EFCFE–#A0FCFE (the f34 cap's lit range), not white.
    The exported Neon colour is the key's hex, and Neon brightens in game: if the key is at #7AFBFD or above, check
    in Studio that it doesn't read white.
  - Decide from a render: if the Neon cap reads as a separate light bulb on top, cut it to the 2–3 largest cap
    facets and record why.
- **Light:** a `crystal_glow` socket (PointLight) at about **(+0.9, −3.6, 3.6)** in the build frame, in the open, about
  0.8–0.9 stud in front of the belt and 1.5 above F1. Colour #6EF2F8, brightness 1.0, range 12, shadows true, no
  flicker, no pulse. It gives the teal spill and the self-lit shade side in Roblox, which keys alone can't guarantee
  under in-game lighting. Re-check the point is ≥ 0.8 stud from every surface (BVH) after any layout change.
- Studio note to record: the glow assumes the place's default Bloom; if bloom is off, the Neon cap still reads, the
  halo emitter carries the rest.

**Stage 6 (VFX):**
- **Halo** (the sheet's "Starlight Glow"): one emitter with the `glow_soft` texture, colour ["#C5F0ED", "#6EF2F8"],
  size [12, 14], transparency [0.82, 1.0], lifetime [2, 3], rate 0.8, speed 0, spread 0, light_emission 1.0, at
  about **(+0.6, −0.6, 4.2)** (behind the crystal's centre, so the rock in front hides the middle of the billboard
  and the rays show round the silhouette, as on the sheet).
  - There is no halo kind in `vfx.py`. `crystal_glow` is documented as "Light only", and M011 noted that overriding a
    kind's emitters makes a different effect under a wrong name. **Ask the main session** to add a small
    `crystal_halo` kind (emitters only, light None, texture `glow_soft`, which already exists) and use it. Fallback if
    it declines: put the Halo emitter in the `crystal_glow` socket's overrides and record the reason.
- **Sparkle:** 3 `ore_glint` sockets with colour ["#F2FFFF", "#8CF8FD"] and the spark_diamond texture ("starlight"),
  boxes tight round the facets where the sheet's ridge glints sit:
  - cap apex / ridge, about (+0.45, −0.85, 5.7): rate 0.5, size 0 → 0.6 → 0;
  - upper-right shoulder, about (+2.2, −1.6, 4.4): rate 0.35, size 0 → 0.45 → 0;
  - left belt ridge, about (−0.3, −2.3, 3.4): rate 0.25, size 0 → 0.45 → 0.
  The box centres may sit just inside the crystal (as M011's did); the boxes must reach the facet surfaces.
- All sockets go on the hero only (the parts carry none), as M011 did. Check the export STATS line reports 5 sockets
  (or 4 plus the halo override) and 1 glow piece.
- Render with `vfx=True`. The halo's preview stand-in is large: if it veils the model in the compare renders, render
  the compare set with the halo hidden and one extra shot with it, and record that.

## 7. Naming

The R04 kit sheet owns the old Starstone set (`R04_stats.json`, `scripts/kit/R04/starstone.py`): `Starstone`,
`StarstoneStoneShell`, `StarstoneStoneShellB`, `StarstoneStarlightCore`, `StarstoneBaseRock`, `StarstoneDepleted`,
`StarlightShard`, `StarlightShardB`, and the keys `r04_star_stone`, `r04_starlight`. `M.mk` would silently rename a
clash to `<name>M014`, so avoid them all.

**Proposed names** (a grep of `art/blender` for each found none):

| Object | Part |
| --- | --- |
| `StarstoneNode` | hero (R04 owns `Starstone`) |
| `StarstoneShellLeft` | Left Rock Shell |
| `StarstoneShellRight` | Right Rock Shell |
| `StarlightCore` | Starlight Core (R04 owns `StarstoneStarlightCore`) |
| `StarstoneFootRock` | Base Rocks (one reusable rock; R04 owns `StarstoneBaseRock`) |

- Palette keys `m014_*` (§5.5; none in use). Collection `Kit/M014 Starstone`. Record the reason for each rename in the
  spec, as M011–M013 did.

## 8. Pitfalls to avoid

1. **A crystal prism or a gem ball.** The core is a skewed hexagonal gem: short slanted cap with an off-centre apex
   and a long ridge, broad belt, long taper to a blunt point; W : H 0.60–0.63; 22–30 broad facets.
2. **An upright, centred crystal.** It leans 12° left and 13° back, sits right of centre (X ≈ +1.0) and forward
   (Y ≈ −1.5), its top at about 0.75 H, below both shells' peaks.
3. **The right shell reaching forward.** It falls to the right and back; the side view's front slope is the crystal.
4. **Two similar shells.** The left one is a tall, chunky diamond-section block (4.5 × 2.6 × 6.7); the right one a
   long thick slab (7.3 × 3.3 × 2.3) at 55°. The right one is the model's top.
5. **A gap or rim round the crystal.** The junction is tight: overlap 0.05–0.15 into the shells and union. No
   fillet, no collar.
6. **Missing back rock.** The rear view is dominated by a big back rock to 0.55 H; without it the rear reads as two
   bare shells.
7. **Base rocks as noisy pebbles.** They are broad domes with 16–24 facets, copies of one part; 11 of them, none in
   front of the crystal except the low F1.
8. **Colour by facing.** The warm-lit / cool-shade split on the rock is lighting. Paint only position fields: cleft
   (inner, spill), feet, weathering.
9. **Crystal too dark or too white.** Calibrate to the exploded's bands (#7AFBFD → #30C7D2); no near-white facets
   (p99 #D1FEFF); no greenish or blue-violet hue drift (180–188° only).
10. **Neon on the whole crystal**, or emission between 0 and 1 (§6).
11. **Rock too grey or too pink.** Shells' medians #968786–#AF9A90, base rocks #8D7C77–#9C8983; the Base Rock swatch
    (#666262) is the foot tone, not the base rocks' body.
12. **Thin faces.** Chamfer rows on the shells and the cap ridge facets: keep triangles above 5°; split long chamfer
    strips at the stations (M012's lesson).
13. **Comparing the wrong views.** The sheet's f34 is a front view; its "rear three-quarter" is not a rear view
    (§4). Use the extra renders at elevation 13.
14. **Inventing VFX.** No smoke, dust, motes or embers: halo, light and glints only.

## Decisions (main session, 2026-10-28)

- Halo: add a small generic `crystal_halo` kind to `art/blender/lib/vfx.py`, using the existing `glow_soft` texture, for the sheet's "Starlight Glow". Stage 6 adds it in that file's conventions and documents it in `art/vfx/README.md`.
- Names: use the proposed `StarstoneNode`, `StarstoneShellLeft`, `StarstoneShellRight`, `StarlightCore` and `StarstoneFootRock`. The old R04 sheet owns the plain names.

## Correction (main session, 2026-10-28): side-view direction

The kit's side camera (`VIEWS["side"]` = azimuth 90) sits at +X and looks along −X with Z up, so screen right is +Y: the model's BACK (fronts face −Y). Wherever this spec says the side view's right is the front, read it mirrored. Stage 1 should confirm this with a probe render before using side-view numbers. The 3D layout is unaffected.

## Stage 1 — Modelling

Builder `art/blender/kit/mcp/m014.py` (`import importlib, kit_models, m014; importlib.reload(kit_models);
importlib.reload(m014); m014.build()`), collection `Kit/M014 Starstone`, saved in `FlintbornWorldKit.blend`.
Renders in this folder: the kit set (`front34`, `rear34`, `front`, `side`, `rear`, `top`, `underside`) plus the
like-for-like extras `front_sheet` (0, 13), `side_sheet` (−90, 13), `side_right_el13` (90, 13), `rear_sheet`
(180, 13), `top_el75` (0, 75), `exploded`, and one shot per part. `m014.preview()` re-renders only the sheet-angle
set while iterating; `m014.measure()` gives the silhouette numbers below.

### Side-view direction (the correction above, confirmed)

The kit side camera (az 90, at +X) has screen right = +Y = the back. The sheet's side view shows the crystal on the
right, i.e. the front on the right, so it matches our **azimuth −90** (camera at −X, screen right = −Y). The §2 side
table (f 0 = back, f 1 = front) is compared with `side_sheet` (−90, 13); `side_right_el13` is the mirror, for
reference.

### Parts (each its own function; the hero is pasted from the finished part meshes and unioned)

| Part | Function | Construction | Tris | Merged facets | Size (studs) |
| --- | --- | --- | --- | --- | --- |
| `StarlightCore` | `core` | hull of a 2-point apex ridge (apex at −0.45 of the half-width, −X), a 6-point shoulder ring tilted from 0.73 to 0.63 of the length (−X to +X), a 6-point belt ring at 0.42 (same angles, radius 1.0), a 6-point taper ring at 0.11–0.21 (half a step round, offset +X) and a 2-point blunt bottom ridge; coplanar hull triangles merged at 4°, BEAUTY | 38 | 29 | 3.27 × 2.66 × 5.6 |
| `StarstoneShellLeft` | `shell_left` | hull of 4 rings on a 5-corner lopsided diamond (the front ridge a third of the way across: shade face ⅓, lit face ⅔; corners aligned ring to ring, so each side is one broad plane broken at the waist; rings at 0 / 0.13 / 0.45 / 0.75 of the height, scale 0.94 / 1.0 / 0.86 / 0.6) plus a blunt 4-point chisel top; merged at 3.5° | 42 | 24 | 5.24 × 3.23 × 6.7 |
| `StarstoneShellRight` | `shell_right` | two hull lobes of a boxy 8-point chamfered section (broad roof, steep sides, narrow chamfers): lobe A from the blunt lower end to 0.45 of the length, lobe B from 0.37 (its underside raised 0.07–0.08 of the thickness: the broad concave step at 0.4) to the chamfered wedge upper end; ±3° station twists; unioned and cleaned | 112 | 58 | 6.6 × 3.79 × 2.72 |
| `StarstoneFootRock` | `foot_rock` | `K.hull_rock`, rings (0, 0.92, 7) (0.32, 1.0, 7) (0.66, 0.8, 6) (0.89, 0.46, 4) (1.0, 0.12, 1), crown offset (0.16, 0.1); merged at 3° | 46 | 39 | 2.53 × 2.26 × 2.0 |

Placeholder keys (stage 4 calibrates and grades; no emission anywhere, stage 5 decides): the crystal cap (faces above
the tilted shoulder ring) `m014_core_glow`, the belt `m014_core`, the taper (below 0.27 of the length)
`m014_core_deep`; both shells `m014_shell`; the base rocks `m014_foot`. `m014_core_light` is set in `palette()` but
not used yet. `StarlightCore` carries `kit_shading_ok`: the cap / belt / taper split is a material split (the cap is
stage 5's emissive cap), so it correlates with facing (0.65); stage 4 regrades by position.

### Hero layout (`StarstoneNode`, build frame; `m014.placements()` gives every matrix)

| Piece | Placement |
| --- | --- |
| Core | axis bottom (1.6, −2.1, 0.3), scale 1.12, lean 12° to −X and 13° back, twist −20° (apex side to −X / back) |
| Left shell | base (−2.6, 0.0, −0.25), yaw −38°, lean 5° to +X, 3° back |
| Right shell | centre (1.23, 1.0, 4.58); the long axis falls from the upper end along heading 14° (right, a little back) at pitch 40°; roof normal as close to (0.45, −0.7, 0.55) as stays square to the axis (front-right-up) |
| Base rocks (11 copies of the foot rock, sunk 0.3, floor-cut) | F1 (0.0, −3.3) 4.6×3.2×2.1 · F2 (−2.8, −2.6) 2.9×2.5×1.8 m · F3 (−4.9, −1.3) 2.2×2.0×1.6 · F4 (3.2, −2.6) 3.0×2.8×3.0 · F5 (4.6, −1.2) 2.2×2.1×1.9 m · F6 (4.6, −3.2) 1.1×1.0×0.7 · B1 (−1.2, 2.3) 6.0×3.3×4.4 m · B2 (3.4, 2.0) 3.2×3.0×2.8 · B3 (4.7, 3.4) 1.9×1.8×1.8 m · B4 (−4.5, 1.5) 2.0×1.9×1.7 · B5 (−3.6, 3.2) 1.3×1.2×0.8 m (m = mirrored) |

Hero pipeline: paste, `M.union_loose` (exact), `_floor_cut` (the ground cap scan-filled over all boundary loops; see
item 4 below), `_clean_mesh` (ears, pockets, `m011._clean`'s sliver pass with the ground plane locked, forced
slivers), `_finish`, `_polish` (all triangles, corners ≥ 5°, origin at the bottom centre, Angle-Based UVs on Smart-UV
islands at 45°, margin 0.008).

### Why the layout moved from the study's starting table

1. **Right shell.** The study's axis (upper end (−0.2, 0.5, 7.8) to lower end (4.6, 2.6, 0.6), 55°) projects at 56°
   in the front view, but the sheet's front shows the shell's top edge at 25–30° with a steep right end, and the side
   view a ~60° back flank. A slab whose axis falls gently to the right and a little back (pitch 30–40°, heading
   14–22°) gives both, with its broad roof facing front-right-up (the front view's big face, the top view's roof) and
   its width running steeply from front-down to back-up. First tries read as a round log lying across the cleft (an
   8-point section of equal chamfers, 3.3 × 2.4) and its lower end hung in the air over the back rocks. The section
   is boxier now (3.7 × 2.6); the length is 6.6 (7.3 ran past the sheet's X −1.3 … +4.6); the lower end is a blunt
   square cut resting on B2 and F4.
2. **Left shell.** A 7-point footprint drawn in to a point made a smooth cone or menhir; it is now a 5-corner lopsided
   diamond with aligned rings (broad planes) and a blunt chisel. Yaw −18° left the side view a thin spire; yaw −46°
   (the top view's back-left to front-right diagonal) opened a gap between the shell and the crystal in the front
   view; −38° keeps the crystal flush against the shell with reasonable side and top views. It is 5.2 × 3.4 (the
   study's 4.5 × 2.6 read too slender in the front and side views).
3. **Base rocks.** The study's sizes left 7 loose shells (rocks not touching), and its small rocks, taller than wide,
   read as spikes with the first ring set (a 0.30 / 3-point crown under a point apex). The crown is blunter now, the
   small rocks squat, everything a little wider so neighbours overlap. B1 is 6.0 wide (the rear view's 0.35–0.89 of
   W) and 3.3 deep (deeper pushed the side view's back slope up).
4. **Floor cut.** `m004.floor_cut`'s `holes_fill` gave an enclosed ground pocket (rocks and the left shell ringing an
   uncovered spot near (−3.2, 1.2)) its own cap over the outer cap: 8 crossing face pairs. `_floor_cut` scan-fills all
   boundary loops at once (`bmesh.ops.triangle_fill`), so the pocket stays a hole in the cap: 0 crossings.

### Measured (stage 1 final)

| Object | Tris | Size (studs) | Shells | Non-manifold / boundary / wire / loose | Self-crossing pairs | Min corner |
| --- | --- | --- | --- | --- | --- | --- |
| `StarstoneNode` | 1050 / 4000 | 11.61 × 9.19 × 7.90 (target 11.8 ± 0.5 × 9.0 ± 0.6 × 7.8 ± 0.3) | 1 | 0 / 0 / 0 / 0 | 0 | 5.01° |
| `StarlightCore` | 38 / 1000 | 3.27 × 2.66 × 5.6 | 1 | 0 / 0 / 0 / 0 | 0 | 10.4° |
| `StarstoneShellLeft` | 42 / 1000 | 5.24 × 3.23 × 6.7 | 1 | 0 / 0 / 0 / 0 | 0 | 10.9° |
| `StarstoneShellRight` | 112 / 1000 | 6.6 × 3.79 × 2.72 | 1 | 0 / 0 / 0 / 0 | 0 | 5.03° |
| `StarstoneFootRock` | 46 / 1000 | 2.53 × 2.26 × 2.0 | 1 | 0 / 0 / 0 / 0 | 0 | 16.4° |

All five: 0 n-gons, 0 zero-area faces, 0 duplicate verts, normals outward, origin at the bottom centre, transforms
applied, UV layer `UVMap`; `K.check` reports no problems. The crystal reaches 0.07 into the left shell and up to 0.8
into the right shell's underside (the cap's back corner tucked under the overhang); both junctions are union creases
with no gap.

**Silhouettes** (`m014.measure()`: orthographic z-buffered rasters of the hero at the sheet's angles, the crystal by
material key; the f 0 and f 1 columns read 0 because they sample the bbox's edge pixel, so ignore them):

| View | W : H (sheet) | Crystal share (sheet) | Crystal W span (sheet) | Crystal H span (sheet) | Profile error, mean / max |
| --- | --- | --- | --- | --- | --- |
| Front (0, 13) | 1.30 (1.41) | 15.2 % (16.0) | 0.45–0.73 (0.43–0.74) | 0.20–0.70 (0.18–0.75) | 0.070 / 0.23 |
| Side (−90, 13) | 1.02 (1.03) | 10.2 % (8.5) | 0.56–0.80 (0.57–0.84) | 0.27–0.74 (0.21–0.80) | 0.080 / 0.27 |
| Rear (180, 13) | 1.36 (1.32) | 0.4 % (0) | — | — | 0.085 / 0.35 |
| Top (0, 75) | 1.30 (1.00) | 9.9 % (17.9) | 0.45–0.73 (0.31–0.74) | 0.27–0.59 (0.26–0.77) | — |

Profiles (f 0.05 … 0.95): front .27 .34 .34 .56 .72 .82 .80 .85 .96 .99 .96 .93 .88 .83 .79 .73 .67 .62 .37;
side .44 .49 .68 .77 .86 .92 .96 1.0 .98 .93 .88 .81 .73 .69 .65 .52 .47 .36 .30;
rear .35 .55 .61 .67 .75 .80 .86 .91 .96 .99 .93 .85 .83 .84 .70 .51 .27 .31 .30.

### View by view

- **Front and front three-quarter (the sheet's f34 is the front):** the left shell is a lopsided pyramid peaking at
  f 0.30 (0.82), with a valley at 0.35; the right shell peaks at f 0.5 (1.0) and its edge falls right to a steep end
  at f 0.9. The crystal sits in the V flush against the left shell, its top under the right shell's lower edge, its
  foot behind F1, with F4 covering its lower right. Within tolerance (profile mean 0.07). Weak: the left flank at
  f 0.10–0.15 sits 0.04–0.23 low, and the crystal reads rounder than the sheet's (a less distinct flat cap face and
  long cap ridge).
- **Side (−90):** one peaked mass with the crystal on the front (right) side above F4. The back slope at f 0.05–0.15
  is 0.2–0.3 high (the right shell's lower end and B1 / B2 reach further back or higher than the sheet's). Crystal
  share 10.2 % against 8.5 (within 3 points). The left shell reads as a tall spire in front of the right shell rather
  than one broad pyramid.
- **Rear:** the right shell's peak at the centre with its back face falling to screen left, the left shell's peak at
  f 0.70, the big B1 dome centre-right, the crystal hidden (0.4 %). Matches the sheet's rear.
- **Top:** arranged as on the sheet (crystal centre-front, left shell front-left on a diagonal, right shell
  back-right, tall F4 front-right, small rocks round the back-left and right). Its crystal is smaller than the
  sheet's top view shows (§4.3: that view governs arrangement only).
- **Rear three-quarter (kit 152, 12):** the crystal shows at most as a sliver, as §4.4 asks.
- **Exploded and parts:** the left shell lifted to the left, the core lifted out of the cleft, the right shell lifted
  to the right, the 11-rock ring in place, as in the sheet's exploded layout.

### Left for later stages

- Stage 2: the hero is already one shell with 0 non-manifold edges, 0 self-crossings and corners ≥ 5°. Check UV
  stretch and overlaps (`_polish` cut 4 faces free on the hero, 2 on the right shell).
- Stage 4: all colour is placeholder. The crystal's cap / belt / taper are real geometric regions to grade from;
  spill and inner fields per §5.6 (the dark inner strip above the crystal is the right shell's front-lower chamfer
  row).
- Stages 5 and 6: no emission and no sockets yet (the cap region is `m014_core_glow`).
- Possible stage 1 follow-ups if the verifier asks: a more distinct slanted cap face on the crystal (front view), a
  broader near mass in the side view, and a lower back slope in the side view.

## Stage 2+3 — Cleanup and UV

All changes are in `m014.py`. I rebuilt the model with `m014.build()` in the open `FlintbornWorldKit.blend` and saved it
through the MCP. Every number below was re-measured through the MCP after the final build: `M.audit`,
`m012._thin`, `m014._self_hits`, `M.uv_stats`, and a ray-parity interior-face test (a face is interior when a point
2e-3 off its centre along its normal lies inside the solid on 2 of 3 ray directions).

**Stage 2: no geometry change was needed.** Stage 1's passes already met every 2c check on all five objects:
`union_loose`, `_floor_cut`, `_clean_mesh` (`_dissolve_ears`, `_drop_inner`, `m011._clean`, `_force_slivers`),
`_finish` and `_polish` (all triangles, corners ≥ 5°, origin at the bottom centre). The final meshes match the saved
stage-1 meshes vertex for vertex: the parts are exact, the hero is within 0.0014. The silhouette numbers are
unchanged (front / side / rear profile error 0.070 / 0.080 / 0.085; crystal share 15.2 / 10.2 / 0.4 / 9.9 %), and
the renders are pixel-identical to stage 1's. All tris are well under budget, so no reduction was made.

**The crystal's embed into the right shell was measured and left as it is.**
- The stage-1 figure of "~0.8" understates the overlap. The crystal's cap passes through the slab's front-lower edge:
  - the apex sits 0.66 inside and the back shoulder vertex 0.82 inside, by distance to the nearest surface;
  - the slab's front-lower edge verts reach up to 0.25 into the crystal.
- Moving one piece does not clear it cheaply. I tested the slab along its roof normal, along +Z and along +Y, and the
  core along −Z and along −roof:
  - Nothing below about 1.0 stud brings the embed under 0.15.
  - The best direction is off the slab's underside, (0.41, 0.51, 0.76): 0.9 gives 0.21 and 1.1 gives 0.04.
  - Along +Z it takes 1.8 to reach 0.07. Along +Y, 1.1 gives 0.11.
- I built the best candidate (the slab moved (0.41, 0.51, 0.76), embed 0.12) and measured it:

  | Measure | Stage 1 (kept) | Slab moved (rejected) |
  | --- | --- | --- |
  | Hero height | 7.90 (target 7.8 ± 0.3) | 8.66 (out of tolerance) |
  | Profile error front / side / rear (mean) | 0.070 / 0.080 / 0.085 | 0.099 / 0.121 / 0.131 |
  | Front W : H (sheet 1.41) | 1.30 | 1.19 |
  | Rear crystal share (sheet 0) | 0.4 % | 4.0 % |

- That is a visible silhouette change, so the tuck stays a union crease: 0 self-crossings, 0 interior faces and
  0 non-manifold edges.
- The reasoning is recorded in a comment above `RS_AT`. The left-shell contact is 0.07 and unchanged.

**Stage 3 changes**
- **`UV_ANGLE` and `_uv(o)`, as in M013.** `_finish` and `_polish` now unwrap every object with its own Smart UV island
  angle, still ANGLE_BASED with margin 0.008. `min_angle` equals the angle, so `smart_uv` never falls back to
  smaller islands. Folds are cut free by `m012._uv_unfold`: 4 faces on the hero and 2 on the right shell, the same
  union S-steps as in stage 1.
- **`build()` now returns `uv`** (`M.uv_stats` for all five objects). Any UV overlap or flipped triangle is added to
  `problems`.
- **How each angle was chosen.** I compared 35°, 40°, 45°, 50° and 55° for each object. The rule: lowest worst
  conformal stretch first, then lowest p95, then fewest islands.

  | Object | 35° | 40° | 45° | 50° | 55° | Chosen |
  | --- | --- | --- | --- | --- | --- | --- |
  | Hero (worst / p95, islands) | 1.113 / 1.012, 239 | **1.113 / 1.005, 192** | 1.117 / 1.030, 167 | 1.333 / 1.073, 138 | 1.333 / 1.103, 124 (8 cut) | 40° (stage 1: 45°) |
  | `StarlightCore` | 1.031, 12 | 1.031, 10 | **1.031, 10** | 1.062, 9 | 1.062, 9 | 45° (default) |
  | `StarstoneShellLeft` | 1.000, 9 | 1.000, 9 | 1.000, 8 | **1.000, 7** | 1.057, 6 | 50° |
  | `StarstoneShellRight` | 1.002, 27 | **1.002, 27** | 1.049, 23 | 1.111, 17 (4 cut) | 1.111, 15 | 40° |
  | `StarstoneFootRock` | 1.021, 15 | 1.017, 12 | 1.017, 12 | **1.017, 11** | 1.090, 7 | 50° |

### Measured (MCP, after the final build)

| Object | Tris / budget | Verts | Size (studs) | Shells | Non-manifold | Boundary | Wire | Loose | Zero-area | Dup verts | Quads / n-gons | Self-crossing pairs | Interior faces | Normals | Min corner | Origin offset | Transforms |
| --- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- |
| `StarstoneNode` | 1050 / 4000 | 521 | 11.61 × 9.19 × 7.90 | 1 | 0 | 0 | 0 | 0 | 0 | 0 | 0 / 0 | 0 | 0 | outward | 5.01° | (0, 0, 0) | applied |
| `StarlightCore` | 38 / 1000 | 21 | 3.27 × 2.66 × 5.60 | 1 | 0 | 0 | 0 | 0 | 0 | 0 | 0 / 0 | 0 | 0 | outward | 10.40° | (0, 0, 0) | applied |
| `StarstoneShellLeft` | 42 / 1000 | 23 | 5.24 × 3.23 × 6.70 | 1 | 0 | 0 | 0 | 0 | 0 | 0 | 0 / 0 | 0 | 0 | outward | 10.89° | (0, 0, 0) | applied |
| `StarstoneShellRight` | 112 / 1000 | 58 | 6.60 × 3.79 × 2.72 | 1 | 0 | 0 | 0 | 0 | 0 | 0 | 0 / 0 | 0 | 0 | outward | 5.03° | (0, 0, 0) | applied |
| `StarstoneFootRock` | 46 / 1000 | 25 | 2.53 × 2.26 × 2.00 | 1 | 0 | 0 | 0 | 0 | 0 | 0 | 0 / 0 | 0 | 0 | outward | 16.40° | (0, 0, 0) | applied |

On all five: no custom split normals, no modifiers, no parent, no children, one UV layer (`UVMap`). The hero's
materials are the five `FB_m014_*` placeholder keys in use. There are no orphan M014 meshes or materials:
`_drop_unused` removed the 19 meshes replaced by the rebuild.

| Object (UV, `UVMap`) | Angle | Islands | Overlaps / cross-island | Flipped | Min gap / border | Fill | Density min / med / max | Conformal worst / p95 | Area worst | Worst angle change | Texels / stud at 1024 |
| --- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- |
| `StarstoneNode` | 40° | 192 | 0 / 0 | 0 | 0.016 / 0.008 | 0.332 | 1 / 1 / 1 | 1.113 / 1.005 | 1.060 | 3.19° | 31.3 |
| `StarlightCore` | 45° | 10 | 0 / 0 | 0 | 0.016 / 0.008 | 0.432 | 1 / 1 / 1 | 1.031 / 1.028 | 1.020 | 1.59° | 112.2 |
| `StarstoneShellLeft` | 50° | 7 | 0 / 0 | 0 | 0.0164 / 0.008 | 0.414 | 1 / 1 / 1 | 1.000 / 1.000 | 1.000 | 0.00° | 75.6 |
| `StarstoneShellRight` | 40° | 27 | 0 / 0 | 0 | 0.016 / 0.008 | 0.522 | 1 / 1 / 1 | 1.002 / 1.000 | 1.002 | 0.13° | 83.0 |
| `StarstoneFootRock` | 50° | 11 | 0 / 0 | 0 | 0.016 / 0.008 | 0.457 | 1 / 1 / 1 | 1.017 / 1.000 | 1.011 | 0.83° | 169.0 |

The exporter writes its own palette UVs. This layer is for FBX/OBJ export and any texture work.

### Left for later stages

- Stage 4: unchanged from stage 1's notes. The crystal's apex and back shoulder are buried in the right shell's
  front-lower edge, so only the cap faces in front of the slab's edge show.
- `FlintbornWorldKit.blend` holds a library datablock for `…/scratchpad/kit_pre.blend` that predates this stage. It
  is not M014 data, so I left it alone; the main session may want to remove it.

## Stage 4 — Materials, colour and texture

All changes are in `m014.py`: `palette`, `PALETTE`, `TARGETS`, `calibrate`, `_drop_calib`, `_crystal_spec`; the
stage-4 constants; `_Piece`, `_pieces`, `_trees`, `_classify`, `_tint`, `colour`, `colour_all`, `SHADING_OK`; the
measurement helpers `report`, `regions`, `sheet_stats` (label renders); the colour step in `build()`; and `_raster`
now counts every `m014_core*` key (mix keys too) as crystal. Geometry and UVs are untouched: `colour()` rewrites only
face keys and the Tint layer. After `m014.build()` the audits equal stage 2+3 (hero 1050 tris, 11.61 × 9.19 × 7.90,
one shell, 0 non-manifold / boundary, 0 UV overlaps), `measure()` is unchanged (crystal share 15.2 / 10.2 / 0.4 /
9.9 %), `problems` is empty, and there are no `T_Calib` orphans and no temporary objects or materials.
`FlintbornWorldKit.blend` is saved.

### Keys and calibration

Targets are the sheet's rendered medians (§5.2 / §5.5), not the swatches. Two passes, as M013:

1. **Dome.** `m014.calibrate()` wraps K.calibrate: stone keys are sampled unfiltered (`M.sample(..., "all")`), the
   crystal keys are held at specular 0.35 every round, and the `T_Calib` meshes are purged. Every key rendered within
   4 levels of its target, but the glow and light keys clipped (g / b 255), so those two were not a real fit.
2. **Hero.** `report()` renders the hero at the sheet's angles, plus a flat-emission **label render** of the same
   mesh (cap, crystal, left shell, right shell, base rocks, spill faces), so each region is measured on exactly its
   own pixels. `sheet_stats()` and `regions()` measure the sheet with the §1 masks, and the §5.2 boxes mapped through
   each view's model bbox.
   - Rock: the dome hexes rendered 1.1–1.6× too dark in linear light (front #857775 against #9B8884, top #817674
     against #9F918D, side #8E7E7B against #948383). All six rock keys × (1.38, 1.33, 1.26) per channel in linear:
     the geometric mean of the front, side and top gains (1.34 / 1.32 / 1.32), a little warmer (ours rendered mauve).
   - Crystal: refitted by height band against the sheet's front bands. The cap faces the key light and rendered
     clipped (#7CFFFF), so its key sits well under the belt's. All keys turned to hue 185–189 (b above g; the dome
     keys were 181). The deep key is more saturated, then × 1.15 in linear to split the difference between the hero
     taper and the free (exploded) core.
   - Spill: mixed from the lit body, so the key is a saturated teal; its 25–75 % mixes land on the sheet's teal rock.

| Key | Target (sheet as rendered) | Dome result | **Final hex** | Roughness | Where |
| --- | --- | --- | --- | --- | --- |
| `m014_core_glow` | #7AFBFD (the f34 cap renders #58F1FA) | #5EF7FB (clipped) | **#47B2C6** | 0.3 | the cap only (stage 5's Neon cap) |
| `m014_core_light` | #6EFBFD | #55F7FB (clipped) | **#4ADCF0** | 0.28 | upper belt, just under the cap |
| `m014_core` | #53F4F6 / hero #47E3EC | #42BEC8 | **#40D2E6** | 0.28 | the belt |
| `m014_core_deep` | #30C7D2 / hero lower #22B4C4 | #259BAD | **#16B7D4** | 0.28 | taper, bottom tip, rock contact |
| `m014_shell` | #A5948F | #7A7174 | **#8E8181** | 0.9 | both shells' bodies |
| `m014_shell_cool` | #8A8388 | #67656E | **#78747B** | 0.9 | broad cool weathering |
| `m014_shell_inner` | #66646A | #4C4D56 | **#595860** | 0.9 | right-shell overhang, left-shell contact strip |
| `m014_spill` | #69828D | #4E6472 | **#4A7C90** | 0.9 | rock within 0.45 of the crystal (25–75 % mixes only) |
| `m014_foot` | #93827D | #6D6466 | **#7F7272** | 0.92 | the 11 base rocks |
| `m014_foot_dark` | #6A605E | #4F4A4C | **#5C5555** | 0.92 | floor cap and flat bottoms, contact rows, crevices, shell feet |

- Crystal keys, mix keys included (`_crystal_spec`): Specular IOR Level 0.35, metal 0. Rock: default specular, metal 0.
- The hero uses 33 keys: the 10 above (cool, inner and spill only inside mixes) plus the `K.mix_key` 25 / 50 / 75 %
  in-betweens. The core part uses 10, the left shell 8, the right shell 11, the foot rock 4.

### Method (position fields only, never facing)

`colour_all()` colours the hero first (the BVHs come from its placeholder keys), then each part.
- A face's region is its key family (`m014_core*`, `m014_shell*`, `m014_foot*`). Its piece is the nearest placed
  piece of that region by box norm.
- A part's faces are mapped into the hero frame through their placement, so **part and hero carry the same colour on
  the same face**. The foot rock part is reused 11 times, so it gets the intrinsic terms only (crown, contact,
  bottom), with no neighbour or spill terms.

**Crystal** (in the core's part frame):
- The cap stays `core_glow`: a material boundary on the real shoulder edge.
- Elsewhere u = height fraction + 0.12 × position towards the apex side (−X) + 0.08 × broad noise. One 9-step ladder:
  deep → core over u 0.15–0.40, core → light over 0.48–0.66, so neighbouring facets differ by a step.
- Contact: within 0.15 of the hero's rock surface, no lighter than 50 % deep; within 0.3, no lighter than core.

**Shells** (hero frame; d = distance to the hero's visible crystal surface):
- Spill: d < 0.15 / 0.3 / 0.45 → 75 / 50 / 25 % `spill`, mixed from `shell_inner` where the face is at least 50 %
  inner, else from `shell`.
- Inner, right shell: the faces that hang over the crystal, in the slab's own frame (the front side above 0.8 and
  below 0.9 of its height, i.e. the front-lower chamfer row; or the underside below 0.35), by d < 1.0 / 1.6 / 2.0 →
  75 / 50 / 25 %. Round 1 used the slab's lower half by height only and missed the chamfer row.
- Inner, left shell: only its contact strip (d < 0.3 → 50 %). On the sheet its lit face stays light beige right up
  to the crystal.
- Feet: hero z < 0.6 → 50 %, < 1.3 → 25 % `foot_dark`.
- Elsewhere: broad weathering `shell` ↔ `shell_cool` (noise scale 0.2, level 0.3, width 0.5, capped at 75 %).

**Base rocks** (each rock's own frame, plus the hero frame):
- Spill as above, mixed from `foot`.
- Crevices (within 0.15 / 0.3 of another placed piece): 50 / 25 % `foot_dark`.
- Crown (above 0.7 of the rock's height): 25 % towards `shell`. Contact row (below 0.3): 25 % `foot_dark`.

**Underside:** the hero's floor cap and every part's flat bottom are `foot_dark` (the Base Rock swatch tone).

**Tint:** a per-piece level (shells 1.02 / 0.98, rocks 0.97–1.03) × broad mottling.
- Rock: amp 0.05, scale 0.45, ±1.5 % jitter, in the hero frame (shells) or each rock's own frame.
- Crystal: amp 0.02, scale 0.9, no jitter, in the core's frame.
- Hero Tint 0.92–1.10 (sd 0.033); core 0.99–1.01. Calm patches, no confetti.

**K.check:** no problems.
- The crystal scores 0. `StarlightCore`'s stage-1 placeholder waiver is removed.
- The rock trips the facing test only through position regions, waived in `SHADING_OK` with the reasons:
  - the foot-tone underside: hero 0.77 (0.28 with the floor cap at the body tone);
  - the parts' flat bottoms and feet: left shell 0.89, foot rock 0.92;
  - the right shell's overhang underside: 0.79.

### Target against got

Sheet → ours, as median / lit quartile / shade quartile. Ours come from `report()` and `regions()`, label-masked, on
the final build.

| Region | Sheet | Ours |
| --- | --- | --- |
| Crystal, front (ours az 0, el 13) | #47E2EC / #95FCFE / #1A8D9E | #46ECF9 / #52FFFF / #2BBFCE |
| Crystal, f34 cap | #58F1FA / #AAFDFE / #4D8EA0 | #56ECFA / #5AFFFF / #55D4E4 |
| Crystal, f34 belt | #4AE8EE / #7CFBFE / #1DA5B6 | #41E3EF / #50FFFF / #2FBECD |
| Crystal, f34 taper | #22B4C4 / #7CFAFD / #0F8397 | #27BBCE / #40E0ED / #1FB1C3 |
| Crystal, side (az −90) | #73F8FB / #ABFDFD / #39D3D9 | #4DE0EB / #5CFFFF / #2B8A95 |
| Crystal, top (el 75) | #62E8F1 / #91FCFE / #158D9E | #52D5E5 / #60EEFE / #48BDD0 |
| Crystal, exploded | #47E8F0 / #78FCFE / #30C7D3 | #45D9E9 / #61FFFF / #27B2C5 |
| Rock, all, front | #9B8884 / #D2BEB3 / #645D5F | #9C8982 / #B8A19A / #796A67 |
| Rock, all, side | #948383 / #CDB8AB / #675F61 | #A5918A / #B49E96 / #6A5D5A |
| Rock, all, rear (fill only; not fitted) | #938481 / #C1ABA1 / #6B6262 | #837574 / #958786 / #5E5452 |
| Rock, all, top | #9F918D / #D4C8BF / #696161 | #998782 / #B8A29B / #827471 |
| Shells, front | #AF9A90 | #9C8B85 |
| Base rocks, front | #93827E | #9A8680 |
| Shell, side | #AA9A97 | #AE9992 |
| Base rocks, side | #8D7C77 | #9F8A84 |
| Shells / base rocks, rear | #968786 / #91817C | #8B7D7C / #776B69 |
| Base rock, f34 front centre | #9C8983 | #937F79 |
| Left shell, f34 lit face | #C3AFA6 | #B9A29B |
| Teal spill (sheet: rock within 5 px of the crystal; ours: spill-key faces) | #79858E (spec: #69828D) | #7D8D99 |
| Underside | #6A5F5D | #302B29 (unlit; see below) |

- Crystal bands, front view, top fifth first: sheet #54CEE3 #5CF1FA #59F1F9 #32C9D6 #1CAEBE; ours #5DE8F7 #56EDFB
  #46EEFB #3DD5E3 #27BBCE.
- Exploded core bands: sheet #75FBFD #6AFBFD #4EE9ED #3BDAE1 #30C7D2; ours #5EEBFB #60ECFB #4DEDFA #2EBACC #20B1C4.
- Crystal hue p5 / p50 / p95: 180 / 184 / 187 in the front and side, 180 / 186 / 188 in the top. All inside 180–188.
- No white facets: p99 #5BFFFF. Only 0.55 % of the front view's crystal pixels have every channel above 200 (the
  cap-ridge glint).
- Darkest tenth / lightest tenth of the crystal's brightness: 0.71 front (sheet 0.70), 0.78 top, 0.54 side (its
  shade side).

### What is left, and why

- **Lighting differences, not paint.** The sheet's key light comes from the front-right: the left shell's left face is
  in shade and the right shell's roof is lit. The kit studio's comes from the front-left. So, face by face:
  - the sheet's left-shell shade face (#77727A) is lit in ours (#B09B93);
  - the right-shell roof (#CFBCB2) is in shade in ours (#8B7A75);
  - the rock right of the crystal (#B09A90) is darker in ours (#7D7272).

  The per-view medians match. The lit quartiles stay below the sheet's (#B8A19A against #D2BEB3) because the sheet's
  light is harder.
- **The dark inner strip above the crystal is geometry.** The f34 box (240,150,300,200) lands on the right shell's
  roof in our front view (#9B8882 against #616068).
  - The crystal's cap tucks through the slab's front-lower edge (stage 2), so most of the chamfer row the sheet shows
    as a dark strip is hidden. The overhang faces that do show (front-left of the crystal's top) are 75 % inner.
  - Painting the open roof dark would fake a shadow, so it is left for stage 1 or the verifier if wanted.
- **Side and shade-side crystal** render darker than the sheet's: side #4DE0EB against #73F8FB, shade #2B8A95
  against #39D3D9. The sheet's crystal reads self-lit; stage 5's Neon cap and `crystal_glow` light carry that in
  Roblox.
- **Underside** renders near black (#302B29). The kit studio has no light from below (the placeholder body tone
  rendered dark brown too), while the sheet's underside view is lit. The floor is never seen in game.
- **Rear** rock renders 15–25 levels darker, because only the fill light reaches it (as M013's).

### Notes for stages 5 and 6

- `m014_core_glow` is only the cap (18 hero faces, 8 on the core part), separate from every belt and taper key, so it
  can take emission ≥ 1.0 on its own.
  - Its hex (#47B2C6) is calibrated **lit and non-emissive**. A Neon part shows the key's hex unlit, so stage 5
    should set the Neon cap's hex to the sheet's cap colour (#7AFBFD–#8EFCFE, spec §6), as M009's Neon keys use the
    sheet's colours, rather than keep #47B2C6.
  - `set_colour` never clears an emission, and flintkit builds emissive keys without the Tint node (see M009's
    `_restyle`).
- `_crystal_spec()` sets Specular 0.35 on every `FB_m014_core*` material. Run it (or `palette()`) after adding new
  crystal keys.
- The spill on the rock is painted (25–75 % mixes within 0.45 of the crystal). The `crystal_glow` light will add to
  it in Roblox, so re-measure the spill with `vfx=True`.

## Stage 5+6 — Lighting and VFX

All changes are in `m014.py`:
- lighting: `NEON`, `CAP_NEON`, `NEON_FACETS`, `NEON_TOL`, `palette`, `_restyle`, `_neon`, `_glow_mats`,
  `_neon_face` and the cap branch of `colour()`;
- VFX: `CRYSTAL_LIGHT`, `HALO_POS`, `GLINTS`, `GLINT_REACH`, `GLINT_PAD`, `GLINT`, `_glint_boxes`, `_vfx` and the
  `_vfx(h)` call in `build()`;
- renders: `_views` and the `front34_halo` shot.

Outside it:
- the new generic kind `crystal_halo` in `art/blender/lib/vfx.py`, documented in `art/vfx/README.md` (kinds table, and
  `glow_soft`'s "used by");
- a `crystal_glow` / `crystal_halo` row in `art/blender/kit/BUILDER_GUIDE.md`;
- `art/vfx/vfx_catalog.json` regenerated (`FX_ONLY=catalog ./art/blender/run.sh scripts/build_08_vfx.py
  art/vfx/vfx_catalog.json`); the diff is the new kind only.

Geometry, UVs and the rock keys are untouched. After `m014.build()` the audits equal stage 4's (hero 1050 tris,
11.61 × 9.19 × 7.90, one shell, 0 non-manifold / boundary edges, 0 UV overlaps / flips) and `problems` is empty.
`FlintbornWorldKit.blend` is saved.

### Stage 5 — Lighting

**Neon: two cap facets, not the whole cap.**
- Round 1 made the whole cap Neon (`m014_core_glow`: 18 hero faces, 8 facets on the core part) at `#7AFBFD`. It read
  as one flat, unlit lid, a light bulb on top:
  - in the top view (el 75) the crystal's top was one `#7BFFFF` blob with no facet edges, where the sheet's top
    shows facets from `#158D9E` to `#91FCFE`;
  - the core part's whole cap was one flat pale shape.
- So, as §6 allows, only the cap's largest visible facets glow (`NEON_FACETS`). They are matched by normal in the core
  part's frame, within `NEON_TOL` (4°), so the part and the hero glow on the same facets:
  - part normal (0.75, 0.13, 0.65): the hero's largest visible cap facet (area 1.37, facing right and up);
  - part normal (0, −0.82, 0.57): the third largest (0.71, plus a 0.41 piece split off by the union, facing front-left
    and up). Its near-coplanar neighbour (3.6°, hero area 0.14) glows with it.
  - The two don't touch: the front-up facet between them (1.17) stays lit, so the cap's main ridge still reads.
  - "Largest" is measured on the hero. The part's own largest facets face back-right and back, under the right shell.
  - Every other cap face takes stage 4's crystal ladder: light at the top, and no lighter than core within 0.3 of
    the rock.
- Result: 5 Neon faces on the hero (2.64 studs²) and 3 on the core part (3.11). In the top view, pale Neon facets
  alternate with lit ones. In the f34 and front views the cap reads as the crystal's palest facets, not a separate
  lamp.
- `CAP_NEON` is `#7AFBFD`, the sheet's cap colour (the exploded core's top band). It is the low end of §6's range
  (#7AFBFD to #8EFCFE), so it doesn't bloom white. It renders `#7BFFFF` unlit.
  - Stage 4's lit fit `#47B2C6` is kept in the comments.
  - `calibrate()` now skips the Neon key.
- Emission `NEON` is 1.0, the exporter's `GLOW_EMISSION`.
  - `_restyle` rebuilds the key's material: flintkit makes emissive keys without the Tint node, and `set_colour`
    never clears an emission.
  - `_glow_mats` previews it unshaded (base colour black, specular 0), so the render shows the hex as Roblox's Neon
    does.
  - `_crystal_spec()` skips it.

**Light: `crystal_glow` socket (PointLight).**

| Setting | Value |
| --- | --- |
| Build frame | (0.9, −4.6, 4.0); hero-local (1.046, −4.361, 4.0) |
| Colour | `#6EF2F8` |
| Brightness | 0.7 |
| Range | 12 |
| Shadows | true |
| Flicker / pulse | none |
| Clearance (BVH on the hero) | 1.80 studs from the nearest surface (the belt), outside the solid; 1.88 for the preview light (+0.25 z) |

§6's point (0.9, −3.6, 3.6) at brightness 1.0 was not used. It is only 0.72 from the belt (0.80 for the preview
light). The table compares the options, measured with `vfx=True` (`report()`, light only, label-masked). Bands are
the front view's crystal, top fifth first.

| Light | Bands (front) | Shade quartile | Spill median (front) | Foot / left shell (front) |
| --- | --- | --- | --- | --- |
| none | #7AFFFF #58FFFF #46EEFB #3DD5E3 #27BBCE | #2CBFCE | #7C8D99 | #99857F / #B8A19A |
| (0.9, −3.8, 3.6), 0.91 clear, brightness 1.0 | #7BFFFF #5BFFFF #54FFFF #40FFFF #28D6EE | #2DE9FF | #81919C | #9B8A84 / #B9A49D |
| same point, brightness 0.6 | #7BFFFF #5BFFFF #51FFFF #3EF1FF #27CAE1 | #2CDBF1 | #7F8E9B | #9B8882 / #B9A39C |
| **(0.9, −4.6, 4.0), 1.80 clear, brightness 0.7 (chosen)** | #7AFFFF #59FFFF #4BFFFF #3EEDFE #27CAE1 | #2CD8EE | **#7E8E9B** | **#9B8A84 / #B9A59D** |
| sheet | #54CEE3 #5CF1FA #59F1F9 #32C9D6 #1CAEBE | #1A8D9E | #79858E (§5.2: #69828D) | #93827E / – |

- Close in, the light made a hot patch on the belt facets that face it (M012's lesson). From 1.8 studs out it spreads
  evenly. Any teal light lifts the crystal's g and b, so it stays soft.
- With the chosen light on:
  - the spill moves 1–5 levels: front #7C8D99 → #7E8E9B, f34 #798D96 → #7B8F9B, side #6F8788 → #6F8C8E, top
    #7E898E → #7F8C97;
  - the rock moves 0–6 levels: all rock, front #9C8982 → #9D8E88, f34 #AB9590 → #AC9993, top #998782 → #998985;
  - the rear is unchanged, because the shells shadow it;
  - there is no visible pool on the ground in front.
- The side and shade-side crystal stay darker than the sheet's (side #47E0EC against #73F8FB), because the light is
  in front. In Roblox the Neon facets, bloom and the halo carry the "self-lit" read. No second light behind was
  added: the sheet's rock shows no spill at the back.

**Studio notes.**
- The glow assumes the place's default Bloom. Without bloom the Neon facets still read pale cyan, and the halo carries
  the rest.
- `#7AFBFD` is a bright Neon. Check in Studio that the two facets don't bloom to white; if they do, step `CAP_NEON`
  down towards `#6EF2F8` (the light's colour).
- Neon pieces get no collision (the exporter's `NO_COLLIDE`). The cap is 4.3–5.7 studs up, inside the hull
  collision.
- The light's range scales with the placed model (`vfx_scale`).

### Stage 6 — VFX

**New generic kind `crystal_halo`** (`vfx.KINDS`, after `crystal_glow`). It has emitters only (light None): one "Halo"
emitter.

| Key | Value |
| --- | --- |
| Texture | `glow_soft` (already exists) |
| Colour | `#C5F0ED` → `#6EF2F8` |
| Size | 12 → 14 |
| Transparency | 1.0 → 0.82 → 1.0 |
| Lifetime | 2–3 |
| Rate | 0.8 |
| Speed, spread | 0, 0 |
| Light emission | 1.0 |

- The defaults are this sheet's "Starlight Glow", as `crystal_glow`'s defaults are M011's violet. Other crystals
  override the emitter colour, and size the halo with `vfx_scale`.
- §6 asked for transparency [0.82, 1.0]. A particle born at 0.82 pops in, so the sequence starts and ends at 1.0 and
  the ~2 overlapping particles fade in and out.
- Usage notes are in the kind's comment and in the README's kinds table.

**Sockets.** All are on `StarstoneNode`; the parts carry none.

| Socket | Kind | Build frame | Hero-local | Where | Settings |
| --- | --- | --- | --- | --- | --- |
| `VFX_StarstoneNode_crystal_glow_1` | crystal_glow | (0.9, −4.6, 4.0) | (1.046, −4.361, 4.0) | in the open, 1.8 in front of the belt, above F1 | the light above |
| `VFX_StarstoneNode_crystal_halo_1` | crystal_halo | (0.6, −0.6, 4.2) | (0.746, −0.361, 4.2) | behind the crystal's centre, 0.86 inside the rock | kind defaults; 12–14 studs ≈ 1.0–1.2 × the model's width |
| `VFX_StarstoneNode_ore_glint_1` | ore_glint | (0.674, −1.368, 5.359) | (0.82, −1.129, 5.359) | the cap's main ridge, a quarter of the way down from the slab crease | rate 0.5; size 0 → 0.6 → 0; box 0.58 × 0.41 × 0.36 (Roblox x, y, z) |
| `VFX_StarstoneNode_ore_glint_2` | ore_glint | (2.093, −1.598, 4.434) | (2.239, −1.359, 4.434) | the right shoulder ridge (cap to belt) | rate 0.35; size 0 → 0.45 → 0; box 0.15 × 0.17 × 0.72 |
| `VFX_StarstoneNode_ore_glint_3` | ore_glint | (−0.609, −2.086, 3.306) | (−0.463, −1.847, 3.306) | the left belt ridge (between light facets) | rate 0.25; size 0 → 0.45 → 0; box 0.19 × 0.69 × 0.28 |

- **Glint emitter** (`GLINT`): `spark_diamond`, colour `#F2FFFF` → `#8CF8FD`, transparency 0.1 → 1, lifetime
  0.5–0.8, speed 0, spread 0, light emission 1, rotation 0–90. That is about 1.1 twinkles a second in all, so under
  one is on screen at a time.
- **Fitting** (`_glint_boxes`, run on the finished hero, so the boxes follow the final mesh):
  - Each glint is a ridge (an edge between two crystal faces) and a point along it. The ridge's ends snap to the
    nearest hero crystal vertices.
  - The box spans `GLINT_REACH` (0.3 stud) either side of the point along the ridge, padded by `GLINT_PAD` (0.06).
  - Every box centre lies on the crystal surface (BVH distance 0.000). The farthest box corners are 0.35 / 0.13 /
    0.23 stud from the crystal, so nothing spawns in open air away from it. (With a reach of 0.4 the cap box's
    corners were 0.43 off, because the cap ridge runs diagonally to all three axes.)
- **Changes from §6's points:**
  - the cap apex itself (0.45, −0.85, 5.7) is inside the right shell's union crease, so the cap glint sits on the
    visible ridge below it;
  - the shoulder and belt points moved 0.11 and 0.39 onto the nearest real ridges.
- **How they are added:** after `_finish(h)`, with `K.socket(h, kind, build point − h[OFF])`, not through
  `M.mk(fx=...)`, because the glints are fitted to the hero's final mesh. `mk` still clears the old sockets on every
  rebuild.

**Renders.** `render_views` uses `_views`: `M.views(vfx=True)`, with the halo's preview stand-in hidden in every shot
except `front34_halo`.
- The stand-in is a few faceted blobs about 10 studs across, and they veil the whole model. A Roblox billboard behind
  the crystal is depth-tested against the rock and doesn't.
- The compare set shows the light and the glint diamonds. The glints sit on the cap ridge, the shoulder and the belt
  ridge in the front34, front and side views.

**Export** (read from `export_kit_roblox.py`, not run):
- `sockets()` walks `children_recursive` for `vfx_kind`, so the hero's manifest entry carries 5 sockets. Their
  positions are in Roblox axes relative to the hero origin, and their spec JSON includes the overrides.
- Faces whose key has emission ≥ `GLOW_EMISSION` group as `glow:m014_core_glow`. That gives one Neon piece on the
  hero, `StarstoneNode_glow_m014_core_glow` (5 tris, colour `#7AFBFD`, material Neon, no collision), and one on
  `StarlightCore` (3 tris: the reusable core's cap glows on the same facets).
- Expected STATS line: 5 assets, 2 glow pieces, 5 vfx sockets. §6 expected 1 glow piece; the second is the same cap
  on the reusable core part.

### Left for later

- Studio: check the Neon facets against bloom, and the halo's size and opacity, in a lit scene and a night scene.
- Verifier: compare the top and f34 cap with the sheet. With the light on, the lower belt bands are 15–25 levels
  lighter in g and b than the sheet's (see the table).

### Stage 1 fixes (after verifier round 1)

Verifier round 1 scored 6.5/10 (technical checks clean). Its four shape findings, fixed in `m014.py`; stages 2-6's
code (UV angles, palette and colour pass, Neon facets, sockets, halo-hidden views) is kept and re-run by `build()`.

- **B1, the right shell's stair-step (blocking).** Round 1 built the slab from two hull lobes with different
  sections (lobe B narrower, thinner, shifted up, with its own station twists), so the join showed as a step across
  the roof and both sides. Now `shell_right` makes **one body hull** with one section along its whole length
  (`RS_STATIONS`, no twists, one jitter value per station point), so the roof and sides run unbroken. Only the body's
  two bottom section points sit `RS_STEP` (0.12 t, 0.31 stud) higher. A **keel** (the same section's bottom points at
  full depth plus its lower chamfer points 0.012 w inside the body, its top buried) is unioned under the lower part
  up to `RS_KEEL_END` (0.42 of the length), its end 40 % shallower, so the broad concave step is on the underside
  only. The part is 84 tris (was 112), one shell, min corner 5.24°. The rear, top and part renders show no step.
- **B2, the left shell read as a narrow spire.** The upper ring scale is 0.75 (was 0.6), the waist 0.9 (was 0.86),
  the chisel top about twice as wide (`LS_TOP` ±0.3-0.4 of the half-width), and the footprint's left corners pushed
  out (`(-1.25, 0.1)`, `(-0.6, 0.9)`; part 5.9 × 3.23 × 6.7). Front f 0.15 / 0.20 / 0.25: 0.34 / 0.56 / 0.72 →
  **0.56 / 0.75 / 0.85** (sheet 0.57 / 0.71 / 0.83). Rear f 0.85 / 0.90: 0.27 / 0.31 → **0.69 / 0.46** (sheet
  0.62 / 0.44).
- **B3, the side view's high back slope.**
  - **Projection effect:** from az −90 / el 13 a rock far out at +X stands about 2.3 studs higher on screen than one
    at −X (found with a piece-by-piece raster of the silhouette top). So the back-right rock B3, the back-most piece,
    set f 0.03-0.10.
  - **Rocks:** B3 moved forward and down (4.6, 3.3, 1.8 tall → 4.7, 2.4, 1.0; it is still the rear view's right-end
    rock). B2 is 2.0 tall (study 2.2; was 2.8). The small B5 behind B1 at −X is now the back-most rock (−3.2, 3.35,
    1.6 × 1.4 × 0.8, touching B1). B1 is (−1.2, 2.0), 6.0 × 2.9 × 3.9, yaw 190.
  - **Right shell:** turned about its fixed upper end (−1.22, 0.4, 6.7) to pitch 47° (was 40) and heading 6° (was
    14), so its lower end sits about 0.4 lower and 0.6 further forward.
  - **Result:** side f 0.05 / 0.10 / 0.15 / 0.20: 0.44 / 0.49 / 0.68 / 0.79 → **0.14 / 0.41 / 0.50 / 0.75** (sheet
    0.17 / 0.25 / 0.47 / 0.65). f 0.10 stays 0.16 high: that is B1's back flank, which the rear view needs to fill
    the centre-right.
  - **Trap:** a rock that touches nothing is deleted by the cleanup's `_drop_inner` (crumb rule, under 2 % of the
    area). B5 at (−3.3, 3.6) vanished that way; at (−3.2, 3.35) it touches B1.
- **B4, the crystal's cap and egg shape.**
  - **Why twist alone could not fix it:** the old cap was a pointed pyramid whose long ridge fell 40-45° to the far
    shoulder. In the az 0 / el 13 view that ridge stayed 32-120° off level at every twist from −180 to 165.
  - **Cap reshaped:** the second apex-ridge point moved from (−0.1, −0.12, 0.93) to (0.25, −0.08, 0.965) of the core,
    giving a short, near-level ridge along X that falls 10° in the part, so the core's 12° lean brings it level. Its
    drop to the low +X shoulder gives the sheet's step down to the right shoulder.
  - **Placement:** twist −20° → 0° (with the new ridge, every twist from −30 to 20 keeps it within 3° of level; 0
    fitted the sheet's front top edge best). Base (1.6, −2.1, 0.3) → (1.6, −2.1, 0.2).
  - **Result:** the ridge lies **2.4°** off level in the az 0 / el 13 view. The crystal's top edge against the sheet's
    front top edge (f 0.43-0.72): mean error 0.040 (round 1: 0.037 with the steep ridge, which matched the edge's
    outline but not the cap). Crystal height span 0.21-0.77 (sheet 0.18-0.75).
  - **Embed:** the apex (−X end of the ridge) still sits about 0.46 inside the slab's underside, by nearest surface;
    the ridge's +X end is 0.5 clear. Moving the core forward took the apex to 0.40 but raised the side view's crystal
    share to 11.5 % (sheet 8.5); lowering it pushed the apex deeper. Kept.
- **Stage 5 / 6 follow-ups** (the cap and the core's placement changed):
  - **Neon facets:** `NEON_FACETS` re-found the same way stage 5 chose them. By hero area the cap's facets are
    front-up 1.69, front-right 1.64, right 1.51 …; the first and third glow (normals (−0.01, −0.84, 0.55) and
    (0.89, 0.20, 0.42), the same front and right directions as before, meeting only at a corner). The part selects
    2 faces (2 facets) and the hero 3 (the union split one).
  - **Glints:** `GLINTS` ends are now given in the core's construction frame and placed through `_core_matrix()`, so
    they follow the core. Each box centre lies on the crystal surface, and box corners are 0.25-0.40 off it.
  - **Other sockets:** the crystal_glow light is 1.92 clear of every surface and outside the rock; the halo is still
    inside the rock.

**Measured after the fixes** (`m014.build()`, MCP):

| Object | Tris | Size (studs) | Shells | Non-manifold / boundary | Self-crossing pairs | Min corner |
| --- | --- | --- | --- | --- | --- | --- |
| `StarstoneNode` | 958 / 4000 | 11.61 × 8.90 × 7.79 (target 11.8 ± 0.5 × 9.0 ± 0.6 × 7.8 ± 0.3) | 1 | 0 / 0 | 0 | 5.10° |
| `StarlightCore` | 38 | 3.27 × 2.66 × 5.6 | 1 | 0 / 0 | 0 | 10.4° |
| `StarstoneShellLeft` | 40 | 5.9 × 3.23 × 6.7 | 1 | 0 / 0 | 0 | 6.06° |
| `StarstoneShellRight` | 84 | 6.6 × 3.72 × 2.6 | 1 | 0 / 0 | 0 | 5.24° |
| `StarstoneFootRock` | 46 | 2.53 × 2.26 × 2.0 | 1 | 0 / 0 | 0 | 16.4° |

`K.check` is clean, and no object has UV overlaps or flips (worst conformal stretch: hero 1.145).

| View | Profile error mean / max (round 1) | Crystal share (sheet) | Crystal spans W / H (sheet) |
| --- | --- | --- | --- |
| Front (0, 13) | **0.053 / 0.17** (0.070 / 0.23) | 18.2 % (16.0) | 0.43-0.75 / 0.21-0.77 (0.43-0.74 / 0.18-0.75) |
| Side (−90, 13) | **0.056 / 0.16** (0.080 / 0.27) | 10.5 % (8.5) | 0.57-0.79 / 0.26-0.79 (0.57-0.84 / 0.21-0.80) |
| Rear (180, 13) | **0.056 / 0.17** (0.085 / 0.35) | 0 % (0) | — |
| Top (0, 75) | — | 11.2 % (17.9; arrangement only, §4.3) | 0.44-0.75 / 0.29-0.63 |

Profiles (f 0.05 … 0.95):
- front .28 .34 .56 .75 .85 .83 .81 .86 .95 1.0 .96 .92 .86 .79 .72 .66 .58 .33 .28;
- side .14 .41 .50 .75 .87 .92 .98 1.0 .96 .92 .88 .80 .75 .70 .63 .52 .48 .35 .30;
- rear .35 .34 .55 .62 .69 .77 .84 .91 .96 .99 .94 .89 .84 .85 .86 .69 .46 .31 .30.

**Still off:**
- The side view's f 0.10 (B1's back) is 0.16 high and f 0.20 is 0.10 high.
- The rear's f 0.05-0.10 are 0.11-0.17 high (F5 / F6 at the far right).
- The front's far left (f 0.05-0.10, the left rocks) is 0.04 high.
- The hero depth, 8.90, sits inside the 9.0 ± 0.6 band.
- The crystal's apex stays tucked about 0.46 into the slab, a clean union crease.

The scratch probes used for the tuning (a union-free orthographic raster of the placed parts: profiles, crystal
top edge, piece ownership of the silhouette top, apex depth, cap facets) are in the session scratchpad
`m014_s1/m014probe.py`; `m014.measure()` remains the in-repo measure.

## Stage 4 — Fixes after verifier round 1

Findings A1 (crystal), C1 (spill) and C2 (halo socket). Everything was measured on stage 1's reshaped model. All
changes are in `m014.py`; there are no geometry or UV changes.

After `m014.build()` the state is:
- hero 956 tris, 11.61 × 8.90 × 7.79, one shell, 0 non-manifold edges;
- `problems` is empty;
- `measure()` crystal share 18.2 / 10.5 / 0 / 11.2 %, as stage 1's fixes.

`FlintbornWorldKit.blend` was saved through the MCP. The hero builds at 956 tris here, where stage 1's table says
958. I did not touch the geometry code, and two consecutive builds both gave 956.

**What changed**
- **`report(light=True)`.** The hero's sockets are now realised as lights only (the `crystal_glow` PointLight, no
  particle stand-ins) for every measurement, so the fit includes stage 5's light.
- **New report fields:**
  - `spill_share`: spill-key pixels as a share of the crystal's pixels;
  - `shade_lit`: the crystal's 12.5th / 87.5th luminance percentile, which is about the median shade quartile over
    the median lit quartile;
  - `clip`: the share of the solid crystal's pixels with g or b at 254 or more. The Neon cap is excluded, because it
    renders its hex unlit.

**A1: the crystal**
- **`CRYSTAL_LIGHT` brightness 0.7 → 0.45.**
- **Keys refitted with the light on.** I fitted them per ladder group: a label render split the crystal into deep
  (ladder steps 0–2), core (3–5) and light (6–8), each measured on its own pixels.
  - `core_light` **#4ADCF0 → #84B0BA**: pale aqua. Its facets render r 140–150 (median #8FD2D6), and their lit
    quartile reaches g / b 246–255.
  - `core` **#40D2E6 → #34B0C8**: the belt's own median had clipped. The core group now renders #3ED7E6-ish, with
    its lit facets just at the clip.
  - `core_deep` **#16B7D4 → #04889F**: a saturated deep teal, so the front's shade quartile lands near the sheet's.
  - `CRYS_SPEC` 0.35 → 0.25. Specular 0.15 / 0.35 / 0.6 moved the clip share by under 1 point, but each step up
    added a grey sheen: front median r 69 / 80 / 92 against the sheet's 71.
- **The Neon cap facets stay at `CAP_NEON` #7AFBFD**, unchanged.
- **What I tried and dropped:**
  - Light #70B8C8 or #78B2C0 is more saturated, so the light facets are less grey in shade, but the clip share
    rises to 34–36 %.
  - Core #36BCD0 brings the median closer (#51D1E1), but clips 31 %.
- **What limits the fit: the kit studio spreads light more than the sheet's renderer.**
  - On our core facets, lit against median is about 2× in linear light; on the sheet it is about 1.2–1.3×, because
    its highlights are compressed.
  - So the median g / b and the clip share trade against each other. Even the sheet has 17.6 % of its front-view
    crystal pixels at g or b ≥ 254 (f34 16.9 %, top 13.4 %).
  - I picked the setting with the lowest clip share (25 %) that keeps the lit quartile at the sheet's.

| Crystal (light on) | Sheet | Round 1 (verifier) | **Now** |
| --- | --- | --- | --- |
| Front: median / lit / shade | #47E2EC / #97FCFE / #1A8D9E | #4AFFFF / #5CFFFF / #2CCFE5 | **#4AC6D9 / #90F6FF / #2796AA** (solid facets only: #47C4CF / #91F5FF / #1E94A7) |
| Front: shade / lit luminance | 0.51 | 0.79 | **0.57** |
| Front: share clipped (g or b ≥ 254, solid facets) | 17.6 % | 73 % | **25 %** |
| Front bands, top fifth first | #54CEE3 #5CF1FA #59F1F9 #32C9D6 #1CAEBE | #5AFFFF #66FFFF #5CFFFF #41F7FF #32C6DB | **#7BE8FE #90ECF9 #4CEDF8 #34C5D9 #2495A9** |
| f34 boxes: cap / belt / taper | #58F1FA / #4AE8EE / #22B4C4 | – | #7BF2FF (Neon) / #33C7DD / #1A96AA |
| Top: all / solid facets | #61E8F1 | #5AFFFF | #7BEAFD (Neon facets) / **#54C0CD**, clip 28 % (sheet 13 %) |
| Side | #73F8FB | – | #97C9CC (shade / lit 0.57) |
| Front three-quarter (kit az −28) | – | – | #6DCDDB, clip 25 % |
| Exploded core | #47E8F0, bands #75FBFD … #30C7D2 | – | #36ABBE, bands #32C9E0 #7AD9E1 #41C8DB #238797 #138796 |
| Hue p5 / p50 / p95 (solid facets) | 180–188 | – | front 181 / 187 / 189, side 181 / 184 / 188, top 183 / 187 / 188 |

- **Facet read** (`front_sheet.png`, `top_el75.png`): pale aqua facets at the top, saturated cyan in the belt and deep
  teal at the foot, with neighbouring facets a step apart. It no longer reads as one cyan blob.
- **Still off:**
  - Light-key facets that face away from the key light render grey-aqua (#8DC6C7, saturation 0.3). The pale key has
    a high red, and in shade nothing lifts it as the sheet's self-lit crystal is lifted. That is why the side view
    reads #97C9CC.
  - The belt and taper are 20–30 levels darker than the sheet's f34 boxes. That is the cost of not clipping.
  - The free core (exploded and part shots) carries the deeper keys and the contact grading, so it renders darker
    than the sheet's free core (#36ABBE against #47E8F0). The hero's front was fitted first, as the verifier asked.

**C1: the teal spill**
- Spill on the shells now always mixes from `shell_inner`, and on the base rocks from `foot_dark`, so each mix key
  keeps its region's prefix.
- The faces near the crystal are broad, so the spill's share jumps with the band widths. Front view:

  | Bands | Spill share |
  | --- | --- |
  | 0.3 / 0.6 / 0.9 (the suggestion) | 45 % (top view 118 %) |
  | 0.25 / 0.5 / 0.7 | 31 % |
  | **0.2 / 0.4 / 0.6** | **21 %** |
  | 0.18 / 0.35 / 0.52 | 9 % |

- **`SPILL_RAMP` = (0.2 → 75 %, 0.4 → 50 %, 0.6 → 25 %).**

| Spill | Sheet | Round 1 | **Now** |
| --- | --- | --- | --- |
| Front: share of the crystal's pixels | 14 % | 4 % | **21 %** |
| Front: median / lit / shade | #596D75 (§5.2 #69828D; my 5 px mask #79858E) | #7B939A | **#62747C / #738E99 / #535D63** |
| Front three-quarter | – | – | #64767E, 20 % |
| Side | – | – | #61787F, 12 % |
| Top | – | – | #5B6870, 49 % (the top view sees the rock round the crystal from above) |

**C2: the halo socket**
- `vfx.py`'s emitter spec has no ZOffset key. The README's spec → ParticleEmitter table lists none, and
  `export_kit_roblox.sockets()` passes the spec through unchanged, so an override would not be applied in Studio.
  Changing `vfx.py` was out of this stage's M014-only scope, so the socket was moved instead.
- **`HALO_POS` (0.6, −0.6, 4.2) → (0.6, 6.5, 3.4)** in the build frame (hero-local (0.746, 6.884, 3.4)). That is
  behind the model and outside the rock: 3.52 studs from the nearest surface, outside the solid, and 2.4 behind the
  model's back (y 4.1).
- Checked against every hero vertex inside the largest billboard (14 × 14, facing the camera): all of them are in
  front of the billboard's plane:
  - front, el 13: by at least 1.6 studs;
  - front, el 4: by at least 2.2 studs;
  - front three-quarter (az −28, el 12): by at least 0.1 stud.

  So the rock hides the halo's middle and the glow shows round the silhouette, as on the sheet's panel. Seen from
  el 13, its centre sits between the crystal's middle and its top.
- From the rear and from above, any billboard there sits in front of, or over, the rock. This one is a faint
  additive veil (transparency at least 0.82). `front34_halo.png` shows its preview stand-in behind the model.

**The rest is unchanged:**
- Rock: rock all, front #A2918B against the sheet's #9B8884; shells #A69896; base rocks #9B8983.
- `K.check` facing scores: hero 0.73 and the parts 0.36–0.92; the hero and the shell / foot-rock parts are waived in
  `SHADING_OK` as before, and the core passes at 0.36.
- The orphan purge, Tint and the rock keys.

Stage 5's table above still lists brightness 0.7 and the old halo point. The values in force are in `CRYSTAL_LIGHT`
and `HALO_POS`.

### Final crystal fix (after verifier round 2)

Verifier round 2 scored 6.5/10. This narrowly scoped final pass changes only the crystal, its Neon facets and glints,
and the halo; everything else is as before.

- **Crystal silhouette (blocking).** The ring-hull gem (shoulder, belt and taper rings; 29 merged facets) read as an
  egg from the front. `core()` is now a **kite gem**: the convex hull of ten named corners (`CORE_PTS`).
  - **Front corners:** drawn straight from the sheet's front crystal, as fractions of its bbox: top corner T
    (0.15, 1.0), left shoulder L1 (0, 0.88), sharp right shoulder R (0.94, 0.66), right flank R2 (1.0, 0.32), bottom
    point B (0.69, 0), lower left L2 (0.31, 0.05), front corner F (0.31, 0.5).
  - **Back corners:** TB, K and KB give the back its depth.
  - **Faces:** the broad slanted top face T-R-F has its top edge running from upper left down to the right shoulder.
    The long front face F-R-R2-B tapers to the point; the left faces run F-L1-T and F-L1-L2.
  - **Counts:** 15 broad facets, 16 tris (was 29 / 38). Size 3.7 × 2.8 × 5.4.
  - **Placement:** nearly upright, so the front view shows the sheet's proportions: `CORE_AT` base (0.75, −1.9, 0.35),
    lean 0° / 5° back, twist 0, scale 1.08. The crystal touches the left shell, the right shell and F1; its top corner
    is clear of the slab.
  - **Placeholder keys:** faces on T or TB are the cap, faces on B the taper.
- **Junction.** With the kite's straight left side against the left shell's lit face and its top corner out of the
  slab, the cleft above the crystal reads as one dark inner face. The front view no longer shows the jagged dark
  slivers or the dark hole at the crystal's lower left.
- **Neon facets.** The cap facets by hero area:
  - slanted top face F-R-T 4.63;
  - left top face F-L1-T 1.22;
  - back-right K-R-TB 0.73;
  - R-T-TB 0.53;
  - two hidden.

  The broad top face stays lit and grades pale by height (a Neon top face would be a flat lid). The left top face and
  the back-right facet glow, one on each side of the top face, sharing no corner. `NEON_FACETS` = (−0.522, −0.779,
  0.346), (0.567, 0.696, 0.44). The part has **2** glow faces, the hero 3 (the union split one).
- **Glints.** `GLINTS` now names kite corners: the top edge T-R (cap ridge), the front ridge F-R (the sheet's
  brightest ridge) and the left ridge F-L1. Each box centre lies on the crystal surface, and box corners are
  0.34-0.39 off it.
- **Colour check.** By height in the core's frame:
  - deep below 0.2;
  - deep→core 0.2-0.35;
  - core 0.38-0.53;
  - light at 0.6 and on the top face (0.71, the biggest face);
  - the two Neon facets.

  The sheet's pale-aqua → cyan → teal runs top to bottom. A few slivers under 0.2 square studs near the slab junction
  take the contact tone (`CRYS_CONTACT`).
- **Halo.** `HALO_POS` moved from (0.6, 6.5, 3.4), behind the model, where it read as a haze in front of the rock
  from the rear. It is now **(0.9, 0.3, 3.4)**: inside the hero's solid (ray parity) right behind the crystal at its
  mid-height, 0.74 stud from the nearest surface, so the rock hides the billboard's middle from every side. The
  crystal_glow light is 1.81 stud clear and outside the rock.

**Measured** (`m014.build()`, MCP):
- **Hero:** 910 / 4000 tris, 11.61 × 8.90 × 7.79, 1 shell, 0 non-manifold, 0 boundary, 0 self-crossings, min corner
  5.10°.
- **Core:** 16 tris, min corner 15.2°.
- **All objects:** no UV overlaps or flips; `K.check` clean.

| View | Crystal share (sheet) | Crystal spans W / H (sheet) | Profile error mean / max |
| --- | --- | --- | --- |
| Front (0, 13) | **17.0 %** (16.0) | 0.41-0.74 / 0.22-0.74 (0.43-0.74 / 0.18-0.75) | 0.053 / 0.17 |
| Side (−90, 13) | **10.2 %** (8.5) | 0.57-0.81 / 0.24-0.78 (0.57-0.84 / 0.21-0.80) | 0.061 / 0.16 |
| Rear (180, 13) | **0 %** (0) | — | 0.056 / 0.17 |
| Top (0, 75) | **9.1 %** (17.9; arrangement only) | 0.41-0.75 / 0.29-0.60 | — |

**Renders:** `front_sheet`, `front34` and `top` show a kite with a broad, pale, slanted top face, a sharp right
shoulder and long sides to a point, the Neon left facet a bright strip along its upper left. `front34_halo` is the
one shot with the halo's (oversized) preview stand-in.

## Result

- **Verifier round 1:** FAIL, 6.5/10. Blockers: the crystal colour and contrast, and a stair-step in the right shell.
- **Verifier round 2:** FAIL, 6.5/10. Round 1's blockers were fixed. The new blocker was the crystal silhouette, which read as an egg.
- **Final fix, under the 2-round cap:** the crystal was rebuilt as the sheet's kite gem (15 broad facets, with a slanted top face), and the cleft was cleaned up. The halo socket now sits inside the asset. The main session checked the result against the sheet's front view and committed it.
- **Open minors, for a later polish pass:**
  - The shell tops are blunt rather than the sheet's pointed peaks.
  - The rock lacks the sheet's two-tone warm-lit / cool-shade contrast, and its lit faces are too dark.
  - The crystal reads washed-out from the side.
  - The side view's back slope at f 0.10 is high.
  - Crystal share is a little high: 17 % against 16 % front, and 10.2 % against 8.5 % side.

## Follow-up (main session, 2026-10-28)

- `m014._hull` passes `dissolve_limit` a Python set of edges. A set iterates in memory-address order, so a rebuild can produce a slightly different core (found and fixed in `m015._hull` with `_edges_in_order`). Apply the same fix to m014 the next time 014 is rebuilt, then re-check the core and the Neon facet pick.
