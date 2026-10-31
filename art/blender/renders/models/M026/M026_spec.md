# 026 Softwood Log — spec

Reference: `art/blender/assets/references/026.png`. The sheet's own title is "SOFTWOOD LOG", subtitle "ENVIRONMENT
ASSET / NATURE / WOODLAND MATERIALS", header "PAGE 21/132" and "FLINTBORN — INDIVIDUAL MODEL STUDY". INDEX.md row 26
calls it "Flintborn softwood log study". The image is 1024 × 1536 px.
Builder: `art/blender/kit/mcp/m026.py` → `build()` (not written yet). Procedure: `art/blender/kit/mcp/STAGES.md`: one
modeller does stages 1–6 in a background Blender, then a fresh verifier does stage 7.

User direction for every model: shapes must match the sheet; colours "need to match the master reference and blend
into the colors nearby. please ensure all color and textures are being made and applied." Effects ship wherever the
sheet shows them. **This sheet shows no effect** (§7).

Sheet text:
- **Header:** "A fallen softwood log with branch stubs and leaves. Stylized, low-poly and chunky to match FLINTBORN's
  visual language. Clean shapes, broad flat-shaded faces, simple solid colors, no texture noise."
- **Model notes:**
  - "Built from simple, reusable low-poly parts."
  - "Broad, flat-shaded faces."
  - "Clean, readable silhouette."
  - "Separate mesh parts for log, branch stubs, cut-end and leaf clumps."
  - "Consistent style, scale and palette with FLINTBORN woodland materials."
  - "Keep geometry simple and game-friendly."
- **Palette:** Cut Wood (Light), Bark Wood (Medium), Leaves (Green).
- **Exploded labels:** Cut-End Insert, Main Log (Trunk), Branch Stub (Large), Branch Stub (Small), Leaf Clump A, Leaf
  Clump B.
- **Close-ups:** "Cut-End Detail" ("Cut Face (Flat Shaded)", "Slight Bevel (Chamfer)"); "Branch Stub Junction"
  ("Branch Stub (Angled Placement)", "Clean Junction (Shared Faces)"); "Underside View" ("Underside (Closed
  Geometry)").
- **Game context:** `src` has no log node (NodeCatalog has `Tree`, look 3 × 14 × 3). The old R06 kit sheet has
  `SoftwoodLog` (hero 15.3 × 8.4 × 14.4 yawed, main log 15.1 long × Ø 5.5, 688 tris, `harvest_hit` +
  `harvest_deplete`), which owns the `SoftwoodLog*` names (§8). Camp sheet 06 has `FallenLog` 9 × 3 × 2.6 and
  `CutLog` 8 × 2.4 × 2.4.

**Pixel boxes and masks.** All pixel boxes are sheet pixels `(x0, y0, x1, y1)`, origin top left. The paper is
`#F1EDE5` (241, 237, 229). View boxes `V` (in `m.py`): f34 (15,176,540,470), r34 (545,176,1010,470), front
(12,540,290,730), side (290,540,508,730), rear (508,540,768,730), top (768,540,1012,730); exploded (15,750,805,1240);
close-ups cut end (15,1290,370,1520), junction (375,1290,700,1520), underside (705,1290,1010,1520). The masks are
`cls()` in `m.py` (HSV):
- **L, leaves:** sat ≥ 0.30, hue 62–160°, g > 50.
- **W, cut wood:** hue 24–52°, sat 0.12–0.58, v ≥ 0.78 (cut faces, stub tops, the knot tip).
- **B, bark:** sat ≥ 0.18, hue ≤ 45° or ≥ 340°, v < 0.78. Includes the stubs, the knot and the thin bark rim round
  the cut face.
- **O, other:** ground shadow, dark bark slits, text; not counted in the shares.

**Scratch study material** (pure Python, numpy + Pillow, no Blender), in
`<temp>\3f83a1be-3b3d-4e4b-ae5a-7b04dbb75bdc\scratchpad\m026_study\`.
Run with `...\scratchpad\venv22\Scripts\python.exe`.
- **Helpers:** `m.py` (masks, view boxes `V`, `label()` connected components), `bb.json` (silhouette boxes).
- **Measurements:** `measure.py` (bboxes, shares, mask previews `cls_*.png`); `comps.py` (cut-face and clump
  components per view); `prof.py` (top/bottom profiles, width per height); `rings.py` (radial ring bands on every cut
  face); `outline.py` (cut-face outline radius by angle, corner count); `rim.py` (bark rim thickness); `cracks.py`
  (dark bark slits); `edge.py` (top-line straightness); `leafrad.py` (leaf base → tip, leaf count).
- **Colour:** `sw.py` (swatch rows), `samp.py` (swatches, views, height bands, exploded parts, close-ups), `dec.py`
  (deciles, stub-end bands).
- **Names:** `blendall.py` (every sheet .blend, zstd-decompressed).
- **Crops:** `f34.png`, `r34.png`, `front.png`, `side.png`, `rear.png`, `top.png`, `expl.png`, `cu_cut.png`,
  `cu_junc.png`, `cu_under.png`, `pal.png`; zooms `z_f34_stubL.png`, `z_f34_stubS.png`, `z_f34_cut.png`,
  `z_f34_far.png`, `z_f34_body.png`, `z_f34_leaf*.png`, `z_top.png`, `z_side.png`, `z_rear.png`, `z_r34_top.png`,
  `z_r34_left.png`, `z_expl_*.png`, `z_under.png`.
- **To run the scripts on our renders,** point `R` (in `m.py`) at the render, set `P` to its background colour and
  re-run `measure.py` (it rewrites `bb.json`), then `prof.py` / `comps.py`.

## 1. Study (2a)

### 1.1 Classification, what it is, size

- **Classification:** full asset (a resource node / world prop). Hero budget 4000 tris, each part under 1000. The plan
  in §4.3 lands at about 1700–2200.
- **Overall read (check this first).** One fallen softwood log lying on the ground:
  - a long, chunky **11-sided bark log** (L : D ≈ 2.9), its bark broken into long irregular **plates** with dark
    step-slits between some of them; it is **not** a smooth cylinder;
  - **one pale ringed cut end** at −X (the end facing the hero camera), inside a thin bark rim with a slight chamfer;
    the other end (+X) is a **closed, blunt, rounded bark end** (no cut face);
  - a **large branch stub** standing up out of the log's top just past the middle, leaning toward +X and slightly
    back, with a pale broken top, and a **small knot nub** at its −X foot;
  - a **small branch stub** growing out of the log's lower front, angling forward and toward +X, its pale cut end
    resting on the ground;
  - **four bright leaf clumps** (six-leaf flat stars): two on the ground in front (near each end), one on the log's
    top-back near +X, one on the ground behind the log (hidden in the hero).
  - Hero shares: bark 74 %, cut wood 15 %, leaves 11 %.
- **Focal silhouettes, in order:**
  1. The cut end: an 11-gon (radius ±5 %) with a dark pith, a light band, a dark ring and a wide light outer band.
  2. The large stub's diagonal against the sky, with its pale top.
  3. The log's long body with plate facets and slits; the blunt rounded far end.
  4. The small stub running down to the ground, with its pale end facing the camera.
  5. The leaf clumps' broad pointed kite leaves (6 per clump).
- **Target size: about 9.4 W × 6.7 D × 5.05 H studs**; log Ø 3.2 (R 1.6), length 9.3 (cut plane to dome tip).
  H = 0.92 of the 5.5-stud character (the stub top); the log top is at 3.2 (0.58 C, hip height). Tolerances W ±0.35,
  D ±0.5 (the hidden back clump is uncertain, §3.5), H ±0.25. Decision §8.1.
  - **How it was derived.** The sheet has no character. Anchors:
    - **Log proportions** (measured): L : D 2.82 (front cell), 2.96 (rear), 2.8 (f34 with its perspective); 2.9
      recommended. H : D = 1.60 (f34 269 / 168 px), 1.58 (front), 1.62 (rear).
    - **Leaves:** hero clump spans are 0.43–0.6 of the local log Ø (FL 0.43, BR 0.58, FR 0.6 in the top view), so at
      D 3.2 the spans are 1.4–2.0 and a leaf is about 0.7–1.0 long, in line with M018–M020 (leaf L 0.85–1.1).
    - **Gameplay:** a chop-height log (hip-high), between camp `FallenLog` (Ø 2.6–3) and the M020 stump (cut face
      Ø 3.6). R06's `SoftwoodLog` (Ø 5.5, 15 long) is a character-tall log; too big for a fallen softwood log.
- **Build frame:** log axis along X at y 0, z R; cut-face plane at x −4.65, dome tip at x +4.65; front −Y, ground
  z 0. Positions along the log are given as **t** (0 at the cut face, 1 at the dome tip): x = −4.65 + 9.3 t. The
  origin is moved to the bbox bottom centre in stage 2.

### 1.2 Measured views (`measure.py`, `comps.py`)

| View (box) | Silhouette bbox (px) | W : H | Leaves L | Cut wood W | Bark B | Cut face (W comp.) |
| --- | --- | --- | --- | --- | --- | --- |
| Front three-quarter (hero) | 55–522 × 177–445 | 1.740 | 11.1 % | 14.6 % | 74.4 % | 80 × 160 px, f .01–.18, h .16–.75 |
| Rear three-quarter | 580–973 × 205–444 | 1.642 | 7.6 % | 21.3 % | 71.1 % | 111 × 145, f .71–.98, h .03–.62 |
| Front | 31–277 × 567–707 | 1.752 | 11.4 % | 13.1 % | 75.6 % | 35 × 83, f .01–.15, h .16–.74 |
| Side | 313–480 × 573–707 | 1.244 | 15.6 % | 43.2 % | 41.2 % | 85 × 87, f .33–.83, h .02–.66 |
| Rear | 523–749 × 575–707 | 1.707 | 11.0 % | 13.2 % | 75.7 % | 42 × 74, f .81–.99, h .03–.58 |
| Top (a high 3/4 view) | 795–984 × 567–714 | 1.284 | 12.9 % | 9.0 % | 78.1 % | 24 × 63, f .00–.12, h .30–.72 |

- **Verifier tolerance:** shares ±4 points (W ±2.5); positions ±0.05 of W/H unless stated.
- **The front cell is the hero drawing again** (same W : H, same component fractions within 0.02), only smaller.
- **Cut-face ellipse openness** (W / H of the cut face): f34 0.50, front 0.42, rear 0.57, r34 0.77, side 0.98,
  top 0.38. With the cut face's normal along −X this gives the cameras in §3.1.

**Top profiles** (highest silhouette pixel per column as a fraction of H, every 0.05 f; all labels):

| f | .00 | .05 | .10 | .15 | .20 | .25 | .30 | .35 | .40 | .45 | .50 | .55 | .60 | .65 | .70 | .75 | .80 | .85 | .90 | .95 | 1.0 |
| --- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- |
| f34 | .44 | .68 | .75 | .78 | .77 | .75 | .74 | .73 | .72 | .71 | .82 | .78 | .89 | 1.0 | 1.0 | .96 | .67 | .76 | .64 | .51 | .39 |
| Front | .47 | .70 | .79 | .78 | .77 | .75 | .74 | .74 | .73 | .72 | .79 | .81 | .89 | .99 | 1.0 | .96 | .68 | .75 | .79 | .52 | .40 |
| Rear | .42 | .60 | .80 | .79 | .74 | .65 | .97 | .98 | .82 | .69 | .73 | .70 | .68 | .82 | .98 | 1.0 | .93 | .63 | .62 | .59 | .41 |
| r34 | .46 | .65 | .68 | .72 | .71 | .93 | .97 | .95 | .75 | .70 | .73 | .70 | .69 | .81 | .94 | .99 | .97 | .66 | .64 | .59 | .42 |
| Side | .14 | .36 | .46 | .61 | .90 | .97 | .99 | .96 | .85 | .72 | .74 | .73 | .76 | .84 | .93 | .99 | 1.0 | .95 | .35 | .36 | .12 |
| Top | .56 | .73 | .76 | .76 | .75 | .74 | .74 | .74 | .78 | .84 | .84 | .90 | .98 | 1.0 | .94 | .76 | .74 | .78 | .78 | .69 | .53 |

**Bottom profiles** (lowest pixel; the log lies flat, contact h .00–.07 along most of its length):

```
f34    .38 .15 .13 .13 .05 .04 .06 .06 .10 .07 .01 .01 .10 .07 .07 .09 .06 .07 .07 .12 .28
front  .33 .13 .13 .13 .04 .05 .05 .11 .11 .04 .00 .01 .07 .11 .08 .10 .07 .08 .08 .12 .28
rear   .33 .09 .07 .08 .06 .08 .11 .10 .09 .08 .07 .07 .05 .05 .04 .02 .02 .01 .01 .05 .29
```

**Wood-only top line in the f34** (bark + cut wood, leaves excluded): .44 .68 .75 .78 .77 .75 .74 .73 .72 .71 | stub
.82 .78 .89 1.0 1.0 .96 | .58 .55 .54 .51 .39. The log's top falls from .78 near the cut end to .71 at mid-length
and .51–.55 at the far end: perspective (strong in this cell) plus a mild taper (§1.4).

**Width per height** (silhouette width / W at h = 0.0, 0.1 … 1.0; start f after the @):

```
f34    .04@.51 .69@.22 .96@.02 .99@.01 .99@.00 .95@.01 .91@.03 .83@.07 .21@.49 .13@.60 .07@.64
front  .06@.47 .75@.19 .97@.01 .99@.01 1.0@.00 .96@.01 .91@.02 .85@.05 .20@.50 .13@.60 .06@.64
r34    .08@.77 .86@.09 .92@.07 .96@.03 .99@.01 .96@.01 .91@.04 .64@.13 .55@.25 .59@.24 .02@.76
side   .23@.46 1.0@.00 .85@.05 .90@.05 .77@.10 .71@.11 .62@.15 .54@.26 .60@.23 .66@.20 .48@.33
rear   .08@.81 .93@.03 .94@.04 .98@.01 .99@.00 .96@.02 .88@.05 .66@.10 .69@.09 .54@.26 .04@.72
top    .04@.48 .16@.41 .75@.14 .91@.04 .98@.02 1.0@.00 .96@.02 .89@.04 .27@.41 .16@.55 .05@.61
```

**Components** (`comps.py`): centre (f, h); extent.

| View | Stub / knot cut tops (W) | Leaf clumps (L) |
| --- | --- | --- |
| f34 | large-stub top .689, .961 (f .65–.74, 44 × 21 px); small-stub end .549, .090 (f .51–.59, h .01–.19, 36 × 49); knot tip .520, .805 (19 × 6) | FR .841, .172 (f .74–.93, h .06–.31, 88 × 69); BR (top-back) .846, .645 (f .76–.94, h .55–.78, 84 × 64); FL .278, .116 (f .20–.35, h .04–.22, 73 × 50) |
| front | large .687, .957; small end .520, .088 | FR .837, .176; BR .850, .643; FL .258, .118 |
| r34 | two upright stub tops: .775, .951 (41 × 26) and .286, .946 (36 × 18) | one, ground at the left (+X end, back): .154, .228 (f .03–.27, 95 × 80) |
| side | two upright stub tops: .791, .951 and .274, .958 | left (back) .145, .209; right (front) .887, .181 |
| rear | two upright stub tops: .748, .947 and .298, .938 | ground left .145, .199 (h .06–.38); log top at the left (+X) .148, .678 (h .57–.80) |
| top | large-stub top .654, .944; small-stub end .523, .060 | FR .803, .273; BR .834, .685; FL .207, .232; BK (behind the stub, split by it) .446, .781 and .660, .754 |

### 1.3 Silhouette and composition per view

**Front three-quarter (the hero, governs).** Camera front-left at about az −30, e 12 (cut-face openness 0.50 =
sin 30 × cos 12): the cut end faces the camera at the left, the log runs back to the right.
- **Cut end:** an 11-gon ellipse 80 × 160 px with a thin dark bark rim (`z_f34_cut.png`). Rings: dark 7–8-gon pith, a
  light band, a dark ring, a wide light outer band (§1.4).
- **Log body:** broad, long plate facets; the top edge nearly straight (falls .78 → .71 to mid-length); the bottom on
  the ground. 8–10 dark slits show on the visible half (§1.4). The far end (+X) closes in a blunt faceted dome: the
  top falls .55 → .39 and the bottom rises .12 → .28 over the last 0.05 f (`z_f34_far.png`).
- **Large stub:** stands on the top just right of centre (base f ≈ .58–.66), leaning right (screen lean ≈ 23° from
  vertical); width ≈ 52 px perpendicular to its axis (0.31 of the cut-face height); its pale top is an irregular
  broken cut (`z_f34_stubL.png`). The **knot nub** sits just left of its foot (f .46–.55, rising h .72 → .82): a short
  stub 42 px wide with a pale jagged tip.
- **Small stub:** leaves the log's lower front at f ≈ .40–.45, h ≈ .25–.40 and runs down-right to its pale end on the
  ground (f .51–.59, h .01–.19, 36 × 49 px); 8-sided, straight, slightly tapered (`z_f34_stubS.png`).
- **Leaf clumps:** FL on the ground left of the small stub, FR on the ground in front of the far end, BR on the
  log's top-back near the far end (its leaves stick up above the top line). Each a star of 5–6 broad kite leaves with
  a lit and a dark half.

**Front cell.** The same drawing (§1.2).

**Rear three-quarter, side, rear.** All three are one alternative drawing (§3.2): the log and cut end match, but
**two upright stubs** stand on the top (one near the cut end leaning toward −X, one at mid-length leaning toward +X)
with a small knot between them, and no stub lies on the ground.
- r34: camera rear-left (cut face at the right, openness 0.77 → about az −130); one big clump on the back ground
  near +X; the +X end is a rounded bark dome with a small knot hole (`z_r34_left.png`).
- Side: looking almost straight at the cut face (openness 0.98; az ≈ −80); the face is a near-round 11-gon (85 × 87
  px), the body shows to the left; one clump on the ground each side.
- Rear: camera behind, a little toward −X (openness 0.57, az ≈ −145); clumps on the back ground and on the log's
  top at +X (= hero BR).

**Top (`z_top.png`).** Not a plan view: a high three-quarter from the front-left (about az −30, e 40–50). Same layout
as the hero: the large stub at mid-length leaning to +X/back, the small stub pointing forward and toward +X
(screen vector (35, 43) px from its base), FL and FR on the ground in front, BR on the top-back, and a 4th clump (BK)
behind the log, split by the stub's base (§3.5).

**Close-ups.**
- **Cut-End Detail** (15,1290,370,1520): the 11-gon face (11 corners measured) with pith, light band, dark ring,
  light outer band; a narrow **chamfer** between the face and the bark rim (the outer light band's last 5 %, lit
  edge `#FBD19A` on the exploded insert); bark rim ≈ 0.07 R thick. Plate facets on the bark beside it.
