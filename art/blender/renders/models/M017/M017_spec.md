# 017 Berry Bush — spec

Reference: `art/blender/assets/references/017.png` (BERRY BUSH, "Shrub / Nature / Flintborn Style", "Individual Model
Study", footer "PAGE 17/132"; INDEX.md lists it as 17, "Flintborn Berry Bush Study"; 1024 × 1536 px).
Builder: `art/blender/kit/mcp/m017.py` → `build()` (stages 1–6 below). Procedure: `art/blender/kit/mcp/STAGES.md`.

User direction for every model: shapes must match the sheet; colours "need to match the master reference and blend
into the colors nearby. please ensure all color and textures are being made and applied." Effects ship wherever the
sheet shows them (this sheet shows none, §7).

Sheet text: "Chunky, stylized, low-poly shrub with bright red berries. Simple, readable shapes, broad flat-shaded faces
and clean colors. Designed for reuse, modular, and easy production." Modeling notes: "Modular construction: 1 trunk,
multiple leaf clumps, multiple berries"; "Simple, chunky low-poly forms with broad flat faces"; "Keep silhouette full and
readable from all angles"; "Leaves and berries are separate reusable parts"; "Use clean, solid colors. No textures or
noise" (but see §3.9); "Maintain consistent scale and joinery across all parts". Palette: Leaf Green, Trunk Brown,
Berry Red. The game already has a `BerryBush` resource node (`src/shared/Resources/NodeCatalog.luau`: material
Berries, 2 hits).

All pixel boxes are sheet pixels `(x0, y0, x1, y1)`, top-left origin. Paper is `#F2EDE6`. Masks (`m.py` `cls()`, HSV):
- **L, leaf:** sat ≥ 0.25 and hue 55–110° and g > 60.
- **B, berry:** sat ≥ 0.35 and (hue ≥ 340° or ≤ 12°) and r > 90.
- **T, trunk:** sat ≥ 0.18 and hue 12–55° and v < 0.85. For the trunk numbers only the T component touching the
  ground is used (`comps.py`), because berry and leaf edges leave a few brown pixels in the canopy.
- **O:** other non-paper (the ground shadow, dark edges). Not counted in the shares.

Scratch study material (pure Python, no Blender), in the session scratchpad
`C:\Users\Orang\AppData\Local\Temp\claude\D--Projects-Roblox-RBLX-Flintborn\3f83a1be-3b3d-4e4b-ae5a-7b04dbb75bdc\scratchpad\m017_study\`:
- `png.py` (reader, `crop`, `sample`); `m.py` (masks, view boxes `V`); `bb.json` (silhouette boxes);
- `measure.py` (bboxes, shares, top / leaf-bottom / trunk-top profiles, width per height), `comps.py` (berry
  components, trunk runs per height), `expl.py` (exploded and close-up components), `samp.py` / `samp2.py` (median,
  quartiles, deciles), `bands.py` (colour per height band), `spill.py` (leaf colour against distance from a berry),
  `gridcrop.py` (views with a 10 % grid: `g_front.png`, `g_side.png`, `g_rear.png`, `g_top.png`, `g_f34.png`,
  `g_r34.png`), `viz.py` (mask previews `cls_front.png`, `cls_f34.png`);
- crops: `f34.png`, `r34.png`, `front.png`, `side.png`, `rear.png`, `top.png`, `expl.png`, `cu_clump.png`,
  `cu_berry.png`, `cu_junc.png`, `pal.png`, and zooms `z_*_trunk.png`, `z_rear_ends.png`, `z_f34_toplobe.png`,
  `z_f34_frontlobe.png`, `z_expl_topclump.png`, `z_expl_peg.png`.
- To run them on our renders, point `R` at the render and set `P` to the render's background colour.

## 1. Study (2a)

### 1.1 Classification, size and scale

- **Classification:** full asset (forage resource node). Hero budget 4000 tris; each part under 1000.
- **What it is:** a round, slightly wide shrub. **Five faceted brown stems** splay out of one fused root foot and carry
  **fifteen faceted leaf lobes** (rounded low-poly ovoids with a five-facet apex, grouped as five leaf clumps on the five
  stem tips). **Eight glossy faceted red berries** sit half-sunk in the gaps between lobes: six on the front and right,
  two on the back. The lower 0.2–0.38 of the height shows bare stems with see-through gaps between them.
- **Target size: about 6.0 W × 4.8 D × 5.0 H studs** (H about 0.9 of the 5.5-stud character). Tolerances W ±0.3,
  D ±0.3, H ±0.25. Berries 0.9–1.05 across.
  - How it was derived: the front, side and rear cells are drawn at one scale (silhouette height 205 / 197 / 206 px).
    The berry is the only part with an obvious real size: front berries are 0.18–0.20 H across. A 1-stud berry
    (R05's `BerryShrubBerry` is 1 stud too) gives H ≈ 5.0 and **about 41 px per stud** in the front and rear cells,
    39.4 in the side. Measured: front W 251 px (6.1), rear 239 px (5.8), side depth 188 px (4.77).
  - Repo neighbours: the lobby `BerryBush` is 5.5 × 4.5 (README) / 6.2 × 4.3 (build_05), R05 `BerryShrub` 7 × 6 × 5.5.
    WorldModeling §3.2 suggests 0.25–0.65 C for a forage shrub, but the repository contracts win (WorldModeling,
    "Repository integration"). The size is a decision (§8).
- **Stud mappings used below** (build frame: front −Y, +X right, ground z 0, bbox centre at the origin):
  - front view X = (f − 0.50) × 6.1; rear view X = (0.50 − f) × 5.8 (screen right is −X);
  - side view (camera at +X): Y = (f − 0.50) × 4.77, **screen right = +Y (the back)** (M016 pitfall 13, confirmed
    from `frame_box`'s maths);
  - top view: X = (f − 0.50) × 6.0, Y = (h − 0.50) × 4.8 (image top = back), but see §3.6;
  - heights z ≈ h × 5.0 (the orthographic cells look down about 8°, §3.7).

### 1.2 Measured views (`measure.py`)

| View (box) | Silhouette bbox (px) | W : H | Leaf L | Berry B | Trunk T | Visible berries |
| --- | --- | --- | --- | --- | --- | --- |
| Front three-quarter (25,130,525,478) | 37–520 × 134–470 | 1.44 | 68.9 % | 17.3 % | 13.8 % | 6 |
| Rear three-quarter (530,130,1000,478) | 540–991 × 135–469 | 1.35 | 65.5 % | 15.6 % | 18.8 % | 4 full + 3 partial |
| Front (22,535,285,752) | 26–277 × 539–744 | 1.22 | 66.4 % | 18.9 % | 14.7 % | 6 |
| Side (290,535,510,752) | 309–497 × 547–744 | 0.95 (D : H) | 69.4 % | 17.1 % | 13.6 % | 3 |
| Rear (515,535,765,752) | 521–760 × 538–744 | 1.16 | 69.5 % | 8.4 % | 22.2 % | 1 full + 2 partial |
| Top (772,535,1010,752) | 784–998 × 544–751 | 1.03 (W : D) | 81.8 % | 16.9 % | 1.3 % | 5 |

- Reading: from every side about two-thirds of the silhouette is foliage. Berries take a fifth of the front and only
  a twelfth of the rear. The trunk shows most from the rear.
- The T share in the canopy views includes a little berry/leaf edge brown (about 1 point). Use the same masks on our
  renders, so it cancels.
- **Verifier check:** shares ±4 points (top ±6), profiles below ±0.06 h.

**Top profiles** (highest silhouette pixel per column, fraction of H, every 0.05 f):

| f | .00 | .05 | .10 | .15 | .20 | .25 | .30 | .35 | .40 | .45 | .50 | .55 | .60 | .65 | .70 | .75 | .80 | .85 | .90 | .95 | 1.0 |
| --- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- |
| Front | .39 | .48 | .63 | .71 | .75 | .76 | .91 | .96 | .94 | .96 | 1.0 | .97 | .92 | .86 | .87 | .83 | .76 | .74 | .66 | .55 | .46 |
| Side | .55 | .62 | .65 | .71 | .76 | .78 | .88 | .92 | .96 | 1.0 | .98 | .96 | .93 | .90 | .87 | .83 | .77 | .77 | .75 | .66 | .45 |
| Rear | .39 | .51 | .62 | .74 | .78 | .82 | .83 | .84 | .91 | .96 | .99 | .98 | .94 | .90 | .80 | .78 | .79 | .75 | .58 | .52 | .39 |
| f34 | .37 | .46 | .52 | .68 | .77 | .78 | .87 | 1.0 | .99 | .97 | .98 | 1.0 | .94 | .89 | .86 | .80 | .79 | .71 | .68 | .57 | .46 |
| r34 | .42 | .51 | .58 | .70 | .77 | .83 | .85 | .86 | .88 | .93 | .97 | .99 | .95 | .91 | .90 | .76 | .78 | .72 | .61 | .53 | .42 |

**Leaf bottom** (lowest leaf pixel per column; the high values at f 0.50–0.55 are the central gap where the stems and
the front-centre berry show):

```
f       .00 .05 .10 .15 .20 .25 .30 .35 .40 .45 .50 .55 .60 .65 .70 .75 .80 .85 .90 .95 1.0
front   .36 .27 .24 .15 .10 .12 .16 .09 .09 .25 .57 .56 .34 .29 .28 .16 .12 .10 .14 .38 .43
side     —  .22 .16 .14 .16 .16 .17 .18 .11 .09 .28 .36 .35 .35 .36 .17 .15 .14 .16 .21 .43
rear    .36 .28 .25 .26 .19 .13 .15 .33 .37 .24 .59 .53 .39 .22 .14 .13 .15 .26 .25 .28 .36
```

**Width per height** (silhouette width / W at h = 0.0, 0.1 … 1.0; the start f after the @):

```
front  .12@.47 .68@.18 .80@.13 .94@.04 .97@.01 .91@.06 .83@.09 .70@.14 .50@.25 .33@.29 .01@.51
side   .10@.44 .34@.32 .86@.07 .88@.06 .86@.12 .95@.01 .89@.03 .80@.13 .47@.29 .32@.32 .01@.45
rear   .13@.44 .31@.35 .64@.19 .91@.04 .98@.01 .91@.05 .76@.09 .75@.11 .48@.22 .28@.38 .01@.51
```

So the crown is widest at h 0.35–0.45 (z 1.75–2.25), a round dome above, and pulls in quickly below h 0.2. The
silhouette at the ground is only the stem foot (0.12 W).

### 1.3 Silhouette and composition per view

**Front (`g_front.png`):**
- A full round dome, apex at f 0.50 (h 1.0), shoulders at h 0.75 (f 0.20 and 0.80), widest at h 0.4. The left side
  bulges lower (f 0.0 at h 0.24–0.52) than the right (f 1.0 at h 0.27–0.57).
- **Stems:** a fused foot 0.32 H wide at the ground (1.6 studs) at f 0.39–0.65, widening to 0.39 H at h 0.15 as the
  stems splay. Separate stems show from h 0.2: a centre one (f 0.47–0.55, vertical, up to the front-centre berry at
  h 0.37) and a right one leaning up-right (f 0.58–0.66 at h 0.25). The left and far-right stems show only below
  h 0.2 before lobes hide them. Small see-through gaps between the stems at f 0.55–0.60, h 0.25–0.35.
- **Lobes** (about 12 visible; centre f, h; size in studs): L1 top big (0.42, 0.79; 1.9), L2 top-behind (0.54, 0.88;
  part), L3 left-upper (0.20, 0.64; 1.3), L4 far-left (0.07, 0.38; 1.4), L5 low-left big (0.31, 0.31; 1.95), L6
  bottom-left (0.20, 0.18; 1.2), L7 small low front by the stems (0.37, 0.13; 0.8), L8 centre (0.59, 0.58; 1.2),
  L9 right-upper (0.75, 0.65; 1.3), L10 low-right big (0.75, 0.40; 1.85), L11 far-right (0.93, 0.42; 1.4), L12
  bottom-right (0.82, 0.19; 1.3).
- **Berries** (`comps.py`; centre f, h; width): B1 (0.173, 0.451; 0.18 H), B2 (0.337, 0.605; 0.20), B3 (0.514, 0.466;
  0.195), B4 (0.687, 0.780; 0.19), B5 (0.867, 0.595; 0.14, partly behind a lobe), B6 (0.914, 0.315; 0.14, partly
  hidden). Each sits in a gap between lobes, roughly a third sunk.

**Side (camera at +X, screen right = +Y back; `g_side.png`):**
- Narrower dome (D : H 0.95), apex at f 0.45 (Y −0.2). The front berry B3 sticks out of the front silhouette
  (berry from f 0.0, leaves from f 0.03).
- **Stems:** foot 0.28 H (1.4) at f 0.35–0.64; at h 0.15 one stem leans to the front (f 0.28–0.38, Y −0.8) and is
  hidden above h 0.16; the centre column (f 0.48–0.59) rises to h 0.36; one leans back (f 0.64–0.72 at h 0.20, Y +0.8)
  to the back-low berry.
- **Lobes:** top big (Y −0.07, z 3.95, 1.8); front-upper (Y −1.2, z 3.2); top-back small (Y +1.0, z 3.9); centre-right
  big (Y +0.6, z 2.5, 1.85); back-right (Y +1.9, z 2.2); lower-front big (Y −0.84, z 1.65, 1.7); far-front low (Y −1.8,
  z 1.25); lower-back (Y +1.5, z 1.3).
- **Berries:** S1 front (0.117, 0.528; 0.234 H = 1.15 across, the biggest berry on the sheet), S2 back-low (0.771,
  0.284; 0.19), S3 back-high (0.832, 0.668; 0.21).

**Rear (camera at +Y, screen right = −X; `g_rear.png`, `z_rear_trunk.png`):**
- Dome with the apex at f 0.50; more stem visible than the front (T 22 %).
- **Stems: all five** show from the ground to h 0.35–0.45, fanned: far-left (screen) leaning out about 30°, left
  about 22°, centre vertical, right about 17°, far-right about 36° from vertical. Runs at h 0.25: f 0.28–0.32,
  0.36–0.44, 0.46–0.63 (two overlapping), 0.68–0.75. The two outer stems end in cut stubs under their lobes at
  h 0.3–0.35 (dark, shaded; no pale cut face shows).
- **Lobes** (about 10): top big (X −0.15, z 3.9, 1.9); upper-left (X +1.4, z 3.5); left big (X +1.35, z 2.4, 1.7);
  far-left (X +2.3, z 1.9); right big (X −1.3, z 2.55, 2.0); far-right (X −2.3, z 2.0); lower-left (X +1.3, z 1.0);
  lower-right (X −1.5, z 1.05).
- **Berries:** R1 partial at the left edge (0.111, 0.590 → X +2.26, z 2.95: B5 from behind), R2 centre (0.479, 0.449
  → X +0.12, z 2.25; 0.19 H), R3 upper-right (0.780, 0.706 → X −1.6, z 3.5; 0.20 × 0.17). A red sliver at the top-left
  (X +1.16, z 4.0) is B4 seen from behind.

**Top (`g_top.png`):**
- Six big elongated masses (each about 2.1 × 2.4 in plan) radiating from the centre: a big one up-right of centre,
  left, lower-right, lower-left, right, and a small one at the top. They read as the five clumps (plus the crown).
- Five berries: T1 (0.20, 0.29), T2 (0.30, 0.82), T3 (0.44, 0.47, near the centre), T4 (0.63, 0.10), T5 (0.84, 0.59).
- The cell is tilted (lobe sides show at the image bottom) and its W : D (1.03) does not match the front/side
  (1.28): §3.6.

**Three-quarters (`f34.png`, `r34.png`):** the f34 shows the same six berries in the same left-to-right order as the
front, four to five stems at the foot (`z_f34_trunk.png`). The r34 shows five stems clearly separate down to the
ground (`z_r34_trunk.png`), and 4 full + 3 partial berries, a different set from the f34 (it is not a mirror of it).

**Close-ups (Part Close-ups, right column):**
- **Leaf Clump (Bottom View)** (665,840,875,975), `cu_clump.png`: two lobes side by side; between them a brown
  **collar** (a flared, roughly hexagonal disc) and a **hexagonal peg** sticking down out of it. Peg about 0.31 of the
  clump width.
- **Joining Surface** (880,850,998,975): the peg end, flat, with a tiny centre dot (ignore: too small).
- **Berry Detail** (665,1010,875,1140), `cu_berry.png`: a round faceted berry (99 × 101 px: round), broad facets
  (a quad-looking highlight face about a quarter of the diameter), a tiny dark peg stub on its side.
- **Attachment Peg** (880,1020,998,1140): the berry (71 × 69, slightly squat) with a small brown cylinder peg on top,
  about 0.17 of the berry's diameter across and as long.
- **Trunk Junction** (665,1170,860,1305), `cu_junc.png`: two limbs in a V, 6-sided, faceted with slightly irregular
  planes; flat cut ends.
- **Top View (Junction)** (862,1180,998,1305): a **hexagonal** cut end (pale heartwood face) with two limbs going
  down-left and down-right. All wood sections are 6-sided.

### 1.4 Parts (Exploded View & Parts (20,800,650,1300), crop `expl.png`)

Labels: "Leaf Clump (x5)", "Berry (x6)", "Trunk Fork (x1)". Arrows plug clump pegs and berries into the fork's limb
ends and into the crotch. The exploded draws 5 clumps and 4 berries. Its scale (berries 56–59 px) is about **58 px per
stud**; it is drawn from about 15–20° above.

Facet language for every part: broad flat-shaded facets, 0.35–0.55 studs on a big lobe, calm and slightly irregular.
No spikes, no confetti, no smooth shading.

#### Leaf Clump: exploded top clump (225,806,411,930) 186 × 124 px = 3.2 × 2.1 studs; others (33,950,167,1066) 2.3 × 2.0, (181,921,293,1032) 1.9 × 1.9, (336,954,458,1075) 2.1 × 2.1, (472,1040,612,1144) 2.4 × 1.8 (all including the peg); crop `z_expl_topclump.png`

- **The labelled clump is three lobes** on one collar: a tall centre lobe (about 1.9 across, 1.8 tall), a smaller
  left lobe (about 1.5, set lower and out) and a right lobe behind (about 1.6). They overlap by about a third.
  The other four exploded clumps read as one or two lobes each.
- **Lobe shape:** an irregular faceted ovoid, W 1.0 : D 0.9 : H 0.85 of its size, widest at about 0.6 of its height
  above the peg. The top is a low **five-facet apex** (the icosahedral fan visible on every hero lobe), set a little off
  centre toward the outside of the bush. The underside tapers like an inverted teardrop into the collar. The hero lobes
  look the same: big ones 1.85–1.95 across, mid 1.2–1.5, small 0.8–1.0.
- **Collar:** dark brown flared hex disc, about 0.9 across × 0.2, sunk into the lobes' underside.
- **Peg:** 6-sided prism about 0.5–0.6 across × 0.6 long (exploded pegs 0.5–0.9 across including the collar),
  flat end.
- **Triangles:** lobe 80 (a Blender `primitive_ico_sphere_add(subdivisions=2)`, 80 faces, 42 verts, reshaped; see
  §4), collar 12–16, peg 20 → clump about 270–290.
- **Construction:** `_lobe(size, apex_dir, seed)`: an ico-2 sphere scaled to the ovoid, its apex vertex turned to
  `apex_dir`, the lower hemisphere tapered toward the peg (scale ring by ring, 1.0 → 0.55), plus 2–3 broad, low-
  frequency pulls (±6 % radius over a third of the lobe). **No per-vertex noise.** `_clump(lobes, seed)` places 2–4
  lobes from a list `[(offset, size, apex_dir, seed)]` on one collar and peg. The exported part uses the exploded
  three-lobe list; each hero clump uses its own list (§2.2) from the same builder.

#### Berry: exploded (116,880,172,935), (130,1061,188,1119), (445,899,503,957), (511,970,566,1025), 56–59 px = 1.0 stud; close-ups (708,1024,806,1124), (902,1051,972,1119)

- **Shape:** a round faceted ball, 1.0 across, squash z 0.96. Broad facets: an ico-2 sphere (80 tris), radius
  jitter ≤ 2 %, so it reads round, not a jewel (WorldModeling §6.7, §18).
- **Peg:** a 5–6-sided brown stub 0.17 across × 0.17 long on one pole. In the hero the peg points into the canopy
  (hidden); berry sizes vary 0.9–1.05 (the side view's front berry reads 1.15).
- **Triangles:** about 90–100 with the peg.

#### Trunk Fork: exploded (177,1083,401,1262) 224 × 179 px = 3.9 W × 3.1 H studs; close-ups `cu_junc.png`

Trunk runs (`expl.py`; width in studs, t from the top):

| t | Width | What |
| --- | --- | --- |
| 0.00–0.31 | centre limb 0.79–0.86; right limb 0.6–1.07 (seen obliquely) | two upper limbs, flat hex cut ends at t 0.00 (centre) and 0.09 (right) |
| 0.27–0.54 | left limb 0.5 → 1.12 (oblique) | the left limb, leaving at t 0.55, cut end at t 0.27–0.31 |
| 0.36–0.54 | 1.5–1.95 (centre + right merged) | the upper crotch at t 0.36 |
| 0.58 | 2.55 | the fork (all three) |
| 0.63–0.94 | 2.3 → 1.36 | the trunk, tapering down |
| 0.94–1.00 | 1.36 → 0.78 | the flared foot seen from above |

- **Shape:** a 6-sided trunk (1.4 at the foot, flaring slightly, 1.5 at t 0.85) splits at about 1.3 above its foot
  into a **centre limb** (nearly vertical, leaning about 10° left, to 3.1), a **right limb** (about 40° from vertical,
  cut end at 2.8) and a **left limb** (about 50–55°, cut end at about 2.2). Limbs 0.75–0.85 thick, tapering 10 %.
  Flat **hexagonal cut ends** with a pale heartwood face. Facets: rings every 0.5–0.7, each turned and scaled a little
  (±8 % radius, ±10° twist), as M016's `_limb`.
- **Triangles:** 200–280.
- **The hero does not use this exact shape** (§3.1): every hero view shows five thinner stems (0.5) parting at the
  ground. Build `_trunk(limbs, split_z, radius, seed)` once; the exported part is the exploded's 3-limb call, the hero
  the 5-stem call (§2.1).

## 2. Layout (starting values; tune to §1.2–§1.3 on the 8° sheet-elevation extras)

Build frame: front −Y, +X right, ground z 0. Every piece is a transformed copy of a part-builder result (m011
`_paste` pattern). Coordinates below are relative to the bbox centre; the stems' foot sits at about (+0.1, 0).

### 2.1 Skeleton (5 stems, `_trunk` hero call)

Each stem: 6 sides, Ø 0.55 at its base flaring to 0.65 at z 0, tapering to 0.42 at the tip; rings every 0.5–0.7 with
±8 % / ±10° jitter; a flat hex cut end (hidden in its clump). Stems start at z −0.2 and are floor-cut at z 0. Their
bases overlap, so the union fuses them into one foot about **1.6 W × 1.4 D** at the ground; the V-creases between them
run down to the ground (rear and r34). Lean = angle from vertical; azimuth from +X, counter-clockwise.

| Stem | Base (X, Y) at z 0.25 | Azimuth | Lean | Length | Tip (X, Y, z) | Carries | Seen |
| --- | --- | --- | --- | --- | --- | --- | --- |
| S1 centre | (+0.1, +0.05) | — | 3° toward −X | 2.9 | (−0.05, +0.05, 3.1) | clump C1 (crown) | front centre column to h 0.37; side centre column; rear centre |
| S2 front-left | (−0.15, −0.45) | −125° | 30° | 2.3 | (−0.8, −1.4, 2.25) | C2 | front only below h 0.2 (L7 hides it); side front-leaning stem at Y −0.7, z 0.75 |
| S3 front-right | (+0.45, −0.2) | −15° | 22° | 2.6 | (+1.4, −0.45, 2.65) | C3 | front right stem (f 0.58–0.66 at h 0.25); rear X +0.35–0.8 at z 1.25 |
| S4 back-right | (+0.5, +0.3) | +35° | 35° | 2.0 | (+1.45, +0.95, 1.9) | C4 | rear far-left (screen) stem at X +1.05–1.3, z 1.25; side back-leaning stem |
| S5 back-left | (−0.35, +0.25) | +160° | 40° | 2.0 | (−1.55, +0.7, 1.8) | C5 | rear far-right (screen) stem at X −1.05 to −1.45, z 1.25 |

- Visible stem height: 0.2–0.38 H (1.0–1.9 studs) under the canopy, as WorldModeling §8.2 asks (lower quarter to
  third). Keep two or more see-through gaps between stems in the front, side and rear (sheet: front f 0.55–0.60,
  h 0.25–0.35; rear between all five).
- **Collars** (optional, decision §8): where each stem enters its clump, a small flared hex collar (the part's
  joinery), visible only from below (underside view).

### 2.2 Canopy (15 lobes in 5 clumps, `_clump` per-instance lobe lists)

Lobe centres and sizes (Ø = the lobe's width; height 0.85 Ø; apex direction = outward and up from the bush centre
unless noted). Checked against the front, side and rear lobes in §1.3.

| Lobe | Clump (stem) | Centre (X, Y, z) | Ø | Front (f, h) | Notes |
| --- | --- | --- | --- | --- | --- |
| L1 top big | C1 (S1) | (−0.35, −0.05, 3.95) | 1.9 | (0.42, 0.79) | the bush's apex; its apex vertex offset +X to sit at f 0.50, h 1.0 |
| L2 top-back | C1 | (+0.6, +0.5, 4.3) | 1.2 | (0.54, 0.88) | shows over L1's right shoulder; rear top-left of L1 |
| L3 left-upper | C1 | (−1.8, −0.3, 3.2) | 1.3 | (0.20, 0.64) | |
| L5 low-left big | C2 (S2) | (−1.15, −1.1, 1.55) | 1.95 | (0.31, 0.31) | the big front-left lobe; its front edge (Y −2.05) shows in the side view's far-front low lobe |
| L7 small low | C2 | (−0.7, −0.9, 0.7) | 0.8 | (0.37, 0.13) | hides S2; lowest leaf z ≈ 0.4 |
| L8 centre | C3 (S3) | (+0.55, −1.1, 2.95) | 1.2 | (0.59, 0.58) | between B3 and B4 |
| L9 right-upper | C3 | (+1.3, −0.8, 3.3) | 1.3 | (0.75, 0.65) | the side view's front-upper lobe |
| L10 low-right big | C3 | (+1.5, −1.2, 1.9) | 1.85 | (0.75, 0.40) | the side view's lower-front big lobe |
| L11 right | C4 (S4) | (+2.15, +0.5, 2.3) | 1.7 | (0.93, 0.42) | the side view's centre-right big lobe; rear far-left |
| L12 bottom-right | C4 | (+1.6, +0.6, 1.0) | 1.3 | (0.82, 0.19) | rear lower-left; side lower-back |
| L13 back-right upper | C4 | (+1.4, +1.3, 3.5) | 1.4 | hidden | rear upper-left; side top-back |
| L14 back-right | C4 | (+1.2, +1.7, 2.2) | 1.6 | hidden | rear left big; side back-right edge (Y +2.5) |
| L4 far-left | C5 (S5) | (−2.25, +0.2, 1.9) | 1.45 | (0.07, 0.38) | rear far-right |
| L6 bottom-left | C5 | (−1.4, +0.2, 1.0) | 1.2 | (0.20, 0.18) | rear lower-right |
| L15 back-left big | C5 | (−1.3, +1.3, 2.6) | 1.9 | hidden | rear right big; rear centre berry sits between L14 and L15 |

- Lobes overlap their neighbours by 0.2–0.5 (no floating lobes, no coplanar contact). Each clump's lobes overlap
  the stem tip by at least 0.3.
- Vary each lobe: its own seed, apex direction, ±10 % per-axis scale. Never two lobes with the same mesh orientation
  side by side (WorldModeling §6.4: "not identical untouched icospheres").
- From the top the five clumps must read as five or six radiating masses (top view).

### 2.3 Berries (8 copies of the Berry part)

Each berry sits in a gap between two or three lobes, sunk 25–35 % of its diameter (its centre about 0.15–0.25 outside
the lobe surfaces), its peg pointing at the nearest stem tip.

| Berry | Centre (X, Y, z) | Ø | Front (f, h) | Side / rear / top | Notes |
| --- | --- | --- | --- | --- | --- |
| B1 front-left low | (−2.0, −1.1, 2.25) | 0.9 | (0.173, 0.451) | top T1 | between L3, L4 and L5 |
| B2 front-left high | (−1.0, −1.4, 3.0) | 1.0 | (0.337, 0.605) | | between L1, L3 and L5 |
| B3 front centre | (+0.1, −1.95, 2.4) | 1.05 | (0.514, 0.466) | side S1 (front edge, 1.15); top T4 | over the centre stem; the front-most point of the bush in the side view |
| B4 top-right | (+1.15, −0.3, 3.9) | 0.95 | (0.687, 0.780) | rear sliver at X +1.16, z 4.0; top T3 | between L1, L2 and L9 |
| B5 right high | (+2.2, +0.9, 3.05) | 1.0 | (0.867, 0.595), partly hidden | side S3; rear R1 (left edge); top T5 | between L11 and L13 |
| B6 right low | (+2.45, +0.9, 1.5) | 0.95 | (0.914, 0.315), partly hidden | side S2 | between L11 and L12 |
| Bk1 back centre | (+0.1, +1.95, 2.3) | 0.95 | hidden | rear R2 (centre) | between L14 and L15, above the stems |
| Bk2 back-left high | (−1.4, +1.5, 3.5) | 0.9 | hidden | rear R3; top T2 | between L1 and L15 |

**Expected hero:** about 6.1 × 4.9 × 5.0. Tris (§4.3): 15 lobes × 80 = 1200; 8 berries × 80 = 640; stems about 300;
collars about 60 → about 2200 before the union, about 1900–2600 after.

## 3. View conflicts and resolutions

### 3.1 Trunk Fork (exploded) against five stems (every hero view)

- The exploded "Trunk Fork (x1)" is one 1.4-wide trunk that splits 1.3 above the ground into three 0.8-thick limbs.
  Every assembled view (front, side, rear, f34, r34) instead shows a fused foot 1.4–1.6 wide with **five 0.5-thick
  stems** separate almost from the ground (`z_r34_trunk.png`, `z_rear_trunk.png`: the creases between stems reach the
  ground).
- **Resolution:** the hero views govern the assembled bush (WorldModeling §1.1). One builder `_trunk(limbs, split_z,
  radius, seed)` makes both: the exported `BerryBushTrunkFork` part is the exploded 3-limb call (split 1.3, radius
  0.4); the hero's skeleton is the 5-stem call (split at the ground, radius 0.25–0.28). Same rings, facets, cut ends
  and keys.
- **Alternative:** a hero built from the exact exploded fork plus two extra stems. It would show a single trunk to
  z 1.3, which no hero view does. Not recommended.

### 3.2 Leaf Clump (x5) against twelve to fifteen lobes

- The hero shows about 12 lobes from the front, 9–10 from the side and rear, and six masses from the top. The
  exploded labels 5 clumps, and its labelled clump has three lobes.
- **Resolution:** five clump instances (one per stem tip) of two to four lobes each = 15 lobes (§2.2). The exported
  `BerryBushLeafClump` part is the exploded three-lobe clump.

### 3.3 Berry (x6) against eight

- The front and the f34 show exactly six berries, all on the front and right. The rear shows three (one of them B5
  from behind), the r34 four full and three partial, the top five. Six berries cannot fill the rear's centre and
  upper-right berries without showing in the front.
- **Resolution:** **8 berries**: the front's six (B1–B6) plus two back berries (Bk1, Bk2) for the rear (§2.3).
  The exported `BerryBushBerry` part is one berry.
- **Alternative:** 6 (the label). The rear then shows only B5's edge and B4's sliver: about 3 % B against the sheet's
  8.4 %. Decision §8.

### 3.4 The rear is not the front's mirror, and the r34 is not the f34's mirror

- Their berry and lobe positions disagree (generated sheet). **Resolution:** the front and f34 govern the front half;
  the rear and r34 govern the back half; the side governs depth. The side and rear agree with the front on B5 (X +2.2,
  z 3.0) and B4 (X +1.15, z 3.9), which fixed those two.

### 3.5 Front and rear widths differ

- Front 251 px (6.1), rear 239 px (5.8). **Resolution:** W 6.0. Expect our front W : H about 0.02 under the sheet's
  and the rear's about 0.04 over; tolerance ±0.08.

### 3.6 The top view is tilted and its W : D does not fit

- Lobe sides show at the image bottom (a camera about 65–75° up, from the front), and W : D is 1.03 against the
  front/side's 1.28. **Resolution:** the top governs only the counts and spread: five or six radiating masses, 5–7
  berries visible, spread round (one near the centre, one back-left, one right). Compare with the kit top (0, 89) and an
  extra `top_tilt (0, 70)`.

### 3.7 Camera elevation

- The stems' ground contact curves up 0.005–0.015 h over the foot's half-width (about 0.75), so about 6–8°. The
  upper faces of the low lobes are lit and visible, which also suggests a slight downward look.
- **Resolution:** about **8°**. Render extras `front_sheet (0, 8)`, `side_sheet (90, 8)`, `rear_sheet (180, 8)` and
  compare §1.2's profiles on those. The kit's 4° views read slightly flatter.

### 3.8 The three-quarter views are drawn wider

- f34 W : H 1.44 and r34 1.35, but a 6.0 × 4.8 round bush seen 28° off axis is no wider than its front (about 1.2).
  The sheet's 3/4 cells are simply drawn wider (a closer perspective camera). **Resolution:** judge the 3/4 views by
  shares, berry count and order, stem count and lobe arrangement, not by W : H. Compare with the kit's front34
  (−28, 12), rear34 (152, 12) and an extra `f34_sheet (−20, 14)`. Record the W : H miss.

### 3.9 "Clean, solid colors. No textures or noise" against the user's blended-colour rule

- The user's standing rule wins: graded regions (young lime crown lobes, mid body, old dark lower lobes; bark darker
  under the canopy) plus calm Tint. The sheet's own renders show these differences (§5.3), so this matches the sheet.
  Keep Tint low (leaves 0.035, berries 0.02) so it stays "clean".

### 3.10 Glossy berries against WorldModeling §5.2 ("avoid glassy berries")

- Every sheet berry has a white-pink specular facet (p95 `#FE8579`–`#FE9490`). **Resolution:** opaque, glossy but not
  glassy: roughness 0.3–0.35, specular 0.5, no transparency, no emission.

### 3.11 Lime lit faces and green shade faces

- Lit leaf faces are lime (71°, `#AAC72D`), shade faces deep green (85°, `#405C19`), in every lobe. That is mostly the
  warm sun against a cool fill. **Resolution:** never paint by facing. The young/old split is per lobe and by canopy
  height (§5.5); the studio does the rest. Check `K.check`'s facing correlation (< 0.5).

## 4. Construction plan (Stage 1)

1. **Parts first**, each with its own function and checked against its cell:
   - `lobe()` (one lobe) → `clump(lobes)` (`BerryBushLeafClump`: the exploded three-lobe clump with collar and peg);
   - `berry()` (`BerryBushBerry`: ball and top peg);
   - `trunk(limbs, split_z, radius)` (`BerryBushTrunkFork`: the exploded 3-limb fork with pale cut ends).
   - Render a parts shot (`extra`, about (−20, 15)) laid out as the exploded: the fork at the bottom, the clump above,
     the berry to the right. Compare the fork's run table (§1.4), the clump's 3.2 × 2.1, the berry's 1.0.
2. **Hero:**
   1. `trunk` with the five stems of §2.1; `_paste` 5 clump instances (§2.2 lobe lists) on the stem tips, 8 berries
      (§2.3), the optional collars.
   2. One exact self-union (m011 `_self_union`), then `union_loose`, then `m004.floor_cut` at z 0.
   3. Origin at the bbox bottom centre; transforms applied.
3. **Budget** (`_lobe` ico-2 = 80 tris; berry ico-2 = 80; stems 6 sides): hero about 2000–2600 (limit 4000); clump
   about 280, berry about 95, fork 200–280 (limit 1000 each). If the lobes look too coarse at the f34 zoom, ico-2 is
   still the right level (the sheet's lobes show about four facets across a face); don't go to ico-3 (320 tris).
4. **Placeholder keys** (stage 1): `m017_leaf`, `m017_bark`, `m017_berry`, `m017_peg`, `m017_heartwood`.
   Stage 4 adds the others (§5.4).
5. **Stage 1 acceptance** (render, compare every view, measure):
   1. **Profiles:** top and leaf-bottom profiles and the width table within ±0.06 of §1.2 on the 8° extras.
   2. **Shares** (L / B / T, same masks) within ±4 points per view: front 66 / 19 / 15, side 69 / 17 / 14, rear
      70 / 8 / 22, top 82 / 17 / 1 (±6). The 3/4 views: L ±5, B count and order.
   3. **Berries:** front shows exactly 6 at §2.3's (f, h) ±0.05; side 3 (front edge plus two at the back); rear 1 full
      plus 2 partial with one central; top 5–7.
   4. **Stems:** five, 6-sided, Ø 0.42–0.65, fanned as §2.1; front shows the centre and right stems above h 0.2; rear
      shows all five from the ground to h 0.35–0.45; see-through gaps between stems in front, side and rear.
      Foot 1.6 W × 1.4 D at the ground.
   5. **Lobes:** 15, ico-2 based, each with a visible five-facet apex, Ø per §2.2 ±10 %; no two identical neighbours;
      lowest leaf z 0.35–0.5.
   6. **Parts against their cells** (shape, proportions, facet size; the fork's runs; the clump's three lobes, collar
      and hex peg; the berry's roundness and top peg).
   7. **Hero size** 6.0 × 4.8 × 5.0 (±0.3 / ±0.3 / ±0.25).

## 5. Colour plan (Stage 4)

### 5.1 Swatches (flat; medians of a 45 × 45 box inside each)

| Swatch | Box | Hex | HSV |
| --- | --- | --- | --- |
| Leaf Green | (45,1375,90,1420) | `#779931` | 80°, 0.68, 0.60 |
| Trunk Brown | (157,1375,202,1420) | `#906642` | 28°, 0.54, 0.56 |
| Berry Red | (267,1375,312,1420) | `#E23434` | 0°, 0.77, 0.89 |

- The leaf swatch is close to the rendered leaf median (`#6F9322`, 79°, 0.77): slightly greyer and lighter.
- The trunk swatch matches the **unshadowed** bark (exploded fork `#8C5F39`; hero stem foot `#845A35`–`#8B5D35`). The
  hero's stem medians (`#5B3F25`–`#744F2C`) are darker because the canopy shades them.
- The berry swatch is duller than the render (`#F62624`, 1°, 0.85, 0.96). Calibrate to the render.

### 5.2 Rendered regions (`samp.py`, `samp2.py`; median, lit quartile, shade quartile)

| Region | Box | Mask | Median | Lit | Shade |
| --- | --- | --- | --- | --- | --- |
| Leaves, front | V front | L | `#6F9322` | `#AAC72D` | `#405C19` |
| Leaves, side / rear | V | L | `#678B21` / `#658924` | `#A3C12F` / `#A2C12E` | `#45641B` / `#44601B` |
| Leaves, f34 / r34 | V | L | `#709221` / `#678B23` | `#ADC92E` / `#A9C62E` | `#3F5C18` / `#45611B` |
| Leaves, top | V top | L | `#86AB20` | `#B6D025` | `#4F721B` |
| Leaves, exploded | (20,800,650,1150) | L | `#618426` | `#9EBE2F` | `#476424` |
| Leaves, clump underside close-up | (665,840,875,975) | L | `#597C29` | `#8EB02F` | `#425F23` |
| Berries, front / f34 | V | B | `#F62624` / `#F82523` | `#FD6560` / `#FD5955` | `#9C0C0D` / `#9C0B09` |
| Berries, side / rear / top | V | B | `#EB2222` / `#F52526` / `#EA2221` | `#FD6966` / `#FD7674` / `#FD6661` | `#930E0D` / `#AD1415` / `#850707` |
| Berries, exploded | (110,870,575,1125) | B | `#EB2224` | `#FD6B67` | `#B9181A` |
| Berry close-up | (665,1010,875,1140) | B | `#EB2628` | `#FD7370` | `#C51C1D` |
| Berry peg (close-up) | (880,1020,998,1140) | T | `#865137` | `#B58975` | `#613522` |
| Bark, exploded fork | (177,1083,401,1262) | T | `#8C5F39` | `#A67348` | `#65462A` |
| Bark, junction close-up | (665,1170,860,1305) | T | `#7A5333` | `#B37F52` | `#65472B` |
| Bark, hero stems front / f34 | V, ground component | T | `#6B492B` / `#744F2C` | `#93653B` / `#9B683C` | `#3B2A17` / `#442F1A` |
| Bark, hero stems side / rear / r34 | V, ground component | T | `#5B3F25` / `#6B492B` / `#614327` | `#885B36` / `#93633A` / `#815733` | `#392816` / `#3F2D19` / `#3C2A17` |
| Heartwood (cut end, junction top view) | (915,1205,950,1240) | all | `#C3A588` | | `#B89A7D` |
| Pegs and collars, exploded | (306,910,358,962), (139,1009,174,1043), (371,1048,409,1085), (458,1080,502,1122) | T | `#534430`–`#5C4B38` | `#755C44`–`#997B5D` | `#3A3021`–`#423727` |
| Peg and collar, clump close-up | (721,904,785,967) | T | `#554531` | `#82664D` | `#3A3121` |

Deciles (dark → light), front:

```
leaves  #334C14 #43621C #4D6E25 #5A7C21 #698B1F #73981F #7EA326 #90B223 #A6C42C #AECB32
berries #7C0707 #A91110 #C21A1B #E91D1E #F82121 #FA2624 #FA2D2A #FC3B36 #FD5854 #FE9490
bark    #2F2112 #402C19 #4C351F #563C23 #624428 #75502F #835934 #8B5E37 #91633A #9E6C41
```

### 5.3 How the colour works

**Leaves.**
- One yellow-green family, hue 71–89°, sat 0.70–0.82. Lit faces lime (71°), shade faces deep green (85–89°).
- **Height gradient** (median per band; `bands.py`):

  | h band | 0.1–0.2 | 0.2–0.3 | 0.3–0.4 | 0.4–0.5 | 0.5–0.6 | 0.6–0.7 | 0.7–0.8 | 0.8–0.9 | 0.9–1.0 |
  | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- |
  | Front | `#4F6E1E` | `#517220` | `#6B8E23` | `#7A9D23` | `#5E811C` | `#789D22` | `#6F911C` | `#99BA2C` | `#A4C438` |
  | Side | `#4C6920` | `#5D8024` | `#5F8321` | `#678A1F` | `#85A820` | `#6A8C20` | `#64871D` | `#97B830` | `#AAC83A` |
  | Rear | `#47621D` | `#4A6823` | `#547621` | `#66891F` | `#9ABB25` | `#547721` | `#618624` | `#83A82E` | `#9ABB3C` |

  The crown (h > 0.8) is pale lime in every view; the lowest lobes are deep. In the low bands even the lit quartile is
  dark (`#5B7B26`–`#6E9120`), so part of it is canopy shade, part paint.
- **Per lobe** (front, ±14 px boxes at each lobe's centre): young/lime lobes L1 `#789A1B` (lit `#AECB2E`), L2
  `#9EBE36`, L5 `#93B422`, L8 `#A8C428`, L10 `#A4C129`; mid L3 `#789D22`, L9 `#82A72B`; old/deep L4 `#5A7C22`, L6
  `#4B6B1A`, L11 `#49691A`, L12 `#5B7B1C`. The front-facing, upper lobes are young; the low and side lobes old.
- **Contact with berries:** leaf within 0.05–0.25 stud of a berry is darker (`#46641B`–`#52741C` against `#729623`
  away; `spill.py`), with no red spill. A soft dark band, mostly contact shadow.

**Berries.**
- Saturated red, hue 0–2°, sat 0.85. Deciles span deep `#7C0707` (underside, contact) to the pink-white highlight
  facets `#FE9490`: glossy. The body is one paint; the range is light and gloss.

**Bark.**
- Warm mid brown, hue 27–30°, sat 0.59–0.62 (rendered); the heartwood ends pale `#C3A588`; pegs and collars a duller,
  greyer dark brown (32–34°, sat 0.40).
- **Height gradient** on the hero stems (median per band, front / rear):
  h 0.0–0.1 `#845A35` / `#815633`; 0.1–0.2 `#7A5430` / `#754F2E`; 0.2–0.3 `#533A22` / `#5F4227`; 0.3–0.4
  `#3A2816` / `#49331E`. The foot is sunlit; the stems darken quickly under the canopy.

### 5.4 Keys (start from these; `K.calibrate`; write the calibrated hexes into `palette()`)

Calibration targets are rendered medians, not swatches. Kinds: `M.sample(..., "green")` for leaves; `K.sample(...,
"vivid")` on berry-only boxes (vivid also catches leaves, so keep the boxes tight); `M.sample(..., "brown")` for bark;
`"all"` on tight boxes for heartwood and pegs (sat ≈ 0.3–0.4 sits on the brown filter's edge).

| Key | Calibration target | Where | Finish |
| --- | --- | --- | --- |
| `m017_leaf` | `#6B8F22` (view medians `#658924`–`#709221`; swatch `#779931`) | lobe bodies | rough 0.85, low spec (`FOLIAGE_SPEC`) |
| `m017_leaf_young` | `#A0C032` (crown bands `#99BA2C`–`#AAC83A`; young lobes `#93B422`–`#A8C428`) | young lobes and the crown (§5.5) | rough 0.85, low spec |
| `m017_leaf_old` | `#4E6D1E` (low bands `#47621D`–`#517220`; old lobes `#49691A`–`#5B7B1C`) | old lobes, lobe undersides by height, berry contact | rough 0.85, low spec |
| `m017_berry` | `#F42524` (view medians `#EA2221`–`#F82523`) | berry bodies | rough 0.3, spec 0.5 |
| `m017_berry_deep` | `#B5161A` (exploded shade `#B9181A`; close-up shade `#C51C1D`) | the berry's third nearest its peg / the canopy | rough 0.3, spec 0.5 |
| `m017_berry_stem` | `#865137` | berry peg (part only) | rough 0.9 |
| `m017_bark` | `#8A5D38` (exploded fork `#8C5F39`; stem foot band `#845A35`–`#8B5D35`; swatch `#906642`) | stem and fork bodies | rough 0.9 |
| `m017_bark_dark` | `#5E4128` (junction p05 `#5E4128`; exploded shade `#65462A`; hero 0.2–0.3 band `#533A22`–`#5F4227`) | stems under the canopy, crotches, ground contact | rough 0.9 |
| `m017_heartwood` | `#C3A588` | cut-end faces (fork part; hero only if any shows) | rough 0.85 |
| `m017_peg` | `#584833` (pegs `#534430`–`#5C4B38`; collar `#554531`) | clump collars and pegs | rough 0.9 |

- **Calibration warnings:**
  - `leaf_young` sits near the green filter's limit only if it drifts yellow; `#A0C032` passes (g − r = 32). Kit
    memory: calibrated greens come out darker than the painted sheet; trust the render match.
  - Specular adds blue-white glints: leaves must use the low foliage specular, or the lime crown washes grey.
  - Calibrate `bark` on the dome (unshadowed), then re-measure the hero's stem bands: the canopy shadow in the studio
    should give most of the 0.2–0.4 darkening. Add `bark_dark` only as far as the bands still miss.
  - `berry`'s lit tone is near the red clip; lower the specular rather than the colour if the dome blows out.

### 5.5 Blending (`K.blend(mode="blend", steps=3)` over explicit face lists; fields are positions, never facing)

- **Leaves:**
  - Per lobe, a maturity mix: young lobes L1, L2, L5, L8, L10 → 60 % `leaf_young`; mid L3, L9, L13, L14, L15 →
    `leaf`; old L4, L6, L7, L11, L12 → 55 % `leaf_old`. Neighbouring lobes then differ the way the sheet's do.
  - Canopy height field across all lobes: z > 4.0 → +0.3 toward `leaf_young`; z < 1.3 → +0.4 toward `leaf_old`,
    blended over 0.5 stud with broad noise ±0.15 on z, so it doesn't read as a band.
  - Within each lobe, the lowest 30 % of its height (relative z, not normals) → +0.25 toward `leaf_old` (the quieter
    underside, WorldModeling §6.4).
  - Berry contact: faces within 0.25 of a berry → 50 % `leaf_old`.
  - Stem/collar entry: faces within 0.3 of a stem tip → 50 % `leaf_old`.
- **Berries:** `berry` body; the third of faces nearest the peg end → `berry_deep`, blend 3 steps (the contact side
  that faces into the canopy). Nothing by facing; no highlight paint (gloss does it).
- **Bark:** `bark` body; z > 1.6 → 50 % `bark_dark`, z > 2.2 → 75 % (under the canopy); faces within 0.12 of a
  neighbouring stem (the V-creases) → 50 % `bark_dark`; z < 0.12 → 40 % `bark_dark` (ground contact). Broad noise
  patches along each stem (scale 0.6, level 0.3) between `bark` and a 70 % `bark_dark` mix, for the sheet's uneven
  facets.
- **Hard edges only** where materials meet: berry against leaf, leaf against bark or collar, heartwood cut faces.

### 5.6 Texture (Tint) and finish

- **Tint:** per piece `tint_var` about 0.04 (each lobe and each berry differs slightly).
  - Leaves: `K.texture` amp 0.035, scale 0.5 (broad, per facet group, never confetti).
  - Bark: amp 0.05, scale 0.35 (along-stem mottling).
  - Berries: amp 0.02.
- **Finish:**

  | Material | Roughness | Specular | Metal | Notes |
  | --- | --- | --- | --- | --- |
  | Leaf keys | 0.85 | `FOLIAGE_SPEC` 0.06 (`set_colour(low_spec=True)`) | 0 | matte faceted foliage |
  | Berry keys | 0.3 | 0.5 | 0 | glossy, opaque; no transparency, no emission |
  | Bark, peg, heartwood | 0.85–0.9 | normal | 0 | matte wood |

### 5.7 Re-measure (final renders against the sheet, same boxes and masks)

- Leaf median within about 10 levels of `#6B8F22` per view; the band table in §5.3 within about 12 levels and in
  order (crown palest, lowest bands deepest); the per-lobe groups in order (young > mid > old).
- Berry median within 10 levels of `#F42524`; hue 0–3°.
- Stem foot band (h 0–0.1) within 12 of `#845A35`; the 0.2–0.3 band within 15 of `#5A3E24`.
- Shares per §4, step 5.2.

## 6. Joins and contact (this sheet has no cracks, pits or seams)

- **Berries in the canopy:** each berry sunk 25–35 % into two or three lobes, so it is held, not perched (R05's
  lesson: berries "perched on the rim" read wrong). No gap under a berry from any view.
- **Stems into clumps:** each stem tip runs at least 0.3 into its clump's lowest lobe; the optional collar (§8) caps
  the entry.
- **Stem foot:** the five stems' bases overlap and fuse into one foot; the creases between them stay as real V-grooves
  in the mesh (keep them through stage 2: they are silhouette and colour geometry).

## 7. Lighting and VFX plan (Stages 5 and 6)

**What the sheet shows:** an ordinary lit shrub. No glow, halo, light, sparkle, falling leaves, dust or particles
anywhere. The berries' bright facets are specular highlights on a glossy surface, not emission (their shade facets go
to `#7C0707`). WorldModeling §1.2: no ordinary asset "recolored neon with a glow halo"; §15: ordinary forage stays calm.

### 7.1 Stage 5 (lighting): skip, and record why

- **No emissive faces.** `export_kit_roblox.py` turns every face with emission ≥ 1.0 into a flat Neon part; that would
  erase the berries' shading and gloss. No PointLight: nothing on the sheet glows or is enclosed.
- **Studio note (Requires Manual Validation):** check in Studio that the berries keep a visible gloss (the palette
  export may flatten roughness); if they read matte, set the berry MeshPart's material to SmoothPlastic.

### 7.2 Stage 6 (VFX), kinds in `art/blender/lib/vfx.py`

- **Kinds that exist:** `torch_fire`, `campfire`, `brazier_fire`, `forge_fire`, `chimney_smoke`, `embers`,
  `heat_glow`, `glyph_glow`, `rune_glow`, `waterfall_mist`, `water_foam`, `waterfall_curtain`, `water_flow`,
  `vapour`, `harvest_hit`, `harvest_deplete`, `ore_glint`, `crystal_glow`, `dust`. No new kind is proposed.
- **Recommended: none.** The sheet shows no effect, and m009 and m011–m016 decided against harvest sockets.
  Record "skipped: sheet shows no VFX".
- **Options** (decision §8):
  - `harvest_hit` at the front (0, −2.5, 2.4) and `harvest_deplete` at the foot (0, 0, 0.5), colour overrides
    `["#8DB02A", "#E8302C"]` (leaf and berry chips), as R05 `BerryShrub` shipped. Only if the main session wants the
    berry node to give hit feedback like R05.
  - Not recommended: `ore_glint` on the berries (reads as magic or crystal, not forage).

## 8. Naming and decisions for the main session

Names owned elsewhere (a `git grep` of the repo and a byte search of `FlintbornWorldKit.blend`):
- lobby / build_05: `BerryBush` (and `src` NodeCatalog's `BerryBush` node id);
- R05 kit: `BerryShrub`, `BerryShrubBerry`, `BerryShrubBerries`, `BerryShrubDepleted`, `BerryShrubLeafClump`,
  `BerryShrubTrunkFork`, keys `r05_*`;
- V02 kit: `RaspberryBush*`, `RaspberryCane`, `RaspberryLeafCluster`, `RaspberryBerryCluster`,
  `RaspberryLeafUnderside`, `ElderberryShrub*`, `ElderberryForkedStem`, `ElderberryLeafClump`, `ElderberryBerryBunch`,
  `ElderberryLeafUnderside`; V06 `RowanBerryBunch`, `JuniperBerry`.
- `M.mk` would silently rename a clash to `<name>M017`, so avoid them all.

**Proposed names** (none found in the repo or the kit .blend; `m017_` is unused too):

| Object | Part | Why |
| --- | --- | --- |
| `BerryBushNode` | hero | the lobby owns `BerryBush`; matches M014 `StarstoneNode`, M016 `StormglassNode` and the NodeCatalog id |
| `BerryBushTrunkFork` | Trunk Fork (x1) | R05 owns `BerryShrubTrunkFork` |
| `BerryBushLeafClump` | Leaf Clump (x5) | R05 owns `BerryShrubLeafClump` |
| `BerryBushBerry` | Berry (x6) | R05 owns `BerryShrubBerry` |

- Fallback set if the main session prefers a distinct species name: `RedberryBush`, `RedberryTrunkFork`,
  `RedberryLeafClump`, `Redberry` (also free).
- Palette keys `m017_*` (§5.4). Collection `Kit/M017 Berry Bush`.

**Decisions needed:**
1. **Size** (§1.1): 6.0 × 4.8 × 5.0 (recommended; berry 1 stud, between the lobby BerryBush and R05), or smaller
   toward WorldModeling's 0.25–0.65 C (about 3.5 tall, berries 0.7).
2. **Hero skeleton** (§3.1): five stems from one `_trunk` builder, ground-level split (recommended), or the exploded
   fork plus two stems.
3. **Berry count** (§3.3): 8 (recommended: front 6 as drawn, rear as drawn) or 6 (the label).
4. **Lobes** (§3.2): 15 lobes as 5 clump instances of 2–4 lobes (recommended).
5. **Collars in the hero** (§2.1): five small collars where stems enter the clumps (recommended; about 60 tris, shows
   only from below) or none.
6. **Exports:** hero plus `BerryBushTrunkFork`, `BerryBushLeafClump`, `BerryBushBerry` (4 objects, recommended). A
   harvested/fruitless variant is not on the sheet; not built unless asked.
7. **Stage 5/6:** no Neon, no light, no VFX (recommended); or the R05-style `harvest_hit` / `harvest_deplete` pair.
8. **Names** as proposed.

## 9. Pitfalls to avoid

1. **Leaf cards or spiky leaves.** This sheet's foliage is **faceted lobe masses** (WorldModeling §6.4 canopy masses,
   the sheet's "Leaf Clump"), not individual leaves. Don't use `NS["leaf"]` (narrow, serrated, marked down by every
   verifier) or scatter `broad_leaf` cards. Each lobe is a closed, broad, smooth faceted ovoid.
2. **Broccoli balls / identical icospheres** (WorldModeling §6.4, §18). Reshape every lobe (ovoid, offset apex,
   tapered underside, broad pulls), vary sizes 0.8–1.95, keep the stems and the see-through gaps showing.
3. **Per-vertex noise.** It turns lobes into crumpled rocks and berries into jewels. Only broad pulls on lobes, ≤ 2 %
   on berries.
4. **Jewel berries.** Ico-1 (20 faces) reads as a gem; use ico-2 (80), round, squash 0.96.
5. **Floating or perched berries.** Sink each 25–35 % into two or three lobes, in the gaps (§6).
6. **One thick trunk.** The hero has five 0.5-thick stems parting at the ground (§3.1); a single trunk or a Y fork at
   z 1.3 fails the rear and r34.
7. **An opaque green wall.** Keep the canopy's underside open from h 0.2 down (leaf bottom profile §1.2) and two or
   more gaps between stems.
8. **Colour by facing.** Lime tops and green sides are the lighting (§3.11). Paint per lobe and by height only;
   `K.check` facing correlation < 0.5.
9. **Too-dark bark everywhere.** The hero's stem medians are canopy shadow; paint to the unshadowed `#8A5D38` and let
   the studio darken them (§5.4).
10. **Berries too orange, pink or dull.** Hue 0–3°, sat 0.85; the swatch `#E23434` is duller than the render.
11. **Leaves too blue-green or too yellow.** Median hue 76–81°; young lobes 71–74°, old 83–86°.
12. **Glassy or glowing berries.** Opaque, rough 0.3, no emission (§3.10, §7).
13. **Side-view handedness.** The side camera at +X has screen right = +Y (the back), as M016 confirmed. The side's
    front berry (B3) is at screen left.
14. **Comparing the wrong views.** Use the 8° extras for the orthographic profiles; the 3/4 views by shares, counts
    and order, not W : H (§3.8); `top_tilt` plus the kit top for the top (§3.6).
15. **Exact booleans.** Overlap everything: lobes 0.2–0.5 into neighbours, berries 25–35 %, stems 0.3 into clumps and
    into each other at the foot, stems from z −0.2. No coplanar contact. Remove slivers with m011's `_tidy` /
    `_desliver`; keep triangles above 5°, especially where 15 ico spheres intersect.
16. **Stage 2 over-cleaning.** Don't decimate lobes into blobs or stems below 6 sides, and keep the foot's V-creases.
17. **Naming clashes** with the lobby, R05, V02 and V06 (§8). Only one agent drives Blender at a time. No commits,
    pushes or exports in stage agents.

## Decisions (main session, 2026-10-28)

1. **Size.** Follow WorldModeling (the design doc wins over the sheet's implied scale). A forage bush is at most about 0.65 of the 5.5-stud character, so the target is about 4.3 W × 3.5 D × 3.6 H. Scale every proportion measured here uniformly. Berries then come out about 0.65–0.75 across.
2. **Skeleton.** Five stems from one builder. The exported `BerryBushTrunkFork` matches the exploded fork.
3. **Berries.** Eight.
4. **Lobes.** Fifteen, in five clumps.
5. **Collars.** Yes.
6. **Exports.** The bush and three parts.
7. **Effects.** None; skip stages 5 and 6 and record why.
8. **Names.** As proposed: `BerryBushNode`, `BerryBushTrunkFork`, `BerryBushLeafClump`, `BerryBushBerry`.

## Stage 1 — Modelling

Builder `art/blender/kit/mcp/m017.py` (`build()`), run in a background session (`bgmcp.py`, port 9878, work file
`art/blender/assets/kit/wip/M017.blend`). Every table in the builder is in **sheet studs**; each builder scales its
result by `S = 0.70` at the end (decision 1: the hero 3.6 tall; the study's 0.72, less the 0.1 our lobes stand taller).

### Parts (each its own function; the hero uses the same builders)
- `lobe_mesh()`: one ico-2 sphere (80 tris, built in a scratch bmesh and copied in, see stage 2) reshaped: ovoid
  W 1.0 : D 0.9 : H 0.85, sides drawn in below the widest ring (teardrop underside), three broad pulls (±10 % over
  0.75 rad), the pole pushed out 1.2× (the five-facet apex every sheet lobe shows) and turned up and outwards. No
  per-vertex noise.
- `BerryBushLeafClump` (`clump_part`): the exploded three-lobe clump (tall centre lobe, smaller left lobe lower and out,
  right lobe behind) on a flared hex collar with a hex peg. 316 tris, 2.20 × 1.43 × 1.55.
- `BerryBushBerry` (`berry_part`): ico-2 ball (radius jitter ≤ 1.8 %, squash 0.96) and a 6-sided peg on top. 96 tris,
  0.68 across, 0.79 tall with the peg.
- `BerryBushTrunkFork` (`fork_part`): 6-sided trunk (Ø 1.44 → 1.2) to 1.45, three limbs (centre ~10° left to 3.1, right
  ~40° to 2.8, left ~52° to 2.2), ±8 % / ±10° ring jitter, pale heartwood hex cut ends. 202 tris, 2.63 × 1.00 × 2.21.

### Hero `BerryBushNode`
- Five stems (`_tube` along a bent Bézier, 6 sides, Ø 0.72 flare at the ground, 0.62 above, 0.46 at the tip; each
  starts at its own depth below the ground) parting at the foot. Each tip is moved towards its clump until the stem runs
  ≥ 0.35 into it (`_seat`; measured 0.36–0.92). A flared hex collar where each stem leaves its clump (`_entry` marches
  back down the stem with a ray-parity test).
- Fifteen lobes in five clumps (`LOBES`): the study's table, re-laid against the renders (below).
- Eight berries (`BERRIES`): B1, B2, B4 cast in from the front and Bk1, Bk2 from the rear, each dropped onto the canopy
  with a ring of rays (`_drop`, first contact) and sunk 30 % (B4 45 %); B3, B5, B6 at fixed points, pushed along a
  given direction until 22–36 % sunk (`_surface_dist` hold check). Pegs point into the canopy.
- Union: `_union` (one exact boolean per shell, each checked against the volumes going in, undone and retried with a
  small nudge if it throws geometry away), floor cut at z 0, m011 / m012 sliver passes, `_seal`.

### Why the layout moved from the study's table
1. The drawn widths are silhouettes; the lobe mesh is narrower in depth and height and tapers, so at the drawn sizes a
   contact graph of the 41 pieces showed eleven separate groups, and berries showed through from the far side. Every
   lobe grows `LOBE_GROW = 1.18`; L3 / L4 / L11 sit a little further out; L8 is bigger (1.4) and further in (it touched
   only by an edge, which left non-manifold edges).
2. The side view has no leaf below h 0.28 at mid depth, but the front and rear both show low lobes at the sides: L6 and
   L12 moved to the back-left and back-right (Y 1.4–1.5, z 1.35–1.4), where the rear's low lobes are.
3. L7 moved left and smaller, L10 right and smaller (1.75): the front and front three-quarter showed no stem between
   them (the sheet shows stems to h 0.25–0.59 at f 0.45–0.6).
4. Berries typed as 3D centres were either buried by the grown lobes or perched; casting them from their view put the
   front's six at the sheet's (f, h).

### Measured (stage 1 final; the study's masks on both images, `m017.measure()`)
| View | W:H sheet / ours | L / B / T % sheet | L / B / T % ours | Berries |
| --- | --- | --- | --- | --- |
| Front (0, 8) | 1.224 / 1.146 | 66 / 19 / 15 | 72 / 17 / 12 | 6 of 6: (.20,.45) (.36,.59) (.52,.49) (.66,.71) (.91,.63) (.93,.28, partial) against (.17,.45) (.34,.61) (.51,.47) (.69,.78) (.87,.60) (.91,.32) |
| Side (90, 8) | 0.954 / 0.940 | 69 / 17 / 14 | 81 / 13 / 6 | 4: front edge (B3), top-front (B4), mid-low (B6), back-high (B5) |
| Rear (180, 8) | 1.160 / 1.222 | 70 / 8 / 22 | 75 / 11 / 15 | 3: (.09,.60) (.50,.44) (.79,.65) against (.11,.59) (.48,.45) (.78,.71) |
| f34 (−20, 14) | 1.438 / 1.103 | 69 / 17 / 14 | 74 / 17 / 9 | 5 of 6 (B6 hidden) |
| r34 (160, 14) | 1.350 / 1.154 | 66 / 16 / 19 | 78 / 12 / 10 | 5 |
| Top (0, 70) | 1.034 / 1.220 | 82 / 17 / 1 | 82 / 17 / 1 | 7 |

- Front top profile (f 0…1 by 0.05): ours `.39 .51 .67 .71 .71 .70 .89 .93 .96 .99 .98 .94 .91 .88 .78 .79 .79 .71 .68 .64 .46`
  against `.39 .48 .63 .71 .75 .76 .91 .96 .94 .96 1.0 .97 .92 .86 .87 .83 .76 .74 .66 .55 .46` (worst 0.09 at f 0.70).
  Leaf bottom ours `.36 .30 .21 .13 .11 .09 .06 .05 .10 .20 .59 .59 .36 .20 .14 .13 .14 .17 .20 .36 .43` against
  `.36 .27 .24 .15 .10 .12 .16 .09 .09 .25 .57 .56 .34 .29 .28 .16 .12 .10 .14 .38 .43` (worst 0.10 at f 0.30).
- Rear top profile within 0.06 except f 0.05 (0.67 against 0.51: B5 at the left edge); side within 0.06 except the
  front column (our front berry is narrower than the sheet's 0.234 H one).
- Hero 4.50 × 3.33 × 3.66 (target 4.3 × 3.5 × 3.6: W +0.20, D −0.17, H +0.06; all inside ±0.22 / ±0.22 / ±0.18).
- Stems: five, 6-sided, Ø 0.46–0.72; the rear shows all five fanned from the ground, as `z_rear_trunk.png`.

### Left (honest)
- Stems read less in the front and side than on the sheet (T 12 % / 6 % against 15 % / 14 %): the studio sun is high
  and the canopy's cast shadow falls on them, and at mid depth the side lobes hang to h 0.22 (sheet 0.28–0.36).
- The side view shows B4 over the crown and B6 at mid depth where the sheet shows two berries at the back; the sheet's
  side and front disagree on B5 / B6 (spec 3.4) and the front won.
- The sheet's 3/4 cells are drawn wider (spec 3.8); judged by shares and counts.
- Close up, the lobes are a little rounder than the sheet's crisper polyhedra.

## Stage 2 — Optimisation and cleanup

- Tris: hero **2660** (budget 4000); fork 202, clump 316, berry 96 (each under 1000).
- Every object: 1 shell, 0 non-manifold, 0 boundary, 0 wire or loose, 0 n-gons, 0 duplicate verts, normals outward, no
  custom normals, transforms applied, origin at the bottom centre (offset 0, 0, 0).
- Smallest corner: hero 5.22°, fork 7.49°, clump 7.15°, berry 15.09° (none under 5°).
- Self-intersections (face pairs crossing without a shared vertex): 0 on every object. `build()` adds any to `problems`.
- No interior faces: one guarded exact union per shell (41 hero shells, 0 retried, 0 failed; a failure is listed in
  `problems`), pockets dropped.
- Pitfalls met and fixed in the builder: `bmesh.ops.create_icosphere` on a non-empty bmesh invalidated earlier vert
  references (`_ico` builds in a scratch bmesh); five nearly coplanar stem bottom caps made one exact union discard most
  of the hero (stems start at staggered depths); a stem grazing another failed its union at nudges up to 0.02 (the S4
  base moved 0.07); a 4-edge pinhole by B3 whose other diagonal already existed (`_fan_fill`).

## Stage 3 — UV

Smart UV islands made seams and re-unwrapped angle-based, margin 0.008 (`M.smart_uv`, as M013 / M014), then
`m012._uv_unfold`.

| Object | Islands | Overlaps | Flipped | Min gap | Border | Worst conformal | Worst angle change | Texels/stud @1024 |
| --- | --- | --- | --- | --- | --- | --- | --- | --- |
| BerryBushNode | 488 | 0 | 0 | 0.016 | 0.008 | 1.137 | 4.4° | 61.6 |
| BerryBushTrunkFork | 32 | 0 | 0 | 0.016 | 0.008 | 1.091 | 4.0° | 223.6 |
| BerryBushLeafClump | 58 | 0 | 0 | 0.016 | 0.008 | 1.065 | 3.4° | 229.6 |
| BerryBushBerry | 18 | 0 | 0 | 0.016 | 0.008 | 1.082 | 4.1° | 589.3 |

Texel density is even within each object (min / median / max 1.0 / 1.0 / 1.0). The hero's many islands follow the
union's cut lines; the exporter writes its own palette UVs.

## Stage 4 — Materials, colour and texture

### Keys and calibration (`TARGETS`, `calibrate()`, `PALETTE`)
1. `calibrate()` (K.calibrate on the test dome) against the sheet's rendered medians: every key rendered within 3
   levels of its target.
2. Hero fit: the hero rendered darker than the dome (lobe sides and undersides, the canopy's shadow), so the keys were
   corrected in linear light by sheet / hero over the lit views (front, f34, top). The side and rear are lit mostly by
   the studio fill and are reported, not fitted (as M013).

| Key | Target (sheet render) | Dome-calibrated (dome render) | Final (hero fit) | Finish |
| --- | --- | --- | --- | --- |
| m017_leaf | #6B8F22 | #597722 (#698C22) | #638427 (×1.25) | rough 0.85, foliage spec 0.06 |
| m017_leaf_young | #A0C032 | #809C31 (#9CBC32) | #89A635 (×1.15) | same |
| m017_leaf_old | #4E6D1E | #435D1E (#4D6A1E) | #4F6D25 (×1.4) | same |
| m017_berry | #F42524 | #C31617 (#F32524) | #D71A1B (×1.25) | rough 0.32, spec 0.5 |
| m017_berry_deep | #B5161A | #930309 (#B51B1D) | #A3040B (×1.25) | same |
| m017_berry_stem | #865137 | #6A412C (#85523A) | #6A412C | rough 0.9 |
| m017_bark | #8A5D38 | #6E4C2D (#8A5E3B) | #73502F (×1.1) | rough 0.9 |
| m017_bark_dark | #5E4128 | #493119 (#5D422B) | #4D341B (×1.1) | rough 0.9 |
| m017_heartwood | #C3A588 | #998675 (#C1A488) | #998675 | rough 0.85 (fork cut ends only) |
| m017_peg | #584833 | #453928 (#594A37) | #453928 | rough 0.9 (collars, pegs) |

### Method (position fields only, never facing; painted in the builders before the union, which keeps keys and Tint)
- Leaves on one ladder young ↔ leaf ↔ old in quarter steps (`leaf_key`, K.mix_key): per-lobe maturity (young L1, L2,
  L5, L8, L10; mid L3, L9, L13, L14, L15; old L4, L6, L7, L11, L12), a canopy height field (above 4.0 younger, below 1.3
  older, ±0.15 broad noise on z), each lobe's lowest 30 % up to +0.25 older, and 50 % old within 0.25 of a berry or
  where a stem enters.
- Berries: body to berry_deep over the third nearest the peg (the side in the canopy), 3 steps.
- Bark: darker up under the canopy (z > 1.6 → 50 %, > 2.2 → 75 %), in the V-creases (within 0.12 of another stem below
  1.0), at the ground (z < 0.12 → 40 %), plus broad noise patches; floor-cut faces 50 % dark. Fork: noise patches only.
  Hero stem tips are hidden in the clumps and carry no heartwood.
- Tint: per lobe level ±4 %, broad mottling (leaf amp 0.035 scale 0.5, bark 0.05 / 0.35, berry 0.02 / 0.9), per-face
  jitter ≤ 0.6 %. Tint spread: hero 1.13, fork 1.06, clump 1.06, berry 1.03.
- K.check facing correlation: hero 0.27, clump 0.31, fork 0.0, berry 0.0 (limit 0.5). Problems: none.

### Target against got (medians, with lit / shade quartiles on the front)
| View | Leaves sheet → ours | Berries sheet → ours | Bark sheet → ours |
| --- | --- | --- | --- |
| Front | #6F9322 (#A9C72E / #405C19) → #6B8E24 (#98BD33 / #32450F) | #F62624 → #E52625 | #6A4829 → #3B2716 |
| f34 | #709221 → #759A29 | #F82523 → #F82827 | #724C2B → #3C2818 |
| Top | #86AB20 → #7FA42B | #EA2221 → #FD2A29 | — |
| Side | #678B21 → #53731D | #EB2222 → #BB2221 | #5B3E23 → #583B25 |
| Rear | #658923 → #577820 | #F52526 → #D62424 | #6B492A → #66462E |

- Leaf bands on the front (ground → crown): sheet `#4F6E1E #5D8022 #709320 #729520 #9DBE2E`, ours
  `#3C4F15 #799929 #4C641A #688B23 #9FC234` (crown palest, lowest deepest, as the sheet).
- Left: front / f34 bark is 40–50 levels dark (the canopy's cast shadow on the stems in the kit studio; side and rear
  bark match within 6). Side / rear greens are 15–20 dark and berries 20–40 dark (studio fill). The sheet's lit lime
  facets are a little yellower than ours (#A9C72E against #98BD33).

## Stage 5 — Lighting

Skipped, as decided (decision 7, spec 7.1): the sheet shows no glow, and the berry highlights are gloss, not emission.
No key has emission (no Neon pieces) and there is no light. Studio note (Requires Manual Validation): check that the
berries keep a visible gloss in Roblox; if they read matte, set the berry MeshPart material to SmoothPlastic.

## Stage 6 — VFX

Skipped, as decided (decision 7, spec 7.2): the sheet shows no particles, sparkle, dust or falling leaves. No sockets on
any object; the renders ran with vfx=True and realised nothing.

## Stage 7 — Verification (round 1)

Fresh verifier, read-only. Background session on port 9881 with `wip/M017_verify.blend` (not saved, `build()` not
called). Fresh renders via `m017.render_views()` with `M.MODEL_RENDERS` pointed at the verifier's scratchpad
(`...\scratchpad\v017\renders\M017\`), plus side-by-side crops `pair_*.png` there. Measured with `M.audit`,
`M.uv_stats`, `K.check`, `m017.measure()` and my own BVH / bmesh probes.

**Verdict: FAIL, 6/10.** The geometry is clean and inside budget, but two things are visibly unlike the sheet in every
view: how the lobes are faceted, and how the stem skeleton reads.

### Re-measured (all independently)
| Object | Tris | Size (studs) | Shells | Non-manifold / boundary / wire / loose | N-gons | Normals | Min corner | Self-hits | UV (layer / overlaps / flips / margin) |
| --- | --- | --- | --- | --- | --- | --- | --- | --- | --- |
| BerryBushNode | 2660 / 4000 | 4.50 × 3.33 × 3.66 | 1 | 0 / 0 / 0 / 0 | 0 | outward | 5.22° | 0 | UVMap / 0 / 0 / 0.008 (506 islands) |
| BerryBushTrunkFork | 202 / 1000 | 2.63 × 1.00 × 2.21 | 1 | 0 | 0 | outward | 7.49° | 0 | UVMap / 0 / 0 / 0.008 |
| BerryBushLeafClump | 316 / 1000 | 2.20 × 1.43 × 1.55 | 1 | 0 | 0 | outward | 7.15° | 0 | UVMap / 0 / 0 / 0.008 |
| BerryBushBerry | 96 / 1000 | 0.68 × 0.70 × 0.79 | 1 | 0 | 0 | outward | 15.09° | 0 | UVMap / 0 / 0 / 0.008 |

- Size against decision 1 (4.3 × 3.5 × 3.6): W +0.20, D −0.17, H +0.06, all inside the scaled tolerances. Hero berries
  0.60–0.66 across (mesh), 0.62–0.72 in the front render.
- Origin at the bottom centre (offset 0, 0, 0) on all four; rotation 0 and scale 1; no modifiers; no custom normals;
  0 duplicate vertices; 0 zero-area faces.
- Counts: 5 stems, 15 lobes (5 clumps), 8 berry regions on the mesh, collars present (136 peg faces).
- Materials: 18 `FB_m017_*` on the hero, all Principled, metal 0, alpha 1, emission 0. Leaves rough 0.85 / spec 0.06;
  berries rough 0.32 / spec 0.5; wood rough 0.85–0.9. `Tint` corner attribute present on all four.
- VFX: no sockets and no children on any object, as decided (decision 7).
- `K.check`: no problems (this includes the facing-correlation test).
- **Interior / inverted faces:** a five-direction parity test plus a flood-fill cavity test found **3 inside-out faces
  at the stem foot** (indices 2403, 2658, 2659, around (0.25, 0.12, 0.00–0.13)). They form a thin inverted tetrahedral
  fin, about 0.005 thick, standing in the V-crease between two stems; it is what `_seal`'s fan fill left behind.
  Two of the three faces carry `FB_m017_leaf`, which is why the hero's lowest "leaf" vertex is at z 0. There is also one
  micro-pocket face at (0.14, −0.46, 2.38). Total area is about 0.05 stud².

### Views against the sheet (8° extras, `m017.measure()`, the study's masks)
| View | L / B / T % sheet | L / B / T % ours | Berries | Notes |
| --- | --- | --- | --- | --- |
| Front | 66 / 19 / 15 | 72 / 17 / 12 | 6 (B6 a 0.05 H sliver; sheet 0.14) | top profile worst 0.09 (f 0.70) |
| Side | 69 / 17 / 14 | 81 / 13 / **6** | 4 at f .10 / .14 / .44 / .66 (sheet .12 / .77 / .83) | the two back-edge berries are missing; a low berry at mid depth (B6) |
| Rear | 70 / 8 / 22 | 75 / 11 / 15 | 3, positions within 0.06 | 5 stems fanned, good layout |
| f34 | 69 / 17 / 14 | 74 / 17 / 9 | 5 of 6 | leaf bottom 0.02–0.08 H at f 0.3–0.5 (sheet 0.08–0.12, centre 0.59): the stems are hidden |
| r34 | 66 / 16 / 19 | 78 / 12 / **10** | 5 (sheet 6) | leaf bottom 0.03–0.05 at f 0.2–0.35 (sheet 0.14–0.61) |
| Top | 82 / 17 / 1 | 82 / 17 / 1 | 7 (5–7 allowed) | reads as round balls, not the sheet's pointed radiating masses |

### Colours (median; lit / shade quartiles; sheet → ours)
| Region | Sheet | Ours | Δ (R, G, B) |
| --- | --- | --- | --- |
| Leaf, front | #6F9322 (#A9C72D / #3F5C19) | #6B8D24 (#98BD33 / #32450F) | −4, −6, +2 (lit −17, −10, +6) |
| Leaf, f34 / top | #709221 / #86AB20 | #759A29 / #7FA42B | +5, +8, +8 / −7, −7, +11 |
| Leaf, side / rear / r34 | #678B21 / #658923 / #678B23 | #54731D / #577820 / #5A7C21 | −19, −24, −4 / −14, −17, −3 / −13, −15, −2 |
| Leaf, exploded / clump close-up | #618426 / #597C29 | #779C28 / #81AA2B | +22, +24, +2 / +40, +46, +2 (the sheet's cell is an underside view) |
| Berry, front / f34 / top | #F62624 / #F82523 / #EA2221 | #E52625 / #F82827 / #FD2A29 | −17, 0, +1 / 0, +3, +4 / +19, +8, +8 |
| Berry, side / rear / r34 | #EB2222 / #F52526 / #F62625 | #BC2221 / #D62424 / #DB2524 | −47 / −31 / −27 on R (studio fill) |
| Berry part / berry peg | #EB2628 / #875137 | #F32726 / #7F4E37 | +8, +1, −2 / −8, −3, 0 |
| **Bark, front / f34** | #6A4829 / #724C2B | **#3B2716 / #3C2818** | **−47, −33, −19 / −54, −36, −19** |
| **Bark foot band h 0–0.1, front** | #835A34 (the lightest bark band) | **#3B2616** | **−72, −52, −30** |
| Bark, side / rear / r34 | #5B3E23 / #6B492A / #614327 | #583B25 / #67462E / #68492E | −3, −3, +2 / −4, −3, +4 / +7, +6, +7 |
| Bark, fork part / exploded | #8C5F39 / #835B38 | #815735 / #765034 | −11, −8, −4 / −13, −11, −4 |
| Heartwood | #BD9F83 | #CCAD90 | +15, +14, +13 |
| Peg / collar | #554531 | #4B3F31 | −10, −6, 0 |

- Blending: the leaf ladder grades crown (lime) to low lobes (deep) as on the sheet, with no confetti and no colouring by
  facing (K.check passes, and the crown lime follows the height field). The berries grade to deep on the canopy side.
- **The bark paint works against the sheet at the foot.** In the hero, 87 of the 108 bark faces below z 0.25 are
  `bark_x_dark_50` (the "z < 0.12 → 40 % dark" ground term plus "floor-cut faces 50 % dark"). On the sheet, the foot
  band is the lightest bark in every view.

### Items

**Blockers**
1. **Lobe facet read: round geodesic balls instead of the sheet's angular faceted lobes** (every view; worst on the top,
   front and exploded views; spec pitfall 2). Each sheet lobe is a crisp polyhedron: big flat facets, a pronounced
   pointed apex where five facets meet and stand out on the silhouette, and straight ridge lines. Seen from the top they
   read as pointed masses radiating outwards. Ours are ico-2 spheres with every vertex on an ovoid, so they read round
   and soft, and the top view reads as round balls.
   Fix in `lobe_mesh()`, keeping 80 tris per lobe:
   - Build an ico-1 and subdivide it once *flat*, without re-projecting the new mid-edge vertices onto the sphere.
     Push them only 30–50 % of the way out, so that each original ico-1 face reads as one broad, slightly bent facet
     group.
   - Raise `LOBE_APEX` from 1.2 to about 1.45–1.6, so that the apex is a visible peak on the front, side and top
     silhouettes.
   - Give the crown and the clump-centre lobes a taller H (about 0.95–1.0 of W, against 0.85 now), as in the exploded
     top clump.
   - Re-check the exploded clump against `z_expl_topclump.png`: it should be a tall, pointed centre lobe, not three
     squat domes.
   - Re-run the union and polish checks afterwards; the sharper lobes change where they intersect.
2. **The stem skeleton under-reads, and the front stems are near black.** T shares are low in every view: front 12
   against 15, **side 6 against 14, r34 10 against 19**, rear 15 against 22, f34 9 against 14. In the f34 the big low
   front-left lobes hang to 0.02–0.08 H in front of the foot and hide the stems; the sheet shows four or five warm
   brown stems there. Front and f34 bark is 47–54 levels too dark, and 72 too dark at the foot.
   Fix:
   - **(a) Paint.** In `paint_wood` / `BARK_FIELD`, drop the ground-contact darkening (`ground=(0.12, 0.4)`) and the
     50 % dark on the floor-cut faces. Make z < 0.5 plain `bark`, and keep the darkening only for z > 1.6, which is
     under the canopy, and for the V-creases.
   - **(b) Shape.** Raise or tuck in the low front-left lobes (L5, L7) and the side's mid-depth low lobes, so the
     leaf-bottom profile over the stems meets the sheet: f34 at f 0.35–0.6 ≥ 0.10 H with the centre gap open, and side
     at f 0.35–0.7 ≥ 0.28.
   - Targets: T share within ±4 points in the front, side and rear; at least 11 % in the f34 and at least 15 % in the
     r34; foot band (h 0–0.1) within 20 levels of #835A34 in the front and f34.

**Minors**
3. **Inverted fin at the stem foot:** 3 inside-out faces, two of them with leaf material, in the crease at
   (0.25, 0.12, 0–0.13), plus one micro-pocket face at (0.14, −0.46, 2.38).
   - Fix: after `_seal`, delete any face whose front side tests as solid by multi-direction parity (or that a flood fill
     can't reach), then re-seal. Better still, nudge the two stems at that crease so the union never opens a pinhole
     there.
   - Re-test with the parity and cavity probes (expect 0 faces).
4. **B6 is hidden in the front** (0.05 H sliver against the sheet's 0.14 H at f 0.91, h 0.32), and in the side it shows
   at mid depth (f 0.44, h 0.19), not at the back edge.
   - It sits at (1.65, −0.18, 1.0). Move it out and back to about (1.75, +0.55, 1.05), so it shows at the front's right
     edge and as the side's back-low berry (f about 0.77).
   - The side's back-high berry (f 0.83, h 0.67) would then be B5 if B5 sits about 0.2 further out in +Y.
5. **Lit tones.** The lit lime is less yellow than the sheet's (front lit #98BD33 against #A9C72D). The side, rear and r34
   leaves are 13–24 dark and the berries 27–47 dark. Most of this is the studio fill, which is not fixable in paint
   without breaking the front. Note it for the Studio check.
6. **Front top profile** misses by 0.09 at f 0.70 (tolerance 0.06); the other columns are within tolerance.
7. **Parts.** The exploded and part leaves render 22–40 levels lighter than the sheet's exploded and underside cells.
   The fork's left limb leans about 65°, against the sheet's 50–55°. Heartwood is 15 levels pale.
8. **The top view shows 7 berries.** That is within the allowed 5–7; the sheet shows 5.

### What passed
- Technical requirements:
  - budgets;
  - one closed manifold shell per object;
  - no n-gons, no self-intersections;
  - minimum corner angle ≥ 5°;
  - UVs clean;
  - origin and transforms;
  - no emission and no VFX, as decided.
- Counts and layout:
  - 5 stems fanned as in the rear view;
  - 15 lobes in 5 clumps with collars;
  - 8 berries, with the front's six in the sheet's left-to-right order;
  - the rear's three berries within 0.06 of the sheet.
- Size inside tolerance. Colours:
  - leaf and berry medians within about 10 levels on the lit views (front, f34, top);
  - the bark on the parts, side and rear within 13;
  - the colour blends along the height and maturity ladders, never by facing.

## Round 2 fixes (modeller)

A fresh modeller did this round in a background session (port 9879, `wip/M017.blend`), saving after the final good
build.
- The builder `m017.py` is the source of truth. `build()` was rerun after each change (about 40 s each).
- After each build, every render was read view by view, then measured against the sheet with `m017.measure()` and a
  quartile colour probe, both on the study's masks.
- The shared helpers were not touched.

### What changed in the builder
1. **Lobes (blocker 1).**
   - **Mesh.** `lobe_mesh()` now starts from `_ico_flat()`: an ico-1 subdivided once *flat*. That is 80 tris and
     42 verts, the same as before. Its mid-edge verts are pushed only `LOBE_FACET = 0.4` of the way to the sphere, so
     each ico-1 face reads as one broad, slightly bent facet group with straight ridges.
   - **Apex.** The pole is lifted by `LOBE_APEX - 1`, and the lift runs linearly down the five pole facets (each
     pole-to-ring mid vert gets half). This gives a real five-facet pyramid, not a small spike.
   - **`LOBE_APEX = 1.25`, not the suggested 1.45–1.6.** With this linear lift, 1.5 made every lobe a candle-flame
     spike; that was rendered and rejected. The suggested value assumed a pole-only push, with the neighbouring verts
     left on the sphere.
   - At 1.25 the pole facets rise at about 40°, against the plain icosahedron's 32°. The apex shows on the front, side
     and top silhouettes, and in the exploded clump.
   - **Taller lobes.** `TALL = 0.95` (H : W) on the crown and clump-centre lobes (L1, L2, L8, L9, L13, L15) and on the
     part clump's centre lobe.
   - **Taper.** The teardrop taper is softened from 0.42 to 0.30, so the lobes read as polyhedra, not onions.
2. **Stems (blocker 2), paint.**
   - The ground-contact and floor-cut darkening are gone. `_fix_floor` paints the floor cut plain `bark`.
   - Below z 1.1 (sheet studs), a foot ladder runs from a new key, `m017_bark_light`, up to z 0.5, then grades to
     `bark` in thirds by z 1.1. No crease or noise patches are painted there.
   - The under-canopy darkening (z above 1.6 and 2.2) and the V-crease darkening stay above that.
3. **Stems (blocker 2), shape.** All positions are in sheet studs.
   - L5 moved from (−1.2, −1.1, 1.55), Ø 2.05, to (−1.4, −1.0, 1.85), Ø 1.9.
   - L7 moved from (−0.95, −1.1, 0.8) to (−1.2, −0.85, 1.25).
   - L4 moved forward, out of the side view's mid depth, to Y −0.45 and X −2.2.
   - L6 and L12 went up about 0.65 and back or out; L12 is now at (2.35, 1.4, 2.3).
   - L14 went up to z 2.85.
   - L11 moved to (2.1, 0.3, 2.45).
   - L10 shrank to Ø 1.6 at X 1.45, so B6 shows.
   - The crown came down, because the apex adds height:
     - L1 is now at (−0.4, −0.15, 3.7), Ø 2.15, tilt 0.35.
     - L2 went down 0.2.
     - L8 and L9 moved so that clump C3 touches the crown.
   - S3's tip moved so that it seats in L9 through L10, which joins clump C3.
   - Stem radii went up slightly, to (0.38, 0.32, 0.24).
4. **Inverted fin (minor 3).**
   - **Detection.** A new `_inverted()` runs a five-direction majority ray-parity test on a point 2e-3 in front of each
     face.
   - **Repair.** `_polish` deletes any face that test finds and re-seals.
   - **Reporting.** `build()` lists any such face still left under `problems`, along with a hero that has more than one
     shell.
   - **Foot.** A low hexagonal `FOOT_PLUG` frustum fills the inner V-creases at the ground. S3's base moved from
     (0.45, −0.2) to (0.42, −0.25): at the old base, the union left a three-face crossing fin standing on the floor cut.
   - **Result.** 0 inverted or interior faces and 0 self-intersections.
5. **Berries.**
   - **B6.** Started at (2.75, 0.6, 1.6) and held by L11 and L12. It ends at (2.73, 0.61, 1.62), which is kit
     (1.91, 0.43, 1.13); the suggested position was (1.75, 0.55, 1.05).
   - **B5.** Started at (2.35, 0.9, 3.7), on the right shoulder; it ends at (2.27, 0.9, 3.66).
   - **Others.** B1, B2 and B4 were re-aimed. B3 was pushed forward (hold 0.15) for depth. Bk1 was re-placed between
     L14 and L15.
   - **Contact check.** On the first try Bk1 ended as a floating interior shell. Since then, a contact graph of the 41
     pieces is checked before each build.
6. **Parts (minor 7).**
   - The fork's left limb tip is now (−1.5, −0.05, 2.25), no longer leaning toward the camera. It measures about 49°
     from vertical in the part shot; round 1 measured about 65°, and the sheet shows 50–55°.
   - The part clump's maturities changed from (−0.5, 0, 0.25) to (0.5, 0.75, 1.0).
   - `m017_heartwood` changed from #998675 to #8E7B6A.

### Final numbers (hero 8° extras; sheet → ours)
| View | L / B / T % sheet | L / B / T % ours | Round 1 T | Berries |
| --- | --- | --- | --- | --- |
| Front | 66.4 / 18.9 / 14.7 | 65.4 / 17.5 / **17.1** | 11.5 | 6 (detail below the table) |
| Side | 69.4 / 17.0 / 13.6 | 75.0 / 14.2 / **10.8** | 6.0 | 3: front edge (.12, .55), back-low (.60, .20), back-high (.66, .70); sheet (.12, .53), (.77, .28), (.83, .67) |
| Rear | 69.5 / 8.3 / 22.1 | 66.3 / 12.6 / **21.1** | 14.9 | 4 (B6 shows low left; sheet 3) |
| f34 | 68.9 / 17.3 / 13.8 | 69.5 / 15.8 / **14.6** | 9.3 | 4 components (B1 and B2 overlap) |
| r34 | 65.6 / 15.6 / 18.8 | 71.3 / 13.2 / **15.5** | 10.4 | 5 |
| Top | 81.8 / 16.9 / 1.3 | 80.2 / 18.3 / 1.5 | 0.8 | 6 (5–7 allowed) |

- **Front berries.** Ours: (.15, .45), (.32, .59), (.53, .48), (.69, .77), (.89, .72, partial) and (.95, .35, partial,
  w .10). Sheet: (.17, .45), (.34, .61), (.51, .47), (.69, .78), (.87, .60) and (.91, .32, w .14).
- **Trunk shares.**
  - Front, side and rear are inside ±4 points.
  - f34 is 14.6, against the asked 11 or more.
  - r34 is 15.5, against the asked 15 or more.
- **Leaf bottom.**
  - f34 at f 0.35–0.60: .12 .11 .12 .15 .21 .53. The ask was 0.10 or more; the centre gap is open from f 0.55.
  - Side at f 0.35–0.70: .21 .26 .29 .31 .27 .29 .30 .30. Three columns miss the asked 0.28 or more: f 0.35, 0.40 and
    0.50 read .21, .26 and .27. The sheet itself reads .18 and .11 at f 0.35 and 0.40.
- **Front top profile.**
  - f 0.70 now reads .85 against .87 (round 1: .78).
  - Three columns are still outside ±0.06: f 0.35 (.89 against .96), f 0.85 (.81 against .74) and f 0.90 (.77 against
    .66). The f 0.90 miss is B5, which now sits on the right shoulder so that the front can show it.
- **Stem foot band (h 0–0.1).**
  - Front: #815530 against #835A34 (−2, −5, −4).
  - f34: #815531 against #8C5D35 (−11, −8, −4).
  - Round 1 was 72 levels dark.
  - Side: #7D5432 against #77502E.
  - Rear and r34 now read lighter than the sheet (+28 and +43).
- **Stem medians.**
  - Front and f34 are #52351E against #6A4829 and #724C2B: −24 and −32 (round 1: −47 and −54).
  - Side is +22, rear +11, r34 +26.
  - The kit studio's canopy shadow falls on the front stems and not on the back ones. Without painting by facing, the
    foot ladder is the compromise: the front and f34 foot are on target, and the back views come out a little light.

### Colour (two passes)
- **Pass 1** (measured on the new shape) changed four things:
  - `leaf_young` went from #89A635 to **#95AD2F**. That closes about 70 % of the lit-quartile miss, per channel in
    linear light, averaged over front, f34 and top.
  - `bark_light` is **#986A40** (bark × 1.85 in linear light), fitted to the front and f34 foot band.
  - `heartwood` is **#8E7B6A**.
  - The part clump's maturities changed, as above.
- **Pass 2** re-measured and changed no key:
  - Leaf medians are front +1 / +3 / +3, f34 +7 / +9 / +8 and top −12 / −12 / +9 (R / G / B). They straddle zero, so
    moving the mid key would trade one lit view for another.
  - Berry R is front −17, f34 +4 and top +21.

| Region | Sheet | Ours |
| --- | --- | --- |
| Leaf, front (shade / median / lit) | #3F5C19 / #6F9322 / #A9C72D | #384B0F / #709625 / #A1C02E (lit was #97BC32) |
| Leaf, f34 / top median | #709221 / #86AB20 | #779B29 / #7A9F29 |
| Leaf, side / rear / r34 median | #678B21 / #658923 / #678B23 | #55741E / #5A7C21 / #5B7E21 (studio fill, as in round 1) |
| Leaf bands, front (ground → crown) | #4F6E1E #5D8022 #709320 #729520 #9DBE2E | #384A11 #709523 #4A5D16 #749A27 #ABCA2F |
| Berry, front / f34 / top | #F62624 / #F82523 / #EA2221 | #E52524 / #FC2927 / #FF2B29 |
| Leaves, exploded | #618426 | **#5E8024** (round 1: #779C28) |
| Leaves, part clump (the sheet cell is an underside view) | #597C29 | #678B27 (round 1: #81AA2B) |
| Bark, fork part | #8C5F39 | #815735 |
| Heartwood | #C3A588 (verifier's #BD9F83) | **#B99C81** (round 1: #CCAD90) |
| Berry part | #EB2628 | #F32726 |

- **Final palette:** leaf #638427, leaf_young #95AD2F, leaf_old #4F6D25, berry #D71A1B, berry_deep #A3040B, berry_stem
  #6A412C, bark #73502F, bark_dark #4D341B, **bark_light #986A40**, heartwood #8E7B6A, peg #453928.
- **How colour is placed:** by position only (lobe maturity, canopy height, berry and stem contact, the bark height
  ladder), plus broad Tint mottling. `K.check`, which includes the facing-correlation test, is clean.

### Checks (independently re-run on the saved file)
| Object | Tris | Size | Shells | NM / bnd / wire / loose | N-gons | Min corner | Self-hits | Inverted | UV |
| --- | --- | --- | --- | --- | --- | --- | --- | --- | --- |
| BerryBushNode | 2600 / 4000 | 4.33 × 3.44 × 3.65 | 1 | 0 / 0 / 0 / 0 | 0 | 5.05° | 0 | 0 | 495 islands; 0 overlaps, 0 flips; border 0.008; gap 0.016; conformal ≤ 1.10 |
| BerryBushTrunkFork | 206 / 1000 | 2.55 × 1.00 × 2.21 | 1 | 0 | 0 | 6.93° | 0 | 0 | 34 islands, clean |
| BerryBushLeafClump | 330 / 1000 | 2.16 × 1.41 × 1.68 | 1 | 0 | 0 | 5.12° | 0 | 0 | 63 islands, clean |
| BerryBushBerry | 96 / 1000 | 0.68 × 0.70 × 0.79 | 1 | 0 | 0 | 15.09° | 0 | 0 | 18 islands, clean |

- **Hero size** against the decided 4.3 × 3.5 × 3.6: +0.03, −0.06, +0.05.
- **All four objects:** normals outward, transforms applied, origin at the bottom centre, no modifiers, 0 duplicate
  verts.
- **`K.check`:** no problems.
- **Hero union:** 41 shells, none failed.

### Left (honest)
- **Studio lighting differs from the sheet's.**
  - The side, rear and r34 leaves are 11–23 levels dark.
  - Their berries are 30–48 levels dark.
  - These are the same gaps as in round 1.
  - Stem tone differs by about 50 levels between the front and the back views.
- **Side.** It still reads leafier than the sheet: L 75 against 69, because its low back lobes fill in at mid depth.
- **Rear.** It shows B6 as a fourth berry, so B is 12.6 against 8.3.
- **Front.** B5 and B6 show only partly: 0.08 and 0.10 H wide, against the sheet's 0.14.
- **The stem-foot union is fragile.**
  - Moving S3's base by 0.03 brought a crossing fin back.
  - Both the inverted-face test and the self-hit test run in `build()`, so a regression shows under `problems`.

## Stage 7 — Verification (round 2)

Fresh verifier (not the round-1 verifier, no other stage), read-only. Background session on port 9880 with
`wip/M017_verify.blend` (the main session's copy after its rebuild; not saved, `build()` not called, session stopped).
Fresh renders via `m017.render_views()` with `M.MODEL_RENDERS` pointed at the verifier's scratchpad
(`...\scratchpad\v017r2\renders\M017\`), side-by-side crops `pair_*.png` there. Measured with my own bmesh / BVH
probes (`geo.py`: 7-direction parity, front and behind tests, shells, corners, self-hits, volume), `M.uv_stats`,
`K.check`, `m017.measure()` and a quartile colour probe on the study's masks (`col.py`), plus a facing-correlation
test on the painted keys (`face.py`).

**Verdict: FAIL, 7/10 — one cheap blocker.** Both round-1 blockers are fixed: the lobes are now broad-faceted polyhedra
with visible five-facet peaks, and the stems read warm and show in every view (T shares inside tolerance). The one
remaining clear miss is the berries on the right side: the sheet's headline front three-quarter shows six berries, ours
four.

### Re-measured (all independently)
| Object | Tris | Size (studs) | Shells | NM / bnd / wire / loose | N-gons | Zero-area | Dup verts | Min corner | Self-hits | Volume | UV (islands / overlaps / flips / border / gap / worst conformal) |
| --- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- |
| BerryBushNode | 2600 / 4000 | 4.333 × 3.440 × 3.653 | 1 | 0 / 0 / 0 / 0 | 0 | 0 | 0 | 5.05° | 0 | +10.64 | 495 / 0 / 0 / 0.008 / 0.016 / 1.10 |
| BerryBushTrunkFork | 206 / 1000 | 2.550 × 1.003 × 2.213 | 1 | 0 | 0 | 0 | 0 | 6.93° | 0 | +1.23 | 34 / 0 / 0 / 0.008 / 0.016 / 1.09 |
| BerryBushLeafClump | 330 / 1000 | 2.165 × 1.415 × 1.680 | 1 | 0 | 0 | 0 | 0 | 5.12° | 0 | +1.26 | 63 / 0 / 0 / 0.008 / 0.016 / 1.07 |
| BerryBushBerry | 96 / 1000 | 0.679 × 0.703 × 0.790 | 1 | 0 | 0 | 0 | 0 | 15.09° | 0 | +0.15 | 18 / 0 / 0 / 0.008 / 0.016 / 1.08 |

- **Size** against decision 1 (4.3 × 3.5 × 3.6): +0.03, −0.06, +0.05. Hero berries 0.63–0.67 across.
- **Origin and transforms:** origin at the bottom centre (offset 0, 0, 0) on all four; rotation 0, scale 1; no
  modifiers, no custom normals, flat shading, no parents or children. Texel density even (1.0 / 1.0 / 1.0).
- **Normals and interior faces:** positive volume on all four. Behind every face is solid (0 failures). A point 2 mm in
  front of each face is outside on all four (**0 inverted or interior faces; the round-1 fin is gone**).
  - At 6 mm, four hero faces test inside: 1767, 1993, 2083 and 2579, each ≤ 0.0024 stud².
  - They are not inverted. Each sits in a folded crevice (dihedral −167° to −174°), and a ray along its normal hits the
    opposite wall 3.5–6 mm away, which faces back at it (dot −0.94 to −0.995). These are union creases where two lobes
    meet, or a lobe meets a berry, at (−0.87, −0.90, 1.90), (1.17, 0.96, 1.83) and (0.11, −1.10, 1.90). They can't be
    seen. Info only.
- **Materials:** 22 `FB_m017_*` Principled materials (21 on the hero), metal 0, alpha 1, emission 0.
  - Leaves: roughness 0.85, specular 0.06.
  - Berries: roughness 0.32, specular 0.5.
  - Wood: roughness 0.85–0.9.
  - `Tint` corner attribute on all four (hero range 0.92–1.07).
  - Palette: leaf #638427, leaf_young #95AD2F, leaf_old #4F6D25, berry #D71A1B, berry_deep #A3040B, berry_stem
    #6A412C, bark #73502F, bark_dark #4D341B, bark_light #986A40, heartwood #8E7B6A, peg #453928.
- **`K.check`:** no problems. VFX: none and no sockets, as decided.
- **Facing (my own test).** I correlated the painted key luminance with face normal z: leaves 0.19, bark 0.20, berries
  −0.04. The colour follows height instead: leaves +0.44, bark −0.83. **No colouring by facing.**

### Round-1 items
| # | Round-1 item | Status | Evidence |
| --- | --- | --- | --- |
| 1 | Lobes round geodesic balls (blocker) | **Fixed** | Broad flat facets with straight ridges and a visible five-facet peak on every lobe, in the front, side, rear and top. The exploded clump has a tall pointed centre lobe. Residual minor 6. |
| 2 | Stems under-read and near black (blocker) | **Fixed** | T share (sheet / ours): front 14.7 / 17.1, side 13.6 / 10.8, rear 22.1 / 21.1, f34 13.8 / 14.6, r34 18.8 / 15.5 (all inside the asks). Foot band h 0–0.1: front #835A34 → #815530 (−2, −5, −4); f34 #8C5D35 → #815531 (−11, −8, −4). Five stems fanned in the rear and r34. Residual minor 3. |
| 3 | Inverted fin at the foot | **Fixed** | 0 faces by parity at 2 mm; behind test clean. |
| 4 | B6 hidden in the front / mid-depth in the side | **Partly** | Front: (.95, .35), w .097, against (.91, .32), w .14. Side back-low: f .60 against .77. See blocker 1. |
| 5 | Lit tones | **Front fixed; side and rear as before** | Front lit leaf #A9C72D → #A1C02E (−8, −7, +1). Side, rear and r34 leaves are 11–18 dark at the median (studio fill). |
| 6 | Front top profile at f 0.70 | **Fixed** | .85 against .87. New misses: f .85 +.07 and f .90 +.11 (B5 on the shoulder), f .35 −.07. |
| 7 | Parts | **Fixed** | Exploded leaves #618426 → #5E8024 (−3, −4, −2). Fork left limb about 50°. Heartwood #C3A588 → #B99C81 (−10, −9, −7). |
| 8 | Top shows 7 berries | **Fine** | 6 (5–7 allowed; sheet 5). |

### Views against the sheet (8° extras; the study's masks; sheet → ours)
| View | W : H | L / B / T % | Berries (f, h, w) | Notes |
| --- | --- | --- | --- | --- |
| Front | 1.224 → 1.123 | 66 / 19 / 15 → 66 / 17 / 17 | 6: (.15,.45) (.32,.59) (.53,.48) (.69,.77) all full; **(.89,.72) w .077 and (.95,.35) w .097**, against the sheet's (.87,.60) w .14 and (.91,.32) w .14 | Top profile ±.07 except f .90 (+.11). The skirt is higher: leaf bottom .17–.20 at the sides (sheet .10–.15), width at h .1 .29 (sheet .68). |
| f34 (−20, 14) | 1.438 → 1.040 (drawn wider, spec 3.8) | 69 / 17 / 14 → 70 / 16 / 15 | **4 of 6**: B1, B2, B3, B4. **B5 and B6 are not visible**; on the sheet both sit prominently at the right edge (.86, .62) and (.89, .34). | Stems warm and well shown; centre gap open. |
| Side | 0.954 → 0.977 | 69 / 17 / 14 → 75 / 14 / 11 | 3: front edge (.12, .55) OK; back pair at f .60 / .66 (sheet .77 / .83) | Known sheet conflict (spec 3.4). |
| Rear | 1.160 → 1.217 | 70 / 8 / 22 → 66 / 13 / 21 | 4 (sheet 3): an extra low-left berry (B6 from behind, (.10, .27), w .17); R1 at (.14, .71), w .15 (sheet .07 partial) | Five fanned stems, good. B is 4.3 points over. |
| r34 (160, 14) | 1.350 → 1.186 | 66 / 16 / 19 → 71 / 13 / 16 | 5 (sheet 6) | The lobes hang a little higher than the sheet's (more bare stem). |
| Top (0, 70) | 1.034 → 1.151 | 82 / 17 / 1 → 80 / 18 / 2 | 6 | A big lime crown in the middle with smaller masses around it. Reads less as six big radiating masses than the sheet. |

Parts against their cells: the clump has three lobes, a dark collar and a hex peg; the berry is round and faceted with a
top peg; the fork has six-sided limbs and pale hex cut ends. All match.

### Colours (sheet → ours; Δ R, G, B; median, with the lit and shade quartiles where they tell something)
| Region | Sheet | Ours | Δ |
| --- | --- | --- | --- |
| Leaf, front (shade / median / lit) | #3F5C19 / #6F9322 / #A9C72D | #384A0F / #709525 / #A1C02E | −7,−18,−10 / +1,+2,+3 / −8,−7,+1 |
| Leaf, f34 (shade / median / lit) | #3F5C18 / #709221 / #ADC92E | #4B6216 / #779B29 / #A9C82F | +12,+6,−2 / +7,+9,+8 / −4,−1,+1 |
| Leaf, top median / lit | #86AB20 / #B6D025 | #7A9F29 / #ABC930 | −12,−12,+9 / −11,−7,+11 |
| Leaf, side / rear / r34 median | #678B21 / #658923 / #678B23 | #55741E / #5A7C21 / #5C7E21 | −18,−23,−3 / −11,−13,−2 / −11,−13,−2 |
| Leaf bands, front (ground → crown) | #4F6E1E #5D8022 #709320 #729520 #9DBE2E | #384A11 #6F9523 #4A5D16 #749A27 #ABC92F | crown palest, lowest deepest, as on the sheet |
| Berry, front / f34 / top median | #F62624 / #F82523 / #EA2221 | #E52524 / #FC2927 / #FF2B29 | −17,−1,0 / +4,+4,+4 / +21,+9,+8 |
| Berry, side / rear / r34 median | #EB2222 / #F52526 / #F62625 | #BB2322 / #D32525 / #D82625 | −48 / −34 / −30 on R (studio fill) |
| Berry, lit quartile, front | #FD6560 | #FF514E | +2,−20,−18 (a little less pink sheen) |
| Bark, front / f34 median | #6A4829 / #724C2B | #52351E / #52351E | −24,−19,−11 / −32,−23,−13 |
| Bark, band h 0.2–0.3, front / f34 | #543A22 / #664628 | #3C2718 / #432D1C | −24,−19,−10 / −35,−25,−12 |
| Bark, side / rear / r34 median | #5B3E23 / #6B492A / #614327 | #714E30 / #765233 / #7B5535 | +22,+16,+13 / +11,+9,+9 / +26,+18,+14 |
| Bark, fork part | #8C5F39 | #825835 | −10,−7,−4 |
| Leaves, exploded / clump close-up | #618426 / #597C29 | #5E8024 / #678B27 | −3,−4,−2 / +14,+15,−2 |
| Berry part | #EB2628 | #F32726 | +8,+1,−2 |
| Heartwood | #C3A588 | #B99C81 | −10,−9,−7 |
| Peg / collar (close-up) | #554531 | #4B3F31 | −10,−6,0 |

Medians are within about 10 levels on the lit views (front, f34, top). The side and rear gaps are the kit studio's fill,
not paint. The paint blends along the maturity and height ladders; there's no confetti.

### Items

**Blockers**
1. **B5 and B6 hardly show on the front-right; the f34 shows four berries, the sheet six.**
   - **Front:** both are slivers, w .077 and .097 against .14. B5 also sits high on the shoulder (h .72 against .60),
     which causes the f .90 top-profile miss.
   - **f34:** both are invisible, which leaves the right half of the hero three-quarter without berries.
   - **Rear:** the same two show too much. B6 is an extra fourth berry at the low left, and B5's R1 is 0.15 wide against
     the sheet's 0.07 partial.
   - **Cause:** both sit at Y +0.6 to +0.9 (sheet studs), behind the right lobes.
   - **Fix (two entries in `BERRIES`, sheet studs):**
     - B5: start about (2.4, 0.3, 3.3) instead of (2.35, 0.9, 3.7).
     - B6: start about (2.7, 0.0, 1.75) instead of (2.75, 0.6, 1.6).
     - Keep their push axes and holds, so each still ends 25 % sunk between L9 / L11 and L10 / L11 / L12.
   - **Targets:**
     - front: B5 near (.87, .60) and B6 near (.91, .32), each ≥ 0.12 H wide;
     - f34: 6 berry components;
     - rear: 3 berries, B ≤ 10 %.
   - **Trade-off:** the side's back pair moves a little further from the sheet's back edge (already a known spec 3.4
     conflict).
   - **After the fix:** re-run `build()` and confirm that `problems` is empty, the hero is 1 shell and the inverted count
     is 0. The union at the foot is fragile, but these berries are far from it.

**Minors** (record; don't block)
2. **Front skirt.** The side lobes end higher than the sheet's: leaf bottom .17–.20 at f .15–.35 and .75–.90, against
   .10–.15; width at h .1 is .29 against .68. Ours reads a little more like a small tree on stems than the sheet's full
   shrub. This is the cost of round 1's "show the stems" fix. If wanted, drop L6 / L12 or L4 by about 0.2 at the outer
   edges only; leave the centre gap.
3. **Upper stems dark in the front and f34.** The h 0.2–0.3 band is 24–35 dark, and the medians are 24–32 dark. The
   back views are 11–26 light. This is the studio's canopy shadow against no facing paint. A paint-only nudge (raise
   `BARK_FIELD` z thresholds from 1.6 / 2.2 to about 2.0 / 2.6) would trade some back-view lightness for it. Optional.
4. **Studio fill.** The side, rear and r34 leaves are 11–23 dark and their berries 30–48 dark, as in round 1. This is for
   the Studio check, not paint.
5. **Top view.** It reads as a big lime crown with smaller masses around it, rather than the sheet's six big, pointed,
   radiating masses. Counts and spread are OK.
6. **Lobe peaks.** The crown lobe L1 and a few side lobes come to a slightly sharp, onion-like point in the front and side
   silhouettes, where the sheet's peaks are a little lower and broader. Acceptable at this view size.
7. **Four tiny crevice faces** (≤ 0.0024 stud², gaps of 3.5–6 mm in union creases) test inside at 6 mm. They are
   correctly oriented and not visible. Info only.

### What passed
- All of 2c, re-measured:
  - budgets: 2600 / 206 / 330 / 96;
  - one closed manifold shell per object;
  - no n-gons, no zero-area faces, no duplicate verts;
  - no self-intersections, no inverted or interior faces;
  - minimum corner angle ≥ 5°;
  - UVs clean and even;
  - origin at the bottom centre, transforms applied;
  - Principled materials with the right finishes, `Tint` present;
  - no emission and no VFX, as decided.
- Size inside tolerance. The lobes are angular and faceted with visible peaks. The stems are warm at the foot, five fanned.
  15 lobes in 5 clumps with collars; 8 berries.
- Colours on the lit views are within about 10 levels. Colour blends by position, never by facing.

## Main session after verification round 2 (2026-10-28)

Applied the round-2 blocker fix: B5 starts at (2.4, 0.3, 3.3) and B6 at (2.7, 0.0, 1.75); push directions and sink are unchanged. The rebuild in the kit file gave a hero of 2596 tris, 4.31 × 3.44 × 3.65, one shell, 0 non-manifold, and an empty `problems` list. `f34_sheet` now shows 5 berries (4 full, 1 at the right edge) against the sheet's 6; `rear_sheet` shows 3. Export: 4 assets, 0 problems. The 2-round cap is reached, so this is committed with the minors in MODEL_PROGRESS.md.
