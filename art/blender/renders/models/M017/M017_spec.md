# 017 Berry Bush — spec

Reference: `art/blender/assets/references/017.png` (BERRY BUSH, "Shrub / Nature / Flintborn Style", "Individual Model
Study", footer "PAGE 17/132"; INDEX.md lists it as 17, "Flintborn Berry Bush Study"; 1024 × 1536 px).
Builder: `art/blender/kit/mcp/m017.py` → `build()` (not written yet). Procedure: `art/blender/kit/mcp/STAGES.md`.

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