- **Branch Stub Junction** (375,1290,700,1520): the stub rises straight out of the log top with no collar or seam
  ("Shared Faces"); its top is a pale 8–9-gon with a slightly darker centre and a short bark lip; a leaf clump right
  behind it (the hero BR pulled close).
- **Underside** (705,1290,1010,1520): a closed bottom, no holes; plate facets continue underneath; the large stub
  shows behind the log. Its pale ringed end at the right is the cut end seen mirrored from below (§3.6).

### 1.4 Parts (Exploded Construction (15,750,805,1240), `expl.png`)

Scale: the exploded log's receiving face is 142 px tall = Ø 3.2 → **about 44 px per stud**. The exploded stubs and
clumps are drawn larger than in the hero; the hero governs sizes.

#### Main Log (Trunk) (210,925,605,1100), 392 × 142 px (`z_expl_log.png`, `z_expl_end.png`)

- **What it is:** a long 11-sided prism, both long edges nearly straight (top line ±2 % of D apart from two knot
  bumps), a ringed receiving face at −X and a **blunt faceted dome** at +X (the far end is 0.93 of the near end's
  height on the exploded drawing; in the rear 0.85, the r34 0.86). A small dark **knot hole** near the +X top
  (583–595, 1001–1006; also on the r34's +X end).
- **Cross-section:** 11 sides; outline radius 0.95–1.05 (side view and close-up; `outline.py`), so ±5 % jitter, not a
  regular polygon. Bark rim on the cut end 0.07–0.09 R thick (`rim.py`).
- **Bark plates (the lesson from M020: no smooth cylinder).** On the sheet the bark is a patchwork of long, flat plates:
  - plate length 0.4–0.8 D (1.3–2.6 studs) along the log, width about one face (0.9 stud), plate boundaries staggered
    between neighbouring faces;
  - **dark slits** (`cracks.py`): the f34 shows 8–10 on its visible half: lengths 12–34 px (0.07–0.20 D, 0.25–0.65
    stud), widths 2–6 px (0.012–0.035 D, **0.04–0.11 stud**), shade `#483221`–`#5B3D2C`; the exploded log shows 6, the
    longest 111 px (0.78 D, 2.5 studs) low on the front; mostly lengthwise, a few diagonal;
  - **step ledges:** two short steps on the top near the cut end (t < 0.15) and plate edges catching a lit line.
- **Construction:** `_trunk(seed)`:
  - loft 11-sided rings at **12 stations** (t 0, 0.012 chamfer, then about every 0.8 stud), radius R 1.6 at t 0 →
    1.45 at t 0.9 (linear taper to 0.9 R), jitter radius ±0.06 (±4 %) per vertex, ring twist ±5° per station so the
    face ridges wander slightly; triangulate with beauty fill and flip some diagonals by seed so the plates read as
    long irregular triangles;
  - **plates:** per (face, station band) a radial offset 0 / +0.05 / +0.08 by seed, with **22 vertices per ring**
    (each face split at its middle) so neighbouring plates can step against each other; plate boundaries staggered;
  - **slits:** 9 thin wedge prisms carved one at a time (`M.carve`, before any union): triangular section **0.12 wide
    at the surface, 0.10 deep** (0.06 R), length 0.6–1.6 (one of 2.4 low on the front at t .4–.65), **≥ 6 on the front
    and top half** (azimuth −100° … +30° from the top toward the front), mostly lengthwise (±15°), one or two diagonal;
  - **two step ledges** on the top at t 0.02–0.12: a 0.06-high step across one face each;
  - **dome end (+X):** 3 rings closing over the last 0.45 stud (radius 0.9 R → 0.72 R → 0.4 R → apex flat 5-gon),
    faceted, jittered ±0.05; a knot hole (a shallow 5-sided dent 0.35 wide, 0.12 deep) at the top just before the
    dome;
  - **cut face (−X)**, flush, flat ("Flat Shaded"): the end cap carries loops at **0.20, 0.40, 0.62, 0.92 and 1.0 of
    the face radius**; the face radius is R − 0.13 (rim 0.08 R); pith 8-gon, the 0.40 loop 10-gon, 0.62 and 0.92
    11-gons following the outline; the 0.92 → 1.0 ring is the **chamfer**, bevelled 45° (0.10 stud back into the
    log); the bark rim is the outer 0.13 of the end ring. Keep the face within 0.02 of flat;
  - floor cut at z 0 after sinking the log 0.06 (a flat contact strip "Underside (Closed Geometry)").
- **Triangles:** 22 × 11 bands × 2 ≈ 480 trunk, slits 9 × ~16 = 145, dome 50, cut face ≈ 110 → **about 780**.

#### Cut-End Insert (55,970,165,1140), face 103 × 160 px (`z_expl_cut.png`)

- **Shape:** an 11-sided disc, **Ø 2.94** (the face), thickness **0.38** (0.12 D on the exploded side band), front edge
  chamfered (lit rim `#FBD19A`); rings as on the trunk's face (§1.4 loops, `rings.py` agrees on the insert: dark
  0–0.20, light 0.20–0.40, dark 0.40–0.60, light 0.60–1.0).
- **In the hero** it is the trunk's own face (unioned flush); exported alone as the CutEnd part.
- **Triangles:** about 140.

**Ring bands on every cut face** (`rings.py`, radial medians, r / face radius):

| View | 0–.20 pith | .20–.40 | .40–.62 ring | .62–1.0 outer |
| --- | --- | --- | --- | --- |
| Side (most frontal) | `#E7B278` (s .48) | `#F0C998` (s .37) | `#E6B175` (s .49) | `#F0C997` (s .37) |
| r34 | `#E8B479` | `#F1C998` | `#E7B276` | `#F0C999` |
| Rear | `#E4B27B` | `#EDC595` | `#E3B079` | `#EDC596` |
| f34 (face turned from the sun) | `#D9AA76` | `#E2BB90` | `#D7A673` | `#E0BB90` |
| Close-up | `#EAB376` | `#F2C995` | `#EBB67A` | `#F2CA97` |
| Exploded insert | `#D4A16C` | `#E0B789` | `#DAAA78` | `#E0BA8D`, edge `#FBD19A` |

**Ring count: 2 dark (pith + 1 ring), 2 light.** Dark bands are sat +0.11 and about 9 / 23 / 31 levels darker in
R / G / B than the light bands. The close-up's boundaries sit a little closer in (0.15, 0.25, 0.58); the views agree on
0.20 / 0.40 / 0.62.

#### Branch Stub (Large) (430,770,560,915), 141 × 53 px (`z_expl_stubL.png`)

- **Shape:** a straight, slightly tapered 8-sided branch, **L : Ø ≈ 2.6** (the part includes its buried base), broad
  long facets; a **broken top**: pale, tilted about 15° off square, with a jagged outline (one 0.1 Ø chip on the +X
  side) and a slightly darker pith (`#FED69F` against `#FDDEB0`); a **knot nub** at its foot on the −X side (about
  0.55 of its Ø, pointing out and down; in the hero it is the nub left of the stub).
- **Hero size:** Ø **1.0** at the base, 0.92 at the top (0.31 D; f34 52 px across against 168); **protrudes 2.0** along
  its axis above the log surface (0.62 D), buried 0.5 into the log.
- **Knot (part of this part):** Ø 0.75 (f34 42 px), protrudes 0.5 above the log, leaning 40° toward −X; a pale jagged
  tip (`#F6D6A8`) on bark sides.
- **Construction:** `_stub(length, r0, r1, seed, top_tilt, chip)`: 8 sides × 4 stations, jitter ±0.04, twist ±6°;
  top = a 2-loop cap (pith loop 0.3) tilted 15°; knot = a 6-sided 2-station nub with a jagged 3-point tip.
- **Triangles:** stub 8 × 4 × 2 + top 24 ≈ 90; knot ≈ 40 → **about 130**.

#### Branch Stub (Small) (630,995,770,1125), 144 × 48 px (`z_expl_stubS.png`)

- **Shape:** an 8-sided straight branch, **L : Ø ≈ 3.0**, a flat bark attach end and a **square-cut pale end**
  (`#E2B37F` in the hero = the Cut Wood swatch, faint facets, pith `#E2B179`, no rings); a small ledge-nub near its
  base underneath (exploded only; optional).
- **Hero size:** Ø **0.92** (0.29 D; f34 end 49 px tall), **protrudes 2.2** from the log surface, buried 0.4.
- **Construction:** `_stub` with no tilt or chip; end cap = pith loop 0.3 + face.
- **Triangles:** about 90.

#### Leaf Clump A / B (290,1110,410,1225) and (500,1095,600,1210) (`z_expl_leafA.png`, `z_expl_leafB.png`)

- **Shape:** a **flat six-leaf star** (`leafrad.py`: 6 lobes in the far-pixel angle histogram of each clump, about 60°
  apart ±15°) with a dark hub; leaves are broad pointed **kites**, W : L ≈ 0.5–0.55, with a midrib fold (a lit and a
  shaded half) and visible thickness on the hero leaves. On the exploded both lie almost flat; in the hero the leaves
  rise 15–35° (a few to 45° on FR) and droop slightly at the tips. A and B are the same recipe.
- **Size (hero governs):** spans FL **1.4**, FR **2.0**, BR **1.9**, BK 1.6 (top-view spans 0.42 / 0.60 / 0.58 of
  the log Ø; f34 FL 73 px against D 168); leaf L = 0.5–0.55 span, W = 0.5 L. Exploded clumps are about 1.6× bigger.
- **Construction:** `_leaf_clump(span, seed, fan=360)`: reuse **M020's round-2 broad kite recipe** (`_leaf_path`,
  `_leaf`, `RIDGE ((0.42, 0.075), (0.76, 0.035))`, `FOLD 0.14`, `LEAF_SLOPE (−18, −4)`, `LEAF_ROLL 12`), with
  **`LEAF_PITCH (15, 35)`** (flatter than M020's (24, 46): the exploded stars lie flat), W : L 0.52; 6 leaves, a
  hidden 5-sided hub (10 tris), no visible stem. Per leaf ±8 % L, ±6 % W, ±12° yaw. `fan` ≈ 240° for BR on the log
  top (no leaves into the bark).
- **Triangles:** 6 × 16 + 10 ≈ **106** each.

## 2. Layout (starting values; tune on the renders)

Studs, build frame (§1.1). x = −4.65 + 9.3 t. The hero camera (az −30) puts screen x ≈ 0.87 x − 0.5 y, so items in
front (−y) shift right on screen; the sheet's f34 also has strong perspective (far end drawn at about 0.72 of the
near end beyond the real taper), so expect f-fractions in our render to sit up to 0.05 right of the sheet's for far
items. Tune against kit `front34` (−28, 12).

