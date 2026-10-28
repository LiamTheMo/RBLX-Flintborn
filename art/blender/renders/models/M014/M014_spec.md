# 014 Starstone — spec

Reference: `art/blender/assets/references/014.png` (STARSTONE, "Individual Asset Production Reference"; the sheet
footer says "PAGE 15/132", INDEX.md lists it as 14, "Starstone Low-Poly Construction Study"; 1024 × 1536 px).
Builder: `art/blender/kit/mcp/m014.py` → `build()` (not written yet).

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