| Piece | Placement | Size | Sheet evidence | Notes |
| --- | --- | --- | --- | --- |
| Trunk | axis y 0, z 1.6; x −4.65 … +4.65 | R 1.6 → 1.45 at t .9, dome over the last 0.45 | L : D 2.9; side face 85 × 87 | 11 sides, plates, 9 slits |
| Cut face | plane x −4.65, normal −X | face R 1.47, rim 0.13, chamfer 0.92–1.0 | rings .20/.40/.62 | flush, flat |
| Large stub | base t .60 (x 0.93) on the top, 10° behind the crest (y +0.28, z 3.18) | Ø 1.0 → 0.92, protrudes 2.0, buried 0.5 | f34 top f .689 h .96; base f .58–.66; top view at mid-length leaning +X/back | axis leans **28° toward +X, 8° toward +Y**; top centre ≈ (1.87, 0.53, 4.87) |
| Knot | t .49 (x −0.10), on the crest (y +0.1) | Ø 0.75, protrudes 0.5 | f34 f .46–.55, h .72–.82 | leans 40° toward −X; pale jagged tip |
| Small stub | base on the front, 20° below the equator, t .31 (x −1.77, y −1.50, z 1.05) | Ø 0.92, protrudes 2.2, buried 0.4 | f34 end f .549, h .09; top-view base t .31, front t .34 | axis yaw **25° from −Y toward +X**, pitch **15° down**; end centre ≈ (−0.85, −3.40, 0.47), its lower edge on the ground (floor cut) |
| FL clump | hub (−3.05, −2.05, 0.05), ground | span 1.4 | f34 .278, .116; top .207, .232 | full star |
| FR clump | hub (2.85, −1.95, 0.05), ground | span 2.0 | f34 .841, .172; top .803, .273 | full star; touching the log flank |
| BR clump | hub (3.5, 0.9, 2.9), on the log's top-back (35° behind the crest) | span 1.9 | f34 .846, .645 (h .55–.78); top .834, .685; rear top-left | fan 240°, hub sunk 0.1 |
| BK clump | hub (0.9, 2.1, 0.05), ground behind the log | span 1.6 | top .446/.660, .78 (split by the stub) | hidden in the hero; §3.5 |

**Expected hero:** X −4.66 … +4.66 (with the rim and leaves), Y −3.85 … +2.9, z 0 … 5.05 → **9.3–9.4 × 6.7 × 5.05**.
- **front34 (−28, 12) against the f34 and front cells:** W : H 1.66–1.82 (sheet 1.740 / 1.752; predicted ≈ 1.70).
- **Top:** compare with `top_sheet (−30, 45)`; W : H 1.20–1.40 (sheet 1.284).

## 3. View conflicts and resolutions

### 3.1 Cameras: the kit front34 is the sheet's hero

- **Evidence.** Cut-face openness 0.50 in the f34 = sin 30 × cos 12; the cut end faces the camera at the left; the
  log runs to the back-right. The kit `front34 (−28, 12)` is that view (az −28 = camera front-left).
- **Resolution.** Hero and front cells compare with kit **front34**. Extras for the other cells (§3.2):
  `r34_sheet (−130, 12)`, `rear_sheet (−145, 6)`, `side_sheet (−80, 6)`, `top_sheet (−30, 45)`. Kit `side (90, 4)`
  shows the +X dome and kit `rear34 (152, 12)` the back from the dome end: neither has a sheet counterpart
  (self-consistency only; they are the only checks on the dome and the back of the log).

### 3.2 The r34, side and rear cells draw a second upright stub

- **Evidence.** All three show two upright stubs on the top in a V (one near the cut end at t ≈ 0.1 leaning toward
  −X, one at t ≈ 0.68 leaning toward +X) with a knot between, and no stub on the ground. The hero, front, top and
  exploded views show one upright stub (+X lean, the knot at its −X foot) and the small stub lying forward to the
  ground. A stub on the top near the cut end would stand out against the sky in the f34; it isn't there.
- **Resolution.** **The hero governs** (WorldModeling §1.1): one large upright stub + knot + the small stub lying
  forward. In the r34/side/rear extras expect one upright stub instead of two (the +X-leaning one matches: same lean,
  knot on its −X side); judge them on the log, cut face, rings, shares ±6 and clump positions. Record the miss.

### 3.3 The exploded small stub attaches at the +X end

- **Evidence.** Its dashed arrow points to the log's upper side near +X (585, 1000). The hero, front and top put it
  low on the front at t ≈ 0.31.
- **Resolution.** Hero governs; the arrow is notation.

### 3.4 The far end: dome, not a second cut face

- **Evidence.** Every camera on the sheet sits on the −X side, so the +X end's face is never seen squarely. Its
  silhouette is a blunt, faceted, rounded bark end in the f34, r34 (`z_r34_left.png`, with a knot hole), rear, top
  and exploded (`z_expl_end.png`); the exploded has one Cut-End Insert. R06 built two cut ends.
- **Resolution.** A closed bark dome at +X (decision §8.3). Only the underside close-up shows a second ringed end
  (§3.6).

### 3.5 The fourth clump (BK)

- **Evidence.** The top view shows a clump behind the log, split by the large stub's base (t ≈ 0.55); the r34 and rear
  show a back ground clump near +X (t ≈ 0.85–0.95), but those cells are the alternative drawing (§3.2). The hero
  can't see behind the log.
- **Resolution.** BK on the back ground at t .6 (x 0.9, y 2.1), following the top view (the hero-consistent drawing).
  Top-view tolerance ±0.08 for BK; record the r34/rear offset.

### 3.6 Underside close-up

- It shows a ringed cut end at the right and the large stub as a long branch behind the log. Seen from below, the
  screen is mirrored relative to the elevation views, so the ringed end is the −X cut face. Its point is "Closed
  Geometry": no holes, plates continue underneath. Compare kit `underside (20, −45)` for self-consistency only.

### 3.7 Exploded against hero

- Exploded stubs and clumps are drawn about 1.3–1.6× the hero's scale; the hero governs sizes. The exploded log's
  slits are fewer (6) than the f34's (8–10): use 9.
- The insert is drawn as a separate thick disc; in the hero it is flush with the bark rim (§1.4).

### 3.8 "Simple solid colors, no texture noise" against the user's blended-colour rule

- The user's rule wins, and the sheet shows painted variation anyway: the cut-face rings (2 dark, 2 light bands);
  leaf base → tip (base `#4E8C18`/`#48881B` → tips `#6FAC21`/`#66A422` on the unshadowed exploded clumps); the stub
  tops' slightly darker pith. The bark has **no painted height gradient**: its saturation is 0.51–0.54 and hue
  21–23° in every band (exploded thirds `#61422F` / `#714B35` / `#AA7251` differ only in value, i.e. lighting). Keep
  bark Tint low and broad.

### 3.9 Effects

- The sheet shows none (no glow, sparkle, dust, chips). Stage 5/6 add nothing by default (§7).

## 4. Construction plan (stages 1–3)

1. **Parts first,** each from its own function and checked against its cell:
   - `trunk()` → `FallenSoftwoodLogTrunk`: the log with plates, slits, step ledges, knot hole, dome and the ringed
     flush face. Compare with the exploded log: 11 sides, near-straight edges, dome at +X, ≥ 6 slits visible.
   - `cut_end()` → `FallenSoftwoodLogCutEnd`: Ø 2.94 × 0.38 disc, 11 sides, 4 ring loops + chamfer.
   - `stub_large()` → `FallenSoftwoodLogBranchStubLarge`: stub + knot, broken tilted top. L : Ø ≈ 2.6.
   - `stub_small()` → `FallenSoftwoodLogBranchStubSmall`: straight stub, square pale end. L : Ø ≈ 3.0.
   - `leaf_clump()` → `FallenSoftwoodLogLeafClump`: span 1.9, six flat kites.
   - Render a parts shot (`extra`, about (−20, 15)) laid out like the exploded.
2. **Hero:**
   1. `_paste` (m011 pattern) the trunk, the two stubs (with the knot) and 4 clumps (§2, each with its own seed and
      yaw). Carve the slits into the trunk before pasting the stubs.
   2. One exact self-union, then `union_loose`, then `m004.floor_cut` at z 0.
   3. Origin at the bbox bottom centre; transforms applied. One closed shell (decision §8.6).
3. **Budget** (§4.3): hero about 1700–2200 (limit 4000), parts ≤ about 800. Spend spare on more trunk stations or
   plate splits if the plates read too big; never on smoothing.
4. **Placeholder keys** (stage 1): `m026_bark`, `m026_cut`, `m026_leaf`. Stage 4 adds the rest (§5.4).
5. **Stage 1 acceptance** (render, compare every view, measure with this folder's scripts):
   1. **Overall read:** one fallen log, not a cylinder: plates and slits read at the hero distance; the stubs grow out
      of the log with no collar ("Shared Faces"; extra `junc_cu (−20, 20)` framed on the large stub's foot); the cut
      face is flush in a thin rim; the far end is a rounded bark dome.
   2. **front34 (−28, 12) against the f34 and front cells:**
      - W : H 1.66–1.82; shares within ±4 (W ±2.5) of 11.1 / 14.6 / 74.4;
      - top profile within ±0.07 (the wood-only line ±0.05 from f .1 to .45);
      - cut face 0.15–0.19 W wide, 0.55–0.65 H tall (sheet 80 × 160 px = .171 W, .595 H);
      - large-stub top centre within ±0.05 of (.689, .961), small-stub end within ±0.06 of (.549, .090), knot visible
        left of the stub foot;
      - clump centres within ±0.06 (§1.2); exactly 3 clumps visible;
      - **≥ 5 dark slits** (v < 0.36, length ≥ 0.07 D) on the log body, and the 11-gon corners visible on the cut
        face outline (`outline.py`: 10–12 corners, radius 0.94–1.06).
   3. **Extras:** `r34_sheet`, `rear_sheet`, `side_sheet` against their cells: cut-face openness ±0.08, rings, the
      +X-leaning stub and knot, shares ±6 (the missing second stub is expected, §3.2). `side_sheet`: cut face 0.45–0.55
      of W, near-round. `top_sheet (−30, 45)`: W : H 1.20–1.40, 4 clumps (BK ±0.08).
   4. **Kit views** (side, rear34, rear, top, underside): self-consistency; the side shows the dome, the underside a
      closed bottom with a flat contact strip.
   5. **Parts against their cells** (§1.4).
   6. **Hero size** 9.4 × 6.7 × 5.05 (±0.35 / ±0.5 / ±0.25); log Ø 3.2 ±0.1, length 9.3 ±0.2.
6. **Stage 2:**
   - zero non-manifold, boundary, wire and loose elements; no zero-area faces or n-gons; normals outward;
   - no faces under 5° where stubs, the knot, clump hubs and slits meet bark (m011 `_tidy` / `_desliver`);
   - don't decimate the cut-face ring loops (they carry the rings), the 22-vertex trunk rings below 11 crests, the
     slits, or the leaves' 8-point outlines.
7. **Stage 3:** smart UV, margin ≥ 0.008, no overlaps, even texel density.

### 4.3 Budget table

| Piece | Count | Tris each | Total |
| --- | --- | --- | --- |
| Trunk (22 × 12 stations, plates, dome, face loops) | 1 | 640 | 640 |
| Slits (carved wedges) | 9 | 16 | 145 |
| Large stub + knot | 1 | 130 | 130 |
| Small stub | 1 | 90 | 90 |
| Leaf clumps (6 × 16 + hub 10) | 4 | 106 | 424 |
| **Sum before union** | | | **about 1430** |
| **Hero after union** (seams, slivers, floor cut) | | | **about 1700–2200** (limit 4000) |
| Parts: Trunk / CutEnd / StubLarge / StubSmall / LeafClump | | | about 790 / 140 / 130 / 90 / 106 (limit 1000) |

## 5. Colour plan (stage 4)

### 5.1 Swatches (flat; medians of a 38 × 38 box inside each)

| Swatch | Box | Hex | HSV |
| --- | --- | --- | --- |
| Cut Wood (Light) | (838,786,876,824) | `#DFAF79` | 32°, 0.46, 0.87 |
| Bark Wood (Medium) | (838,842,876,880) | `#7F543C` | 21°, 0.53, 0.50 |
| Leaves (Green) | (838,898,876,934) | `#588E30` | 94°, 0.66, 0.56 |

- **Cut Wood** = the side-facing cut ends: small-stub end `#E2B37F`, exploded small-stub end `#DCAE7A`, exploded
  insert face `#DFB88A`. Faces turned to the light render much paler (stub tops `#FDDEAF`–`#FDE7C2`).
- **Bark Wood** is just below the rendered medians (`#82573D`–`#85583E`): a good start, but calibrate on the render.
- **Leaves** is duller (sat .66) than every rendered leaf (sat .79–.84).

### 5.2 Rendered regions (`samp.py`, `dec.py`, `rings.py`, `leafrad.py`; median / lit quartile / shade quartile)

| Region | Box | Mask | Median | Lit | Shade |
| --- | --- | --- | --- | --- | --- |
| Bark, f34 / front / rear / r34 | V | B | `#82573D` / `#85583E` / `#83573E` / `#7C533D` | `#B47A56` / `#B47A56` / `#AF7653` / `#A97455` | `#533929` / `#543A29` / `#573D2C` / `#543B2C` |
| Bark, side / top | V | B | `#805842` / `#905F42` | `#AA7356` / `#A87251` | `#634330` / `#684632` |
| Bark, exploded log (unshadowed) | (210,925,605,1100) | B | `#85583E` (22°, 0.53) | `#B27955` | `#62422F` |
| Exploded log thirds, bottom / mid / top | x 260–600, y 1060–1100 / 1000–1060 / 925–1000 | B | `#61422F` / `#714B35` / `#AA7251` | | |
| Bark by height, f34, h 0–.2 / .2–.4 / .4–.6 / .6–.8 | x 140–520 bands | B | `#4D3526` / `#6D4935` / `#A46F50` / `#A57152` | `#895C3E` / `#9B6749` / `#B57B57` / `#BE8561` | |
| Large stub above the log, f34 / exploded | (330,177,410,250) / (430,770,560,915) | B | `#85593E` / `#764E36` | `#956446` / `#875F47` | `#714A34` / `#60402D` |
| Knot, f34 | (268,222,315,262) | B | `#95674E` (21°, 0.48) | `#B88364` | `#6F4B39` |
| Small stub, f34 / exploded | (250,345,335,445) / (630,995,770,1125) | B | `#6C4935` / `#8A5A3E` | `#B1744E` / `#BE7D56` | `#503627` / `#644431` |
| Close-ups: cut-end bark / junction / underside | §1.3 boxes | B | `#8D5E41` / `#8E5F44` / `#7C533B` | `#B47D5D` / `#AD7655` / `#A77250` | `#503727` / `#5F3E2C` / `#61432F` |
| Slits (dark components) | `cracks.py` | — | `#483221`–`#5B3D2C` | | |
| Cut face, f34 / front / side / rear / r34 / top | V | W | `#DFBA8E` / `#DBB68B` / `#ECC493` / `#EBC292` / `#EDC594` / `#F8D2A3` | `#E5C096` / `#E9C59D` / `#F4CE9E` / `#F2CDA0` / `#F4CD9C` / `#FBDEB6` | `#D5A471` / `#D2A473` / `#E4AF74` / `#E3AF77` / `#E6B075` / `#E0B886` |
| Cut face, close-up / exploded insert | (85,1295,260,1515) / (55,975,160,1140) | W | `#F0C794` / `#DFB88A` | `#F5CD9C` / `#E5BF94` | `#E8B175` / `#D6A46F` |
| Large-stub top, f34 / junction close-up / exploded | (355,176,405,200) / (470,1300,560,1370) / (510,775,560,815) | W | `#FDE7C2` / `#FDDEAF` / `#FCDDAE` | `#FEEAC9` / `#FEE1B7` / `#FDE1B6` | `#E8B57D` / `#E7AE72` / `#E1AB76` |
| Stub-top bands (junction close-up), r 0–.25 / .25–1 | | W | `#FED69F` / `#FDDEB0` | | |
| Small-stub end, f34 / exploded | (290,392,335,445) / (730,1060,775,1110) | W | `#E2B37F` / `#DCAE7A` | `#F5CC98` / `#F2C995` | `#DAAA75` / `#D5A16B` |
| Knot tip, f34 | (285,222,310,235) | W | `#F6D6A8` | | |
| Leaves, f34 / front / rear / r34 / side / top | V | L | `#528D1A` / `#528A1B` / `#4D851C` / `#4A8719` / `#427B1B` / `#568C1D` | `#82BC21` / `#80BB23` / `#71AF22` / `#6AA91C` / `#77B024` / `#7AB324` | `#2F5F14` / `#335F16` / `#305F18` / `#295B14` / `#234E14` / `#346217` |
| Leaf clumps, f34 FL / FR / BR | §1.2 boxes | L | `#3F7516` / `#538E1A` / `#57951F` | `#64A31D` / `#81BC1E` / `#8AC129` | `#295212` / `#326416` / `#366C16` |
| Leaf clumps, exploded A / B (unshadowed) | (285,1110,410,1225) / (500,1095,600,1210) | L | `#69A61C` / `#5E9E1F` | `#85BC1F` / `#83BD20` | `#407719` / `#407C1B` |
| Leaf base → mid → tip, exploded A / B (r / R 0–.3 / .3–.7 / .7–1) | | L | A `#4E8C18` / `#6EAC1C` / `#6FAC21`; B `#48881B` / `#5D9C1E` / `#66A422` | | |
| Leaves, close-ups junction / underside | | L | `#64A422` / `#518C1C` | `#8FC72C` / `#70AC24` | `#437F1A` / `#315F17` |

Deciles (dark → light), f34:

```
bark   #412D20 #583C2B #654430 #6F4A35 #7A513A #8A5C41 #9E6949 #A67051 #B17855 #BB815E
cut    #D3A06D #D6A472 #D8A876 #DCB281 #DEB88D #E0BA90 #E1BC91 #E1BD93 #E4BF95 #F7D6B3
leaves #274E11 #326415 #386F18 #407919 #4B8719 #55921C #5F9C1C #6DAA1C #7FB91F #8BC427
```

Side view (cut face square to the camera): cut `#E1AB70 … #F6D2A3`.

### 5.3 How the colour works

**Bark.**
- One warm brown: hue 21–23°, sat 0.51–0.54 everywhere (log, stubs, underside). The big lit/shade spread
  (`#412D20` → `#BB815E`) is the sun on the plates and slits; never paint by facing.
- **Painted signals are weak:** the knot is a touch lighter and greyer (`#95674E`, sat .48); the slits are geometry
  shadow. A third bark key is only for slit walls and the knot hole (position-selected).

**Cut wood.**
- Pale warm tan, hue 32–36°, sat 0.31–0.49.
- **Rings are paint on loop edges** ("Cut Face (Flat Shaded)"): pith 0–0.20 dark, 0.20–0.40 light, 0.40–0.62 dark,
  0.62–1.0 light; the chamfer ring a touch paler (lit). Dark bands sat ≈ 0.48, light ≈ 0.37; contrast ≈ 20 levels in
  G between bands on the side view.
- Stub tops: light with a slightly darker pith (r < 0.3), no rings. Small-stub end and the insert's sides are the
  swatch tone.

**Leaves.**
- Vivid yellow-green: hue 86–96°, sat 0.79–0.84. Base darker and greener-blue (95°), tips lighter and yellower (86°).
- The midrib fold gives each leaf a lit and a shaded half (geometry).

### 5.4 Keys (start from these; `K.calibrate`; write the calibrated hexes into `palette()`)

Calibration targets are rendered medians of **unshadowed** regions (exploded parts, the side view's square-on face, the
close-ups), not swatches.
- **`K.sample` kinds:** `"brown"` for the bark keys; `"green"` for the leaves; `"all"` on tight boxes for the cut-wood
  bands (cream fails `"brown"`'s sat filter).

| Key | Calibration target | Where | Finish |
| --- | --- | --- | --- |
| `m026_bark` | `#85583E` (exploded log median; front `#85583E`, f34 `#82573D`) | log, stubs, rim — the default | rough 0.9 |
| `m026_bark_light` | `#94654A` (knot `#95674E`; the lighter plates in the junction close-up `#8E5F44`) | the knot, about 25 % of plates as a broad mix | rough 0.9 |
| `m026_bark_dark` | `#5E402E` (slit / shadow tones `#5B3D2C`–`#62422F` as paint, kept above the geometry shadow) | slit walls, the knot hole, plate step faces (by position) | rough 0.95 |
| `m026_cut` | `#DFAF79` (swatch = small-stub end `#E2B37F` = insert `#DFB88A` medians) | small-stub end, insert sides, chamfer underside | rough 0.85 |
| `m026_cut_light` | `#F0C997` (side light bands `#F0C998`/`#F0C997`; close-up `#F2C996`) | face bands 0.20–0.40 and 0.62–1.0; stub-top and knot-tip faces | rough 0.85 |
| `m026_cut_ring` | `#E7B278` (side pith / ring `#E7B278`/`#E6B175`; close-up `#EAB376`/`#EBB67A`) | pith 0–0.20, ring 0.40–0.62; stub-top piths | rough 0.85 |
| `m026_cut_edge` | `#F6D6A8` (insert lit chamfer `#FBD19A`, knot tip `#F6D6A8`) | the chamfer ring 0.92–1.0 | rough 0.85 |
| `m026_leaf` | `#63A21E` (exploded clump medians `#5E9E1F`–`#69A61C`) | leaf middles | rough 0.8, `low_spec` |
| `m026_leaf_tip` | `#70AE21` (tips `#66A422`–`#6FAC21`; lit `#83BD20`) | outer 30 % | rough 0.8, `low_spec` |
| `m026_leaf_base` | `#4B8A19` (bases `#48881B`–`#4E8C18`) | inner 30 %, hub | rough 0.8, `low_spec` |

**Calibration warnings:**
- **Cut face:** calibrate the band keys so `side_sheet`'s face median lands within 10 of `#ECC493` and front34's within
  10 of `#DFBA8E` (that face is turned from the sun on the sheet; if our studio sun lights it, it will come out paler:
  record, and check the r34_sheet `#EDC594`). The ring contrast (dark vs light band) must stay ≥ 12 levels in G in
  front34 and side_sheet.
- **Bark:** calibrate on the parts shot of the trunk against `#85583E`; then front34 median `#82573D` ±10, lit quartile
  `#B47A56` ±14, shade `#533929` ±14.
- **Leaves:** greens calibrate darker than the painted sheet (kit memory); the front34 leaf median must land within 12 of
  `#528D1A` with sat ≥ 0.78, tips ≤ 90° hue. M020's leaf keys are the closest precedent.

### 5.5 Blending (`K.blend(mode="blend", steps=3)` over explicit face lists; fields are positions, never facing)

- **Bark** (fields: plate id, t along the log, distance to the nearest slit):
  - `bark` base;
  - plate patches: about 25 % of plates (by seed, whole plates) → 30 % `bark_light`; never single faces;
  - slit walls → `bark_dark` (hard inside the slit), 1-face fringe 25 % `bark_dark`;
  - knot → `bark_light`; knot hole → `bark_dark`;
  - stubs: `bark`, with their top 0.3 stud a 20 % `bark_light` mix (the lit lip on the sheet).
- **Cut face** (field = radius / face radius, from the loops): 0–0.20 `cut_ring`; 0.20–0.40 `cut_light`; 0.40–0.62
  `cut_ring`; 0.62–0.92 `cut_light`; 0.92–1.0 `cut_edge`; `mode="blend", steps=2` on each ring edge (soft stepped
  bands, not stripes); **hard** to the bark rim.
- **Stub tops / ends:** pith (r < 0.3) `cut_ring` → rest `cut_light` (large top, knot tip); small end `cut` with a
  `cut_ring` pith; hard to bark.
- **Leaves** (field = along-leaf t): t < 0.3 `leaf_base`; 0.3–0.7 `leaf`; > 0.7 `leaf_tip`; 3 steps, ±0.08 noise;
  hub `leaf_base`.
- **Hard edges only** where materials meet: bark | cut face rim, bark | stub tops and ends, bark | knot tip, leaf hub |
  bark or ground.

### 5.6 Texture (Tint) and finish

- **Tint** (`tint_var` per piece about 0.04): bark `K.texture` amp 0.045, scale 0.6 (broad, per plate group); cut
  faces amp 0.02 ("no texture noise"); leaves amp 0.035, scale 0.5. Never per-triangle confetti.
- **Finish:** bark keys rough 0.9 / 0.9 / 0.95; cut keys 0.85; leaves 0.8 with `FOLIAGE_SPEC` (`low_spec=True`);
  metal 0 everywhere.

### 5.7 Re-measure (final renders against the sheet, same boxes and masks)

- **Bark:** front34 median within 10 of `#82573D`; parts-shot trunk within 8 of `#85583E`; sat 0.48–0.56 in every
  height band (no painted gradient); slits darkest (≤ `#5B3D2C`).
- **Cut face:** side_sheet within 10 of `#ECC493`; ring order (pith dark, light, ring dark, light outer) visible in
  side_sheet and an extra `cut_cu (−75, 8)` close-up, boundaries at 0.20 / 0.40 / 0.62 ±0.05.
- **Stub tops:** large-stub top median within 12 of `#FDDEAF` from front34.
- **Leaves:** front34 within 12 of `#528D1A`, sat ≥ 0.78; tips lighter than bases in the parts shot.
- **Shares** per §4 step 5.2.

## 6. Joins and contact (no cracks or seams on this sheet)

- **Stubs into the log:** each stub starts 0.4–0.5 inside the log (buried); one exact union, no collar or seam ("Clean
  Junction (Shared Faces)"). The knot overlaps the large stub's foot and the log.
- **Slits:** carved into the trunk part before the stubs are pasted; keep slits ≥ 0.3 away from the stub feet and the
  cut-face rim.
- **Clumps:** hubs sunk 0.1 into the ground (FL, FR, BK) or the log (BR).
- **Ground:** the log sinks 0.06 and is floor-cut at z 0; the small stub's end is floor-cut the same way.
- No coplanar faces at the cut face (the face loops must not coincide with a trunk station; the first station sits at
  t 0.012 behind the chamfer).

## 7. Lighting and VFX plan (stages 5 and 6)

**What the sheet shows:** an ordinary sunlit log. No glow, light, sparkle, dust, chips or particles anywhere. The pale
cut faces are diffuse wood (shade quartile still `#E4AF74` on the side view), not emission.

### 7.1 Stage 5 (lighting): skip, and record why

- **No emissive faces, no PointLight.** Emission would flatten the rings.
- **Studio note (Requires Manual Validation):** check in Studio that the cut face's rings survive the game's sun
  (≥ 12 levels between bands), the slits read as dark lines, and the leaf base → tip gradient survives the palette
  export.

### 7.2 Stage 6 (VFX), kinds in `art/blender/lib/vfx.py`

- **Kinds that exist:** `torch_fire`, `campfire`, `brazier_fire`, `forge_fire`, `chimney_smoke`, `embers`,
  `heat_glow`, `glyph_glow`, `rune_glow`, `waterfall_mist`, `water_foam`, `waterfall_curtain`, `water_flow`, `vapour`,
  `harvest_hit`, `harvest_deplete`, `ore_glint`, `crystal_glow`, `crystal_halo`, `dust`. No new kind is needed.
- **Recommended: none.** The sheet shows no effect, and M009–M020 decided against harvest sockets. Record "Stage 6
  skipped: sheet shows no VFX".
- **Option** (decision §8.8): R06 `SoftwoodLog`'s pair, if the main session wants chopping feedback on wood nodes:
  - `harvest_hit` on the cut face, about (−4.75, 0, 1.6), colours `["#DFAF79", "#85583E"]` (cut-wood and bark chips);
  - `harvest_deplete` at the base centre, (0, 0, 0.5), same colours, shape about [9, 1, 3].
- **Not recommended:** `dust`, `ore_glint`, any light.

## 8. Naming and decisions for the main session

**Names owned elsewhere.** Found by `git grep` and every sheet .blend searched with `blendall.py`:
- **R06 kit:** `SoftwoodLog` (57 hits in `R06.blend`, 56 in `FlintbornWorldKit.blend`), `SoftwoodLogMain`,
  `SoftwoodLogBranchStub`, `SoftwoodLogCutEnd`, `SoftwoodLogWoodWedge`, `SoftwoodLogBranchStick`, `SoftwoodLogStump`;
  keys `r06_softbark`, `r06_cutwood`, `r06_leaf`.
- **W05:** `LogShell`, `LogCutEndCap`, `LogBranchStub`, `LogMossFoliage`, `LogAndStump*`. **Camp 06:** `FallenLog`,
  `CutLog`, `LogBench`. **R04:** a `*BranchStub`. `*LeafClump` in W05, W06, R05, M019, M020.
- **Future:** reference 055 is "Fallen Log Model Study"; keep `FallenLog*` free of our names (ours don't start with it).
- `M.mk` would silently rename a clash to `<name>M026`, so avoid all of these.

**Proposed names.** None occur in the repo or any sheet .blend (`FallenSoftwoodLog`: 0 hits); `m026_` is unused.

| Object | Part | Why |
| --- | --- | --- |
| `FallenSoftwoodLog` | hero | R06 owns `SoftwoodLog`; the header calls it "a fallen softwood log" |
| `FallenSoftwoodLogTrunk` | Main Log (Trunk), with its ringed face | R06 owns `SoftwoodLogMain` |
| `FallenSoftwoodLogCutEnd` | Cut-End Insert | R06 owns `SoftwoodLogCutEnd`; W05 `LogCutEndCap` |
| `FallenSoftwoodLogBranchStubLarge` | Branch Stub (Large), with the knot | R06 / W05 own `*LogBranchStub` |
| `FallenSoftwoodLogBranchStubSmall` | Branch Stub (Small) | |
| `FallenSoftwoodLogLeafClump` | Leaf Clump A/B (one recipe) | others own `*LeafClump` |

- Palette keys `m026_*` (§5.4). Collection `Kit/M026 Softwood Log`.

**Decisions needed (a recommendation each):**
1. **Size** (§1.1): **log Ø 3.2 × 9.3 long, hero 9.4 × 6.7 × 5.05** (recommended: hip-high chop log, leaves in line
   with M018–M020), or Ø 2.8 (camp `FallenLog` family; 8.2 × 5.9 × 4.4), or R06's Ø 5.5 (character-tall).
2. **Stub arrangement** (§3.2): **the hero's: large upright stub + knot, small stub lying forward to the ground**
   (recommended), or the r34/side/rear's two upright stubs (contradicts the hero, front, top and exploded).
3. **Far end** (§3.4): **closed rounded bark dome** (recommended), or a second ringed cut face like R06.
4. **Cut face** (§1.4): **flush and flat, rings painted on loop edges at 0.20 / 0.40 / 0.62, chamfer 0.92–1.0, rim
   0.08 R** (recommended: "Flat Shaded", "Slight Bevel"), or stepped ring planes like M020.
5. **Bark detail:** **11-sided trunk with plates, 9 carved slits (0.12 wide, 0.10 deep), 2 step ledges, a knot hole**
   (recommended: the M020 smooth-cone failure; the f34 shows 8–10 slits), or plates only.
6. **Hero packaging:** **one closed shell** (recommended), or stubs/clumps as separate objects.
7. **Exports:** the hero plus 5 parts (`...Trunk`, `...CutEnd`, `...BranchStubLarge`, `...BranchStubSmall`,
   `...LeafClump`) (recommended). R06's drops (wedge, sticks) and depleted stump are not on this sheet.
8. **Stage 5/6:** **no emission, light or VFX** (recommended), or the R06 `harvest_hit` / `harvest_deplete` pair with
   wood-chip colours (§7.2).
9. **Comparison cameras** (§3.1): kit `front34 (−28, 12)` for the hero and front cells; extras `r34_sheet (−130, 12)`,
   `rear_sheet (−145, 6)`, `side_sheet (−80, 6)`, `top_sheet (−30, 45)`, `junc_cu (−20, 20)`, `cut_cu (−75, 8)` and a
   parts shot `(−20, 15)`; kit side, rear34, rear, top, underside as self-consistency.
10. **Back clump BK** (§3.5): **t .6 behind the stub, per the top view** (recommended), or t .9 per the r34/rear.
11. **Names** as proposed.

## 9. Pitfalls to avoid

1. **A smooth cylinder.** The verifier will look for plates, steps and slits. Slits 0.10 deep and 0.12 wide, at least
   6 on the front/top half; radius jitter ±4 %; 22-vertex rings so plates can step. Check front34 for ≥ 5 dark slits.
2. **A regular polygon.** The cut-face outline is an irregular 11-gon (radius 0.95–1.05); the rings are 8/10/11-gons,
   not copies of the outline.
3. **A second cut end or a capped flat end at +X.** It is a rounded, faceted bark dome.
4. **Comparing with the wrong camera.** The hero is kit front34; the sheet's side/rear/r34 are the alternative stub
   drawing (§3.2); the sheet's "top" is a high three-quarter.
5. **Stepped or raised cut face.** It is flush and flat with a slight chamfer; rings are paint on loop edges. Don't
   decimate the loops.
6. **Stub collars or seams.** "Clean Junction (Shared Faces)": one union, buried bases.
7. **Spiky or upright leaves.** Flat six-leaf stars of broad kites (pitch 15–35°, W : L ≈ 0.52); M020 round-2 recipe.
8. **Floating pieces.** Small-stub end, FL, FR, BK on the ground; BR sunk into the log top-back.
9. **Colour by facing or a painted bark gradient.** The bark is one tone; light and dark come from the sun. Choose
   `bark_dark` by slit position, never by normal.
10. **Washed-out rings.** Keep ≥ 12 levels between ring bands in front34 and side_sheet.
11. **Exact booleans.** Carve the slits one at a time on the trunk part, stubs buried ≥ 0.4, no coplanar faces at the
    cut face; save between risky steps.
12. **Naming clashes** with R06 `SoftwoodLog*`, W05 `Log*`, camp `FallenLog`/`CutLog`, `*LeafClump` (§8).

## Decisions (main session, 2026-10-28)

All recommendations are accepted:
1. Size: log thickness 3.2, length 9.3; overall 9.4 W × 6.7 D × 5.05 H.
2. Stubs follow the hero's layout: a large upright stub with its knot, and a small stub lying forward.
3. Far end: a rounded bark dome.
4. Cut face: flush and flat, with the rings painted on the loop edges and the chamfer.
5. Bark detail:
   - 22-vertex rings with stepped plates;
   - 9 carved slits, 0.12 wide and 0.10 deep, at least 6 on the front and top half;
   - 2 step ledges, a knot hole and ±4 % radius jitter.
   - The hero render must show at least 5 dark slits; a smooth tube fails.
6. One closed shell. Add pieces one at a time.
7. Hero plus 5 parts.
8. No VFX.
9. Cameras: kit front34 (−28,12) for the hero and front cells, plus `r34_sheet (−130,12)`, `rear_sheet (−145,6)`, `side_sheet (−80,6)` and `top_sheet (−30,45)`.
10. The hidden back clump sits 0.6 of the way along the log, behind the stub.
11. Names as proposed: `FallenSoftwoodLogTrunk`, `FallenSoftwoodLogCutEnd`, `FallenSoftwoodLogBranchStubLarge`, `FallenSoftwoodLogBranchStubSmall`, `FallenSoftwoodLogLeafClump`, and the hero `FallenSoftwoodLog`.

Leaf clumps are flat six-leaf stars at a 15–35° pitch, never upright tulips.

## Stage 1. Modelling (modeller, 2026-10-28)

Builder `art/blender/kit/mcp/m026.py`, `build()` (fixed seeds, about 20 s geometry + 20 s renders in the background
session). Every part has its own function; the hero is built from the same functions.

- **Trunk (`trunk_raw`, `fuse_trunk`).** 11 stations × 22 vertices (11 corners with a fixed irregular outline ±4 % and
  ±3 % per vertex, a vertex in the middle of every face, ring twist ±5°, axial jitter ±0.08), R 1.6 → 1.45 at t 0.9, a
  level axis (z = 0.96 R0 − 0.06) so the bottom face lies on the ground at the cut end and the far end lifts a little.
  **Deviation:** 11 stations (0.875 apart) instead of 12 (0.8): the spare 44 tris pay for the plates, keeping the Trunk
  part under 1000.
  - **Plates are part of the same surface (no booleans):** each plate's cells use copies of their corner verts lifted
    0.07 or 0.10 along the radius; wall quads close every edge where two cells differ. 2 step ledges on the top at the
    cut end (band 0) + 12 seeded plates (1–3 bands × 2–4 half-columns), never touching each other even at a corner (so
    no bowtie), clear of the ground strip (228–312°), the stub/knot feet, the knot hole and the slits.
  - **9 slits, also in the grid:** a V-groove opened along a lengthwise column line (each vertex on the line split
    into low-side, high-side and bottom copies, plus a midpoint per band), 0.12 wide and 0.10 deep at the middle,
    closed and pointed at both ends, 1–3 bands long (0.9–2.6 studs; the long one low on the front at t .4–.65). 7 of
    the 9 face the hero (front/top 114–222°), 2 on the back. About 6–26 tris each against about 60 for a carved
    boolean slit.
  - **Knot hole:** the one boolean: a shallow inverted 5-sided pyramid (0.35 wide, 0.12 deep) near the +X top.
  - **Cut end (−X):** bark rim annulus (ring 0 → the face edge, 0.13 wide, in the x −4.55 plane), the 45° chamfer
    (0.92 → 1.0 of the face radius, 0.10 deep), and the flat face at x −4.65 with loops at 0.62 (11-gon following the
    outline), 0.40 (10-gon), 0.20 (8-gon) and a centre: flush, flat (the cleanup locks the x plane).
  - **Dome (+X):** 22 → 11 (0.9 R) → 8 (0.70 R) → 5 (0.40 R) → apex over 0.45 stud, jittered ±5 %.
- **Large stub (`_stub`):** 8 sides, 5 stations from 0.5 buried, flared 1.14× at the foot (the flared ring 0.18 out
  along the stub, clear of the bark: a ring lying on the bark left a 1.2° sliver), Ø 1.12 → 0.96, ±8 % per vertex,
  twist ±11°, ring wobble 0.05, leaning 30° to +X and 8° to +Y, protrudes 2.0. Broken top: the cut plane tilted toward
  the camera (normal d + (−0.12, −0.32, 0)), jagged ±0.04, a 0.10 chip on the +X side, a thin bark lip (0.86), the
  pale annulus and a 6-sided pith.
- **Knot (`_nub`):** 6 sides, Ø 0.84, protrudes 0.68 from the crest's front (x −0.15, 100°), leaning 40° to −X, a
  jagged pale tip. (Larger than the spec's Ø 0.75 × 0.5: at that size it hid behind the crest in front34.)
- **Small stub:** the same builder, Ø 1.0 → 0.9, flare 1.14, protrudes 2.2 from the lower front (x −1.77, 200°), yaw
  25° toward +X, pitch 15° down; square-cut pale end resting on the ground (floor-cut).
- **Leaf clumps (`_clump`, M020's round-2 kite recipe):** six broad kites (L 0.52 span, W 0.62 × half-span) round a
  hidden 5-sided hub, pitch alternating in the lower / upper third of 15–35° (flat stars, never tulips), no stem.
  Spans FL 2.1, FR 2.6, BR 2.4 (fan 240° on the log's top-back at 74°, hub sunk 0.1), BK 2.0. The spec's spans
  (1.4–2.0) read too small against the sheet: the f34 leaf share was 6.8 % against 11.1 %, now 8.8 %. Ground hubs at
  z 0.14 (the leaf bases above the floor cut, only the hub cone is cut) are slid toward the log until their leaves cut
  into it (one shell), then 0.2 further.
- **Hero:** trunk (fused) + stubs + knot + clumps → one exact union with no post-union merge (`_union_fine`, m021) →
  floor cut at z 0 → the guarded cleanup → finish → polish → `M.fix_bowties`. A guard rebuilds with the clumps turned
  17° if the result has a fold (clean on the first attempt with the current seeds).
- **Size:** hero 9.30 × 6.32 × 4.84 (target 9.4 ± 0.35 × 6.7 ± 0.5 × 5.05 ± 0.25). Log Ø 3.2, length 9.3.
  - H is the large stub's top. The spec's 2.0 protrusion with the tapered log gives 4.84; 5.03 (protrusion 2.2) made
    the hero W : H 1.56 against the sheet's 1.74.
  - D is set by the small stub's end (y −3.6) and BK (+2.7). The spec's 6.7 assumed BK at y 2.1 with span 1.6, which
    doesn't reach the log and would be a separate shell.

## Stage 2. Optimisation and cleanup

| Object | Tris | Size (studs) | Shells | Non-manifold edges / bowtie verts / boundary / wire / loose | Zero-area / n-gons | Self-hits | Min corner |
| --- | --- | --- | --- | --- | --- | --- | --- |
| FallenSoftwoodLog (hero) | 2060 / 4000 | 9.30 × 6.32 × 4.84 | 1 | 0 / 0 / 0 / 0 / 0 | 0 / 0 | 0 | 5.07° |
| FallenSoftwoodLogTrunk | 934 / 1000 | 9.30 × 3.28 × 3.21 | 1 | 0 / 0 / 0 / 0 / 0 | 0 / 0 | 0 | 5.17° |
| FallenSoftwoodLogCutEnd | 124 | 0.38 × 2.94 × 2.95 | 1 | 0 | 0 | 0 | 9.04° |
| FallenSoftwoodLogBranchStubLarge | 162 | 2.29 × 1.35 × 2.61 | 1 | 0 | 0 | 0 | 5.41° |
| FallenSoftwoodLogBranchStubSmall | 108 | 1.96 × 2.78 × 1.59 | 1 | 0 | 0 | 0 | 7.48° |
| FallenSoftwoodLogLeafClump | 186 | 1.69 × 1.79 × 0.54 | 1 | 0 | 0 | 0 | 5.66° |

- Normals outward (signed volume, recalculated over each closed mesh); no custom normals; flat shading; transforms
  applied; origin at the bbox bottom centre on every object.
- Guarded cleanup (m020's `_clean_guarded`, copied locally): no vertex moves more than 0.08 (the slits are 0.12
  wide). It locks the ground plane (z 0) and the cut-face plane (x = X_FACE in object coordinates), so the face stays
  flat, and refuses moves that would push a face through another.
- The Trunk part is 934 tris with plates and slits in the surface. The first version, with boolean-carved slits, was
  1340.

## Stage 3. UV

Smart UV at 45°, re-unwrapped ANGLE_BASED from its island seams, margin 0.008, then m012's `_uv_unfold`.

| Object | Islands | Overlaps / flipped | Min gap | Density spread | Conformal stretch p95 |
| --- | --- | --- | --- | --- | --- |
| Hero | 414 | 0 / 0 | 0.016 | 1.0 / 1.0 / 1.0 | 1.015 |
| Trunk | 108 | 0 / 0 | 0.016 | 1.0 | 1.013 |
| CutEnd | 8 | 0 / 0 | 0.016 | 1.0 | 1.053 |
| StubLarge | 16 | 0 / 0 | 0.016 | 1.0 | 1.029 |
| StubSmall | 8 | 0 / 0 | 0.017 | 1.0 | 1.028 |
| LeafClump | 35 | 0 / 0 | 0.016 | 1.0 | 1.042 |

## Stage 4. Materials, colour and texture

- **Pass 1** (`m026.calibrate()` on the kit dome, against the spec 5.4 targets). The keys rendered:
  - bark (138,93,66), bark_light (148,100,74), bark_dark (94,65,49);
  - cut (222,175,121), cut_light (240,201,151), cut_ring (231,177,120), cut_edge (247,214,168);
  - leaf (100,162,29), tip (112,174,32), base (76,138,25).
  All are within 6 of target.
- **Pass 2** (hero renders against the sheet, `m026.measure()`, the study's masks; linear-light scaling):
  - **bark ×0.88:** the f34 median was 10 light;
  - **bark_light ×1.75:** the broad lit patches carry the sheet's lit plates (lit quartile #936448 against #B47A56);
  - **leaf_tip ×1.56 and leaf_base ×0.85:** the lit/shade spread;
  - **New keys `m026_face_light/ring/edge`** for the log's own cut face and the CutEnd disc. The face points −X, away
    from the studio sun, so with the dome-calibrated cut keys it rendered #C9A87D in side_sheet against the sheet's
    #ECC493. They are the cut keys ×1.42, from the side_sheet ratio. The sun-lit stub tops keep the cut keys, which
    render #FEDDAF against the sheet's #FDDEAF. The small stub's end (also turned from the sun) is face_light/ring 50 %.
- **Final keys:**

| Key | Hex | Rough | Target / role |
| --- | --- | --- | --- |
| m026_bark | #674631 | 0.9 | #85583E |
| m026_bark_light | #986B50 | 0.9 | lit patches |
| m026_bark_dark | #4A3224 | 0.95 | #5E402E (slit grooves) |
| m026_cut | #AF8F68 | 0.85 | #DFAF79 |
| m026_cut_light | #BDA482 | 0.85 | #F0C997 (stub tops) |
| m026_cut_ring | #B69167 | 0.85 | #E7B278 (stub piths) |
| m026_cut_edge | #C2AE90 | 0.85 | #F6D6A8 (knot tip) |
| m026_face_light | #DCBF99 | 0.85 | #F0C998 (face light bands, disc side) |
| m026_face_ring | #D4AA79 | 0.85 | #E7B278 (pith, ring) |
| m026_face_edge | #E2CBA8 | 0.85 | chamfer |
| m026_leaf | #55881D | 0.8, low spec | #63A21E |
| m026_leaf_tip | #76B126 | 0.8, low spec | lit #82BC22 |
| m026_leaf_base | #3D6D16 | 0.8, low spec | #4B8A19 |

- **Fields (position only, never facing):**
  - bark: broad noise patches stepping 25 / 50 / 75 % toward bark_light;
  - slit grooves: bark_dark (a genuine crack);
  - cut-end bark rim: 50 % bark_dark;
  - stub top 0.35 stud and lip: 25 % bark_light; knot: 50–75 % bark_light;
  - cut face: flat band keys on the ring loops (pith ring, 0.20–0.40 light, 0.40–0.62 ring, 0.62–0.92 light, the
    chamfer edge), hard to the bark rim;
  - leaves: base → mid → tip ladder in 25 % steps along each leaf, one half 0.3 toward the base (the lit/shaded
    halves);
  - floor caps: bark, leaf base under leaves, the small end's key under its end.
- **Tint:** bark amp 0.045, scale 0.6; cut amp 0.02; leaves 0.035 / 0.5. K.check is clean, including the colour-by-
  facing correlation; the disc's sides use face_light so its one wood doesn't follow facing.
- **Re-measured** (ours against the sheet; f34 = `f34_sheet`, long lens at −34° / 12°, which gives the cell's
  cut-face openness 0.52 against 0.50):

| View | Bark median / lit / shade | Cut face median | Leaf median / lit | Shares L / W / B | W : H | Slits |
| --- | --- | --- | --- | --- | --- | --- |
| f34 | #845940 / #AA7453 / #543727 (sheet #82573D / #B47A56 / #533928) | #EAC494 (#DFBA8E) | #5A931E / #75B227 (#528D1A / #82BC22) | 8.8 / 10.7 / 80.6 (11.1 / 14.5 / 74.4) | 1.652 (1.743) | 8 (8) |
| front (kit front34) | #84593F / #A87352 / #543727 | #EAC597 | #59931E | 9.0 / 4.9 / 86.1 | 1.659 (1.757) | 7 (5) |
| side | #825940 | #EAC494 (#ECC493) | #56921D | 6.3 / 42.5 / 51.2 (15.6 / 43.2 / 41.2) | 1.108 (1.246) | 4 |
| rear | #714F3A (#83573E) | #ECC696 (#EBC292) | #355B10 | 3.9 / 11.7 / 84.4 | 1.711 (1.712) | 9 |
| top | #855A41 (#905F42) | #EAC495 | #5F9B1E (#568C1D) | 13.8 / 6.4 / 79.8 (12.9 / 9.0 / 78.1) | 1.317 (1.286) | 7 |

## Stage 5. Lighting

Skipped (decision 8): the sheet shows an ordinary sunlit log, so there is no emissive key and no light.
- **Studio note (Requires Manual Validation):**
  - the face keys are brighter than the stub-top keys because the face points −X, away from the kit studio's sun. If
    the game's sun lights the −X end head-on, the face will read paler than the sheet;
  - check that the ring bands still differ by at least 12 levels, and that the slits read as dark lines.

## Stage 6. VFX

Skipped (decision 8): the sheet shows no glow, sparkle, dust or chips, so there are no sockets. Renders still use
vfx=True (nothing to realize).

## Modeller's notes for the verifier

- **Cameras:**
  - `f34_sheet` is (−34, 12) with a 3× lens, compared with the f34 cell. At −28 the cut face opened only 0.42.
  - Kit `front34` (−28, 12) is compared with the front cell.
  - `r34_sheet`, `rear_sheet`, `side_sheet` and `top_sheet` are as decided. `measure()` runs the study's masks on
    both images.
- **Expected misses:**
  - The sheet's r34/side/rear cells draw two upright stubs (spec 3.2); we have one plus the knot, so their W : H and
    top profiles differ (side 1.11 against 1.25, r34 1.36 against 1.64).
  - In the f34 the sheet's near cut end is enlarged by its perspective, so its W share is 14.5 % against our 10.7 %
    and W : H is 1.74 against 1.65. The stub, log and face sizes are as decided.
  - The back-facing bark (rear, r34) reads darker than the sheet's (#714F3A against #83573E). That is the studio sun
    on the far side; it was not painted lighter by facing.
- **Hero D is 6.32** (tolerance 6.2–7.2). Size notes are in stage 1.
- **Deviations from the spec numbers:**
  - 11 trunk stations instead of 12;
  - knot Ø 0.84 × 0.68 instead of 0.75 × 0.5;
  - stubs Ø 1.12 / 1.0 at a flared foot, not 1.0 / 0.92;
  - clump spans about 1.3× the spec's;
  - slits 0.9–2.6 long, against the sheet's 0.25–0.65 plus one of 2.5: a groove can't be shorter than one band;
  - the large stub's top tilted toward the camera so its pale cut shows (as on the sheet).
- **Slit count on the hero renders:** `stats()["slits"]` gives 8 in f34_sheet and 7 in front34.
- **Self-check:** `build()["problems"]` is empty. It covers every audit field, the size targets, slit count, UV
  overlaps and K.check.

## Stage 7 — Verification (round 1)

Fresh verifier, read-only, in a background session on port 9882 with `wip/M026_verify.blend`. Nothing was saved and
`build()` was not called. Fresh renders went to the scratchpad (`.../scratchpad/v026/renders/M026/`, high-res extras
in `.../v026/renders/big/`). Colours were sampled on both images with the study's masks (`m026.measure()`), a
component pass (`v026/comp.py`), radial ring bands (`v026/rings.py`) and box samples (`v026/samp.py`).

**Result: FAIL, 6.5 / 10.** The log, the cut face, the dome and the topology are good. The fails are three focal
details that read clearly unlike the hero cell.

### Re-measured geometry (all independent; matches the modeller's table)

| Object | Tris | Size | Shells | NM edges / bowtie verts / boundary / wire / loose | Zero-area / n-gons / dup | Self-hits | Inverted (ray parity) | Min corner | UV islands / overlaps / flipped / min gap / p95 |
| --- | --- | --- | --- | --- | --- | --- | --- | --- | --- |
| FallenSoftwoodLog | 2060 / 4000 | 9.30 × 6.32 × 4.84 | 1 | 0 / 0 / 0 / 0 / 0 | 0 / 0 / 0 | 0 | 0 | 5.07° | 414 / 0 / 0 / 0.016 / 1.015 |
| …Trunk | 934 / 1000 | 9.30 × 3.28 × 3.21 | 1 | 0 / 0 / 0 / 0 / 0 | 0 / 0 / 0 | 0 | 0 | 5.17° | 108 / 0 / 0 / 0.016 / 1.013 |
| …CutEnd | 124 | 0.38 × 2.94 × 2.95 | 1 | 0 | 0 | 0 | 0 | 9.04° | 8 / 0 / 0 / 0.016 / 1.053 |
| …BranchStubLarge | 162 | 2.29 × 1.35 × 2.61 | 1 | 0 | 0 | 0 | 0 | 5.41° | 16 / 0 / 0 / 0.016 / 1.029 |
| …BranchStubSmall | 108 | 1.96 × 2.78 × 1.59 | 1 | 0 | 0 | 0 | 0 | 7.48° | 8 / 0 / 0 / 0.017 / 1.028 |
| …LeafClump | 186 | 1.69 × 1.79 × 0.54 | 1 | 0 | 0 | 0 | 0 | 5.66° | 35 / 0 / 0 / 0.016 / 1.042 |

- **Normals and interior faces.** Normals point outward (signed volume, plus a per-face ray-parity test: 0 inverted).
  Each object is one closed manifold shell with no self-hits, so no interior faces are left.
- **Shading and transforms.** No custom normals. Flat shading (0 smooth polys). Rotation 0, scale 1. Origin at the
  bbox bottom centre on all 6 objects. No modifiers, parents or children.
- **Checks.** `K.check` is clean. UV border is 0.008 and density spread is 1.0 on all objects.
- **Size against the decision.** W 9.30 (9.4 ± 0.35) passes. D 6.32 (6.7 ± 0.5) passes. H 4.84 (5.05 ± 0.25) passes.
  Log Ø 3.2 and length 9.30 pass.
- **Materials.** 22 keys on the hero, all `m026_*`. No VFX and no emission (decision 8).

### View comparison (sheet → ours)

**What passes:**
- **Cut face.** It reads as an irregular 11-gon with a thin bark rim and a lit chamfer, and it is flush and flat. The
  rings are in the right order: pith dark, light, ring dark, light outer.
- **Ring colours** (side cell → side_sheet):

  | Band | Sheet | Ours | Δ |
  | --- | --- | --- | --- |
  | Pith | `#E7B277` | `#E1AC73` | −6/−6/−4 |
  | Light | `#F0C896` | `#EAC493` | −6/−4/−3 |
  | Ring | `#E6B176` | `#E2AD73` | −4/−4/−3 |
  | Outer | `#EFC897` | `#ECC594` | −3/−3/−3 |

  The G contrast is 24 against the sheet's 22. r34 and the close-up agree within 8.
- **Bark relief.** Raised plates, the 2 ledges, the knot hole near the +X top and V-slits. Slits counted on the hero:
  8 in f34_sheet (sheet 8) and 7 in front34 (front cell 5). It is not a tube.
- **Dome far end.** Blunt, faceted and rounded, with slits running onto it.
- **Underside and junction.** The underside is closed, and the stubs grow out of the bark without a seam.
- **Top view.** W : H is 1.317 (sheet 1.286) and the leaf share 13.8 % (12.9 %).

**Shares and silhouette (f34 cell → `f34_sheet`):**

| Measure | Sheet | Ours | Tolerance | Result |
| --- | --- | --- | --- | --- |
| W : H | 1.743 | 1.652 | 1.66–1.82 | just outside |
| Leaves L | 11.1 % | 8.8 % | ±4 | ok |
| Cut wood W | 14.5 % | 10.7 % | ±2.5 | fails |
| Bark B | 74.4 % | 80.6 % | ±4 | fails |
| Wood-only top line, f .05–.40 | .68–.78 | .57–.64 | ±0.05 | fails |
| Cut-face height | .59 H | .50 H | 0.55–0.65 | fails |

- **Front cell → kit front34:** W share 4.9 % against 13.0 %, top line .67–.69 against .74–.79.
- **Rear and side cells:** leaf share is 3.9 % against 11.0 % (rear) and 6.3 % against 15.6 % (side), outside ±6.

**Components (f34 → f34_sheet):**

| Item | Sheet (centre f, h; area; median) | Ours | Verdict |
| --- | --- | --- | --- |
| Large-stub pale top | (.691, .965); 0.47 %; 43 × 20 px; `#FDE7C2` | (.632, .971); 0.08 %; a 29 × 15 sliver; `#EAC89C` | 6× too small, Δf −0.059 |
| Small-stub pale end | (.550, .090); 0.91 %; `#E2B480` | missing from the W mask; box median `#A4835C` | not pale |
| Knot tip | (.521, .808); 0.04 %; `#F6D6A8` (lit) | (.470, .696); 0.27 %; `#FEDDAE` | 7× too big |
| FR clump | (.843, .173); hf .25 | (.885, .219); hf .18 | ok position, low |
| BR clump | (.848, .648); h .55–.78, hf .235 | (.754, .739); h .69–.79, hf .10 | Δf −0.094, Δh +0.091; flat strip |
| FL clump | (.279, .116); hf .18 | (.325, .083); hf .15 | ok |

**Colours (sheet → ours, Δ R/G/B):**

| Region | Sheet | Ours | Δ R/G/B | Verdict |
| --- | --- | --- | --- | --- |
| Bark median, f34 | `#82573D` | `#845940` | +2/+2/+3 | |
| Bark lit, f34 | `#B47A56` | `#AA7453` | −10/−6/−3 | |
| Bark shade, f34 | `#533928` | `#543727` | +1/−2/−1 | |
| Bark median, front | `#85583E` | `#84593F` | −1/+1/+1 | |
| Bark median, rear | `#83573E` | `#714F3A` | −18/−8/−4 | studio light on the back; not to be painted by facing |
| Bark lit, rear | `#AF7653` | `#90644A` | −31/−18/−9 | as above |
| Cut face, f34 | `#DFBA8E` | `#EAC494` | +11/+10/+6 | the sheet's face is in shade |
| Cut face, side | `#ECC493` | `#EAC494` | −2/+1/+1 | |
| Cut face, r34 | `#EDC594` | `#EBC595` | −2/0/+1 | |
| Large-stub top (box) | `#FCE4BD` | lit quartile `#E5C398` | −23/−33/−37 | the median is bark |
| Small-stub end | `#DDAF7A` | `#A4835C` | −57/−44/−30 | |
| Knot tip (box) | `#BE8764` | `#F2D2A5` | +52/+75/+65 | far too pale and large |
| Leaves median, f34 | `#528D1A` | `#5B9522` | +9/+8/+8 | sat 0.77, target ≥ 0.78 |
| Leaves lit, f34 | `#82BC22` | `#77B32D` | −11/−9/+11 | |
| Leaves shade, f34 | `#2F5F14` | `#3C6115` | +13/+2/+1 | |
| Leaves median, rear | `#4C851C` | `#375B13` | | BK in shadow |

### Itemised findings

**Blockers** (each with a fix a fresh modeller can act on):

1. **Large-stub pale broken top barely shows.** It is focal silhouette 2. On the sheet it is a broad pale cap in the
   f34, front, top and junction close-up. Ours is a sliver: 0.08 % against 0.47 % of the bbox, lit `#E5C398` against
   `#FDE7C2`, and the junction close-up shows the same thin edge.
   - **Cause.** The cap normal is about d + (−0.12, −0.32, 0) ≈ (0.38, −0.25, 0.88). That gives only about 0.18
     openness toward the f34 camera.
   - **Fix: aim the cap.** In `STUB_L` / `_stub`, aim the broken-top plane's normal at about (0.05, −0.40, 0.91) in
     the build frame: mostly up, tipped about 25° toward the front. That is about 0.48 openness for (−34, 12).
     Keep the jag and the +X chip.
   - **Optional.** Widen the stub's top Ø to about 1.0 so the cap reads at the sheet's 43 × 20 px.
   - **Acceptance in f34_sheet.** A W component of at least 0.35 % at (.69 ± .05, .96 ± .04), median within 15 of
     `#FDE7C2`.
2. **Small-stub pale end renders dull brown.** It is `#A4835C` against `#DDAF7A`, and the study's cut-wood mask
   doesn't find it at all (sheet: 0.91 % at (.55, .09)). Its face normal, about (0.41, −0.88, −0.26), points down
   and away from the key light (n·L ≈ 0.15).
   - **Fix: geometry first.** Slant the end cut up. Rotate the end-cap plane about the stub's horizontal cross axis
     so its normal is about (0.25, −0.80, 0.55) (n·L ≈ 0.6, openness ≈ 0.6 to the camera). Keep its lower edge on
     the floor cut.
   - **Then paint.** Use the same cut keys as the large-stub top: `cut_light` with a `cut_ring` pith. Add no extra
     facing multiplier.
   - **Acceptance in f34_sheet.** A W component of at least 0.6 % at (.55 ± .06, .09 ± .06), median within 15 of
     `#E2B480`.
3. **BR leaf clump on the log top lies flat and sits too far left.**
   - **Sheet:** leaves rise above the top line, centre (.848, .648), h .55–.78.
   - **Ours:** a thin strip at (.754, .739), h .69–.79. That is outside the stage-1 ±0.06 clump tolerance on both
     axes.
   - **Fix:**
     - Move the BR hub toward +X and down the back: x ≈ 3.9–4.1, about 45–55° behind the crest. Avoid the knot
       hole at x 3.85 / 96°.
     - Turn its hub normal to about 10° from vertical, so the 15–35° pitch (decision) lifts the leaves above the
       top line.
     - Use the top of the pitch band (28–35°) and fan about 240° away from the bark.
   - **Acceptance:** f34 BR at (.85 ± .06, .65 ± .06) with hf ≥ 0.18.
   - **Alongside:** give all clumps broader kites (W : L 0.55–0.6) and the upper half of the pitch band, so the
     ground clumps reach hf ≥ 0.2 (sheet FR .25) and the side/rear leaf shares come up toward ±6.

**Minors** (record, or fold into the fix round if cheap):

4. **Knot tip.** The pale tip is 7× the sheet's (0.27 % against 0.04 %). It is the brightest patch on the top,
   which inverts the sheet's emphasis (big stub top, small knot tip). Shrink the pale cap to about 0.35 of the knot
   Ø, with bark sides, and lower it to about h .80.
5. **Stub height against the decision.** The large stub stands about 1.4× taller relative to the log than in the
   hero cell. The f34 wood-only top line is .57–.64 against .68–.78, the cut face is .50 H against .55–.65, and
   W : H is 1.652 against 1.66–1.82. Part of this is the sheet's perspective. The rest is the decided H (5.05 ± 0.25):
   matching the hero cell's profile would need H ≈ 4.5. This is a decision conflict for the main session, not a
   modeller error.
6. **Plate pattern.** The plates' end walls all sit on the same station rings. This gives regular vertical seams
   round the log (clear in rear_sheet and r34_sheet), a "segmented barrel" look. The sheet's plates end on
   staggered diagonals. Possible fix: jitter each plate's end walls ±0.3 along x per column.
7. **Slit length.** The slits are long lengthwise grooves (0.9–2.6). The sheet's are mostly short (0.25–0.65). This
   is a recorded deviation.
8. **Leaf colour.** Slightly flat and desaturated: median sat 0.77, the lit quartile has too much blue (Δ B +11), and
   the shade is too light (Δ R +13). Lower `m026_leaf_tip`'s blue a little, and darken `m026_leaf_base` about 10 %.
9. **Back bark.** It reads darker than the sheet's rear cells (−18/−8/−4). This comes from the studio light. Accepted:
   painting it lighter would be colouring by facing.
10. **`m026_face_*` keys: borderline, accepted with a note.**
    - **Why accept:** they are assigned by region (the log's end grain and the whole CutEnd part, sides included),
      not per face by normal, and `K.check` is clean.
    - **Why borderline:** they are the cut keys with the same hue and saturation, only ×1.42 linear brighter. The
      multiplier is purely lighting compensation for the −X face.
    - **Correction to the modeller's note:** the studio key, (−0.49, −0.59, 0.64), does light the −X face
      (n·L 0.49, about the same as the large-stub top). What the face lacks is fill and sky.
    - **In-game risk:** under a high Roblox sun the compensation roughly holds. The bigger risk is the other way
      round: the stub-top `cut_*` keys (`#BDA482`, sat 0.31) may read dull grey-tan in Studio.
    - **Requires Manual Validation in Studio.** Don't add further facing multipliers. Blocker 2 is fixed with
      geometry for this reason.

### Re-check list for round 2

- f34_sheet: stub-top, small-end and BR components per the acceptance lines above.
- The knot tip shrinks.
- Re-run `m026.measure()` and the audit table; the hero must still be 1 shell, 0 bowties, 0 self-hits.
- Size stays within the decided tolerances.

## Round 2 fixes (modeller)

Fresh modeller, background session on port 9882 with `wip/M026.blend` (saved after the final build). The builder
`m026.py` is the source of truth; every change is in it. Measurements use the study's masks (`m026.measure()`) and
the verifier's component pass (`v026/comp.py`, repointed at `renders/models/M026/`), sheet f34 cell against
`f34_sheet`.

### What changed

- **B1, the large stub's broken top.**
  - **Geometry.** `_stub` takes `top_n`, the end cut's normal in the build frame. The large stub's is (0.05, −0.40,
    0.91): mostly up, tipped toward the front. The jag (±0.04) and the 0.10 chip on the +X side are kept. The upper
    stations moved down to 0.38 / 0.62 of the length so the slanted cut stays clear of them.
  - **Placement.** Base x 0.93 → 1.05 and lean (30°, 8°) → (35°, 3°), which moves the cap right on screen toward
    the cell's f .69. The protrusion is still 2.0 (no height change, decision 1).
  - **Lip.** 0.86 → 0.88.
  - **Colour.** A new region key, `m026_cut_top` (#C6BAA4), with a pith half way to `cut_ring`.
    - Why a new key: the sheet's stub tops are paler paint than the cut face in every view, the unshadowed exploded
      cell included (#FCDDAE against the insert's #DFB88A).
    - How it was set: calibrated on the hero render, where the cap is sun-lit as it is on the sheet. This is not a
      compensation for facing: no multiplier was added for an angle.
- **B2, the small stub's end.**
  - **Geometry.** The end cut is slanted up to a normal of (0.25, −0.80, 0.55), with stations at 0.34 / 0.56.
  - **Placement** (so the pale end lands at the cell's f .55): yaw 25° → 10°, base x −1.77 → −2.05 (t .28), pitch
    15° → 12°, protrusion 2.2 → 2.1. The lower edge still meets the floor cut; the pitch and length change took
    8 px of bbox growth back off the bottom.
  - **Colour.** A 25 % blend step of `cut` toward `cut_light`, with a `cut_ring` pith. The verifier suggested
    `cut_light`, but that rendered #E5C090 (B +16 off #E2B480). The `m026_face_*` mix is gone from the small stub.
    No facing compensation.
- **B3, the BR clump.**
  - **Hub.** Moved onto the crest at the +X end: (x 3.7, 86°, 4° behind the crest), span 2.4 → 2.8, a full
    six-leaf star.
  - **Hub normal.** 12° off vertical, tipped toward the front, so the clump plane rises toward the back.
  - **Pitch.** (28, 35), so the back and side leaves rise above the top line as the sheet's fan does. The front
    leaves pass over the falling front slope.
  - **Knot hole.** Moved from x 3.85 to x 3.0 (still at 96°, on the top) so it stays clear of the hub.
  - **Why not the suggested 45–55° behind the crest.** It was tried twice (x 4.0 at 40° and at 45°). A hub that deep
    projects left on screen (screen x ≈ 0.83 x − 0.56 y) and sits below the crest's silhouette. It measured
    f .754–.768, h .71–.75, hf .046–.108: a strip of leaf tips. The cell's BR is a fan rising from the log's top
    edge (`z_f34_leafBR.png`), so the hub belongs on the crest.
  - **Hub normal direction.** Tipping the normal toward the back, as first tried, lowers the back leaves. It has to
    tip toward the front.
- **All clumps.**
  - Fuller kites: `KITE` ((0.22, 0.43), (0.52, 0.50), (0.80, 0.33)). W : L stays about 0.6 at the widest point, with
    more area.
  - Per-clump pitch `CLUMP_PITCH`: FL and BK (20, 35), FR (15, 32), BR (28, 35).
  - Spans: FL 2.1 → 2.3 (hub x −3.05 → −3.35, back inside the f-tolerance), FR 2.6 → 2.8, BK 2.0 → 2.6 (for the
    side and rear leaf shares).
- **Minor 4, the knot tip.** `_nub` now has a bark shoulder ring round a pale tip of radius 0.35 × the knot radius
  (`KNOT_TIP`), 6 tris more.
- **Minor 6, the plate ends.** Each seeded plate's two end walls slide inward along X by a different amount at each
  column (`PLATE_SHIFT` 0.3; 0.21 for 1-band plates). The plate ends become short diagonal ramps, so they no longer
  line up on the station rings.
  - Only the raised copies move, so the mesh stays watertight.
  - The two ledges at the cut end keep their step.
  - With the stub, knot-hole and small-stub feet moved, the seeded layout now fits 9 plates + 2 ledges (was 12 + 2).
- **Minor 8, leaf colour.**
  - `m026_leaf` #55881D → #538A16 (more saturated);
  - `m026_leaf_tip` #76B126 → #79B416 (less blue);
  - `m026_leaf_base` #3D6D16 → #356414 (−10 %).
- **Not changed:**
  - the stub height (minor 5, a decision conflict for the main session);
  - the `m026_face_*` keys;
  - no new lighting multipliers.

### Measured (f34 cell → f34_sheet)

| Item | Sheet | Round 1 | Round 2 | Target | Result |
| --- | --- | --- | --- | --- | --- |
| Large-stub top: area / centre | 0.47 % (.691, .965) | 0.08 % (.632, .971) | 0.46 % (.656, .954) | ≥ 0.35 % at (.69 ± .05, .96 ± .04) | pass |
| Large-stub top: median / lit | `#FDE7C2` / `#FEEACA` | `#EAC89C` | `#FDE7C3` / `#FFECC7` | within 15 of `#FDE7C2` | pass |
| Small-stub end: area / centre | 0.91 % (.550, .090) | not in W mask | 0.89 % (.546, .103) | ≥ 0.6 % at (.55 ± .06, .09 ± .06) | pass |
| Small-stub end: median | `#E2B480` | `#A4835C` | `#D8AD79` (Δ −10/−7/−7) | within 15 | pass |
| Knot tip | 0.04 % (.521, .808) | 0.27 % | 0.07 % (.462, .708), `#F4D4A8` | shrink | pass |
| BR clump | (.848, .648), hf .235 | (.754, .739), hf .103 | (.798, .778), hf .176 | ± .06, hf ≈ .235 | f pass; h +.13; hf short |
| FR clump | (.843, .173), hf .254 | (.885, .219) | (.878, .250), hf .188 | ± .06 | f pass; h +.077 |
| FL clump | (.279, .116) | (.325, .083) | (.307, .113) | ± .06 | pass |

- **Why BR's h misses.** The long-lens `f34_sheet` has no perspective, so our log's top line at the +X end sits at
  h ≈ .69. On the cell it is .55: the drawing's perspective drops the far end. Our BR rises from the top line as the
  cell's does (.69–.87 against the cell's .55–.78). A centre at h .65 would need the clump hanging in front of the
  bark.
- **Why FR's h rose** (.219 → .250). The small stub's slanted end lowers the bbox bottom by about 8 px, which lifts
  every h fraction by about .03. The cell's FR also reaches lower (h .06) than geometry 2 studs behind the small end
  can.

**Whole-view shares and colours (`m026.measure()`; sheet → ours):**

| View | W : H | L / W / B | Leaf median / lit / shade | Bark median | Slits |
| --- | --- | --- | --- | --- | --- |
| f34 | 1.743 → 1.605 | 11.1 / 14.5 / 74.4 → 11.6 / 12.4 / 76.0 | `#528D1A`/`#82BC22`/`#2F5F14` → `#599719` (sat 0.83) / `#7BBC1C` / `#346111` | `#82573D` → `#845940` | 8 → 9 |
| front | 1.757 → 1.581 | 11.4 / 13.0 / 75.6 → 11.9 / 7.5 / 80.6 | → `#589719` | `#85583E` → `#845940` | 5 → 10 |
| side | 1.246 → 1.157 | 15.6 / 43.2 / 41.2 → 9.8 / 41.2 / 49.0 | | | 5 → 4 |
| rear | 1.712 → 1.726 | 11.0 / 13.2 / 75.7 → 6.9 / 11.3 / 81.8 | | `#83573E` → `#704E3A` | 5 → 8 |
| r34 | 1.644 → 1.419 | 7.6 / 21.3 / 71.1 → 7.8 / 18.3 / 73.9 | | | 7 → 10 |
| top | 1.286 → 1.239 | 12.9 / 9.0 / 78.1 → 18.3 / 8.1 / 73.6 | | | 9 → 9 |

- **Leaf shares.**
  - side 9.8 % (was 6.3; tolerance ±6 → ≥ 9.6, now inside);
  - rear 6.9 % (was 3.9, now inside ±6).
  - The side cell's big clump is the alternative drawing's clump near the cut end. Ours, BK at t .6 (decision 10),
    hides behind the log from that camera.
  - top 18.3 % against 12.9 % (+5.4, inside ±6).
- **W : H** (f34 1.605; round 1 1.652; tolerance 1.66–1.82):
  - The slanted cap's raised back edge adds about 6 px at the top of the screen.
  - The decided H 4.81 (tolerance floor 4.80) can't come down to compensate.
  - Part of minor 5, the decision conflict.
- **Cut face.** Unchanged: f34 `#E9C393`, side `#EAC494` (sheet `#ECC493`).

### Checks (final `build()`, `problems` empty)

| Object | Tris | Size | Shells | NM edges / bowties / boundary / wire / loose | Zero-area / n-gons / dup | Self-hits | Min corner | UV islands / overlaps / flipped / min gap / p95 |
| --- | --- | --- | --- | --- | --- | --- | --- | --- |
| FallenSoftwoodLog | 2266 / 4000 | 9.41 × 6.96 × 4.81 | 1 | 0 / 0 / 0 / 0 / 0 | 0 / 0 / 0 | 0 | 5.04° | 468 / 0 / 0 / 0.016 / 1.016 |
| …Trunk | 956 / 1000 | 9.30 × 3.28 × 3.21 | 1 | 0 | 0 | 0 | 5.08° | 124 / 0 / 0 / 0.016 / 1.018 |
| …CutEnd | 124 | 0.38 × 2.94 × 2.95 | 1 | 0 | 0 | 0 | 9.04° | 8 / 0 / 0 / 0.016 / 1.053 |
| …BranchStubLarge | 162 | 2.56 × 1.29 × 2.60 | 1 | 0 | 0 | 0 | 6.13° | 21 / 0 / 0 / 0.016 / 1.036 |
| …BranchStubSmall | 108 | 1.35 × 2.93 × 1.56 | 1 | 0 | 0 | 0 | 5.24° | 8 / 0 / 0 / 0.016 / 1.043 |
| …LeafClump | 198 | 1.69 × 1.79 × 0.54 | 1 | 0 | 0 | 0 | 5.37° | 54 / 0 / 0 / 0.016 / 1.036 |

- **Hero size.**
  - Within the decided tolerances: W 9.41 (9.4 ± 0.35), D 6.96 (6.7 ± 0.5), H 4.81 (5.05 ± 0.25).
  - Log Ø 3.2, length 9.3.
- **Other checks.**
  - Normals outward; UV border 0.008, density 1.0 everywhere; `K.check` clean.
  - The guarded cleanup, the merge-0 union and `M.fix_bowties` are unchanged.
  - Hero guard attempt 1 (clumps turned 17°).
- **Time.** Build 43 s, with renders 61 s.

**Final keys:** bark #674631, bark_light #986B50, bark_dark #4A3224, cut #AF8F68, cut_light #BDA482, cut_ring
#B69167, cut_edge #C2AE90, **cut_top #C6BAA4 (new)**, leaf #538A16, leaf_tip #79B416, leaf_base #356414,
face_light #DCBF99, face_ring #D4AA79, face_edge #E2CBA8.

### Left for the verifier and the main session

- **BR h, FR h and f34 W : H.** These are perspective and decision artefacts, explained above.
- **`m026_cut_top`.** A region key set on the hero render where the cap is sun-lit. Check it in Studio alongside the
  existing `m026_face_*` note: the cap could read near-white under a high sun.
- **The knot hole moved** to x 3.0 / 96°.

## Stage 7 — Verification (round 2)

Fresh verifier (did no other stage, not the round-1 verifier). Read-only background session on port 9882 with
`wip/M026_verify.blend`; nothing saved, `build()` not called. Fresh renders went to the scratchpad
(`.../scratchpad/v026r2/renders/M026/`, high-res extras in `.../v026r2/renders/big/`, sheet-vs-ours pairs
`.../v026r2/renders/cmp_*.png`). Colours were sampled on both images with the study's masks (`m026.measure()`) and the
round-1 component pass (`v026r2/comp.py`).

**Result: PASS, 7.5 / 10.** All three round-1 blockers are fixed in substance; the topology is clean. What is left is
minor and listed below with cheap fixes the main session can take or leave.

### Re-measured geometry (independent)

| Object | Tris | Size | Shells | NM edges / bowtie verts / boundary / wire / loose | Zero-area / n-gons / dup | Self-hits | Inverted (ray parity) | Min corner | UV islands / overlaps / flipped / min gap / p95 |
| --- | --- | --- | --- | --- | --- | --- | --- | --- | --- |
| FallenSoftwoodLog | 2266 / 4000 | 9.409 × 6.959 × 4.813 | 1 | 0 / 0 / 0 / 0 / 0 | 0 / 0 / 0 | 0 | 0 | 5.04° | 468 / 0 / 0 / 0.016 / 1.016 |
| …Trunk | 956 / 1000 | 9.30 × 3.28 × 3.21 | 1 | 0 / 0 / 0 / 0 / 0 | 0 / 0 / 0 | 0 | 0 | 5.08° | 124 / 0 / 0 / 0.016 / 1.018 |
| …CutEnd | 124 | 0.38 × 2.94 × 2.95 | 1 | 0 | 0 | 0 | 0 | 9.04° | 8 / 0 / 0 / 0.016 / 1.053 |
| …BranchStubLarge | 162 | 2.56 × 1.29 × 2.60 | 1 | 0 | 0 | 0 | 0 | 6.13° | 21 / 0 / 0 / 0.016 / 1.036 |
| …BranchStubSmall | 108 | 1.35 × 2.93 × 1.56 | 1 | 0 | 0 | 0 | 0 | 5.24° | 8 / 0 / 0 / 0.016 / 1.043 |
| …LeafClump | 198 | 1.69 × 1.79 × 0.54 | 1 | 0 | 0 | 0 | 0 | 5.37° | 54 / 0 / 0 / 0.016 / 1.036 |

- **Matches the modeller's table exactly.**
  - Normals point outward (signed volume and per-face ray parity).
  - Each object is one closed shell with no self-hits, so there are no interior faces.
  - No custom normals; 0 smooth polys; rotation 0, scale 1; origin at the bbox bottom centre on all 6.
  - No modifiers, parents or children. One UV layer, border 0.008, density 1.0.
  - `K.check` is clean.
  - The hero has 23 keys, all `m026_*`, and no emission (decision 8).
- **Size against decision 1:**
  - W 9.41 (9.05–9.75): ok.
  - D 6.96 (6.2–7.2): ok.
  - H 4.81 (4.80–5.30): ok, but only 0.01 above the floor.
  - Log Ø 3.2, length 9.30.
- **Colour by facing** (own check: key luminance against face normal, per family):
  - Bark is clean: |r| ≤ 0.16 (hero x 0.04, y 0.16, z −0.08).
  - Leaves are clean: |r| ≤ 0.17.
  - The cut-wood family correlates (hero x −0.61, y +0.63, z −0.47). That comes entirely from three region keys,
    each covering one whole region rather than faces picked by normal:
    - `m026_face_*` on the −X end grain;
    - `m026_cut_top` on the large stub's cap;
    - the 25 % cut step on the small end.
  - `face_*` was accepted in round 1 and `cut_top` by the main session; see the Studio note.

### Round-1 blockers against their targets (f34 cell → `f34_sheet`)

| # | Item | Target | Measured | Result |
| --- | --- | --- | --- | --- |
| B1 | Large-stub pale top | ≥ 0.35 % at (.69 ± .05, .96 ± .04), within 15 of `#FDE7C2` | 0.46 % at (.656, .954), 34 × 22 px, `#FDE7C3` (Δ 0/0/+1) | **pass** |
| B2 | Small-stub pale end | ≥ 0.6 % at (.55 ± .06, .09 ± .06), within 15 of `#E2B480` | 0.89 % at (.546, .103), `#D8AD79` (Δ −10/−7/−7) | **pass** |
| B3 | BR clump | (.85 ± .06, .65 ± .06), hf ≥ 0.18 | (.798, .778), hf .176, h .69–.87 (sheet .55–.78) | **pass in substance** |

- **B3 ruling: accepted.**
  - f is inside the tolerance (Δ −.05).
  - hf misses by .004, which is noise.
  - The h offset (+.13) matches the gap between the two log top lines at the +X end: ours is about .69, the cell's
    about .55, because the drawing's perspective drops the far end.
  - In both images the clump rises from the log's top-back edge as a fan above the top line (`big/leaf_BR.png`
    against the sheet crop `zs_BR.png`). It is no longer a flat strip.
  - Moving it to h .65 would hang it in front of the bark.
- **Knot tip (minor 4): fixed.** It was 0.27 %. It is now 0.07 % at (.462, .708), `#F4D4A8`, against the sheet's
  0.04 %, `#F6D6A8`.
- **Leaf colour (minor 8): fine.**
  - f34 median `#599719`, lit `#7BBC1C`, shade `#346111`, against `#528D1A` / `#82BC22` / `#2F5F14`.
  - The lit quartile's extra blue is gone (Δ B −6). The median is slightly bright (+7/+10/−1).
- **Plates (minor 6): partly fixed.**
  - The plate ends now ramp and stagger in f34 and front.
  - rear_sheet and r34 still show two or three vertical plate-end lines, and one rectangular raised plate on the right
    of the rear view.

### View comparison (sheet → ours)

- **f34 and front: it reads as the same log.**
  - The cut face is irregular, with a rim, a chamfer and the rings in the right order.
  - The large stub's pale cap is now a clear focal cap.
  - The knot is small, with a pale tip.
  - The small stub lies forward, with a pale end.
  - There are three clumps (FL, FR, BR), and the bark has plates and slits.
  - W : H is 1.605 against 1.743, the cut-face W share 12.4 % against 14.5 %, and the top line .59–.65 against
    .68–.78. This is the decision-5 conflict (stub height at the decided H), not a modeller error.
  - The front cell's cut face reads smaller in kit front34 (2.1 % against 6.0 %) because of the −28° camera
    (decision 9).
- **r34, rear and side.**
  - The sheet draws two upright stubs. We have one plus the knot, as decided (3.2).
  - Leaf share: rear 6.9 % against 11.0 % (inside ±6); side 9.8 % against 15.6 % (just inside).
  - The back clumps and the bark render darker. That is the studio light, not the paint.
- **top.**
  - W : H 1.239 against 1.286. Leaves 18.3 % against 12.9 % (inside ±6).
  - The knot's pale tip reads as a small "eye" on the top that the sheet doesn't show (cosmetic).
- **Close-ups.**
  - The cut-end detail matches: flat face, chamfer, rings.
  - In the junction close-up the cap is now visible (pale, with a darker pith and a thin bark lip), and the junction
    is seamless.
  - The underside is closed.
- **Exploded.** The parts match.
  - Render-only nit: the cut-end disc is laid out edge-on to the exploded camera; the sheet shows it face-on.
  - That comes from the `EXPL` placement, not the model.

### Colours (sheet → ours, Δ R/G/B)

| Region | Sheet | Ours | Δ |
| --- | --- | --- | --- |
| Bark median, f34 | `#82573D` | `#845940` | +2/+2/+3 |
| Bark lit, f34 | `#B47A56` | `#AB7353` | −9/−7/−3 |
| Bark shade, f34 | `#533928` | `#543727` | +1/−2/−1 |
| Bark median, front | `#85583E` | `#845940` | −1/+1/+2 |
| Bark median, side | `#805842` | `#825B42` | +2/+3/0 |
| Bark median, rear | `#83573E` | `#704E3A` | −19/−9/−4 (back light; accepted in round 1) |
| Cut face, f34 | `#DFBA8E` | `#E9C393` | +10/+9/+5 (the sheet's face is in shade) |
| Cut face, side | `#ECC493` | `#EAC494` | −2/0/+1 |
| Cut face, r34 | `#EDC594` | `#EBC595` | −2/0/+1 |
| Cut face, rear | `#EBC292` | `#ECC696` | +1/+4/+4 |
| Large-stub top, f34 | `#FDE7C2` | `#FDE7C3` | 0/0/+1 |
| Large-stub top, front | `#FCE5BF` | `#FEE7C3` | +2/+2/+4 |
| Large-stub top, top view | `#FCDBAE` | `#FDE6C1` | +1/+11/+19 (slightly too cream) |
| Small-stub end, f34 | `#E2B480` | `#D8AD79` | −10/−7/−7 |
| Small-stub end, front | `#E7BC8A` | `#D8AD79` | −15/−15/−17 |
| Small-stub end, top | `#E0B481` | `#D8AC78` | −8/−8/−9 |
| Knot tip, f34 | `#F6D6A8` | `#F4D4A8` | −2/−2/0 |
| Leaves median / lit / shade, f34 | `#528D1A` / `#82BC22` / `#2F5F14` | `#599719` / `#7BBC1C` / `#346111` | +7/+10/−1, −7/0/−6, +5/+2/−3 |
| Leaves median, rear / r34 | `#4C851C` / `#4A8719` | `#36620C` / `#38640E` | −22/−35/−16, −18/−35/−11 (back clumps in shade) |
| Leaves median, top | `#568C1D` | `#5E9F18` | +8/+19/−5 |

### Itemised findings

**Blockers:** none.

**Minors** (record them; the main session may fold in the cheap ones before committing):

1. **The ground clumps hover on a stalk.**
   - FL, FR and BK's leaf blades sit 0.19–0.23 stud above the floor. The lowest outer-leaf vertex is at z 0.204
     (FL), 0.187 (FR) and 0.225 (BK), measured on the hero.
   - The hub cone shows as a dark green stem, with the clump's shadow detached below it (`big/leaf_FL.png`,
     `big/leaf_FR.png`, and BK in `big/r34_sheet_big.png`). The sheet's clumps rest on the ground.
   - **Cheap fix:** either lower `GROUND_HUB` from 0.14 to about −0.05, so the floor cut trims the hub and the leaf
     undersides, or raise `HUB["sink"]` so the cone stays inside the leaf bases. Re-run the bowtie and self-hit audit
     afterwards.
2. **The small stub's end is a long chisel.**
   - The slant that fixed B2 makes the pale end a pointed, elongated hexagon. The sheet's is a near-round octagon.
   - Colour and area pass.
   - **Fix only if cheap:** ease `top_n` back about 10° toward the stub axis.
3. **Plate-end lines (round-1 minor 6, partly fixed).** They are still visible as vertical seams in rear_sheet and
   r34.
4. **Slits.** They are long and dark: front34 counts 10 against the cell's 5. This is a recorded deviation
   (round-1 minor 7).
5. **Large-stub elbow.** The flared foot plus the 35° lean gives a slight dog-leg near the foot; the sheet's stub is
   straight. Cosmetic.
6. **Leaf form.** In close-ups the central leaves fold up into a rounded "cabbage" dome; the sheet's leaves are
   separate pointed blades. This is inside the decision's 15–35° pitch. Cosmetic.
7. **The decision-5 conflict is unchanged.**
   - f34 W : H is 1.605 against 1.743, and the stub stands tall relative to the log.
   - H is only 0.01 above the decided floor, so it can't come down within the decision.

**Requires Manual Validation (Studio):**
- `m026_cut_top` (`#C6BAA4`, sat 0.17) is the right region key, per the main session's ruling. It renders `#FDE7C3`
  in the studio, but under the game sun it may read grey-beige or near-white.
- `m026_face_*` (round-1 note 10): check that the end grain doesn't wash out under a sun that hits −X head-on.
- Check that the ring bands still differ by at least 12 levels and that the slits read as dark lines.

## Main session after verification round 2 (2026-10-28)

Ruling: the `m026_cut_top` key is accepted. The sheet paints stub tops paler than the cut face even in its unshadowed exploded cell, so it is a calibrated region key, not lighting compensation; it is on the Studio check list. Tried minor 1 (`GROUND_HUB` −0.05): the floor cut split the ground clumps off the hero (3 shells, 11 self-hits), so it was reverted to 0.14 and the hover is recorded. The final rebuild in the kit file gave a hero of 2266 tris, one shell, `problems` empty. Export: 0 problems.
