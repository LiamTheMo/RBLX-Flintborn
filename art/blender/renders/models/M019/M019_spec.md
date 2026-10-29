# 019 Resin Node — spec

Reference: `art/blender/assets/references/019.png`. The sheet's own title is "23 — RESIN NODE", with the footer "FLINTBORN — INDIVIDUAL
MODEL STUDY, PAGE 23/132". INDEX.md row 19 calls it "Flintborn Resin Node study". The image is 1024 × 1536 px.
Builder: `art/blender/kit/mcp/m019.py` → `build()` (stages 1–6 recorded at the end of this file). Procedure: `art/blender/kit/mcp/STAGES.md`
(three agents: Build = stages 1–3, Finish = stages 4–6, Verify = stage 7).

User direction for every model: shapes must match the sheet; colours "need to match the master reference and blend
into the colors nearby. please ensure all color and textures are being made and applied." Effects ship wherever the
sheet shows them. This sheet shows a sparkle overlay (§7).

Sheet text:
- **Modeling notes:**
  - "Keep low polygon, chunky shapes with broad flat-shaded faces."
  - "Use simple, solid colors—no texture noise or gradients" (but see §3.9).
  - "Model as separate, reusable parts: main branch body, resin lumps, leaf clumps, and cut end inserts."
  - "Resin lumps are distinct geometry, attached to branch surfaces."
  - "Leaf clumps are simple, low-poly clusters."
  - "Maintain clean silhouettes and readable forms from all angles."
  - "Keep geometry consistent across all views."
- **Palette:** Wood (Bark), Wood (Inner), Resin, Cut End Wood, Leaves.
- **Exploded labels:** Leaf Clump (×5 drawn), Resin Lump (Large), Resin Lump (Small), Main Branch Body, Branch Cut End
  (2 drawn floating, 4 drawn attached).
- **Close-ups:** "Branch Junction (Close-Up)"; "Resin Attachment (Underside)", with the caption "Flat Join Surface";
  "Cut End Detail", with the caption "Thick, Faceted End".
- **VFX overlay (optional):** "Simple stylized sparkle VFX (separate from geometry). No glow baked into model."
- **Game context:** the game has no resin node (`src/shared/Resources/NodeCatalog.luau` has no Resin entry), but GDD.md
  lists Resin as an uncommon harvest. The old R06 kit sheet has a `ResinNode` (11.7 × 11.6 × 8.8, 576 tris), which
  owns the `ResinNode*` names (§8).

**Pixel boxes and masks.** All pixel boxes are sheet pixels `(x0, y0, x1, y1)`, with the origin at the top left. The
paper is `#F2EDE7` (242, 237, 231). The masks are defined in `m.py` `cls()` and work in HSV:
- **L, leaves:** sat ≥ 0.25, hue 62–150°, g > 50.
- **R, resin:** hue 20–52°, sat ≥ 0.66, v ≥ 0.50. Also the pale-yellow resin highlight facets: hue 40.5–56°,
  sat ≥ 0.42, v ≥ 0.90.
- **C, cut-end wood:** hue 18–52°, sat 0.12–0.66, v ≥ 0.78. This includes the join pads.
- **B, bark:** sat ≥ 0.16, hue ≤ 48° or ≥ 340°, v < 0.78.
- **O, other:** the ground shadow and dark edges. Not counted in the shares.

**Scratch study material.** Pure Python with no Blender. It is in the session scratchpad
`C:\Users\Orang\AppData\Local\Temp\claude\D--Projects-Roblox-RBLX-Flintborn\3f83a1be-3b3d-4e4b-ae5a-7b04dbb75bdc\scratchpad\m019_study\`.
Run the scripts with `C:/Users/Orang/.local/bin/python3.14.exe`.
- **Helpers and measurements:**
  - `png.py`: PNG reader and `crop`.
  - `m.py`: the masks and the view boxes `V`.
  - `bb.json`: silhouette boxes.
  - `measure.py`, with its output in `measure_out.txt`: shares, top/bottom profiles and width per height.
  - `comps.py`: lump, cut-end and clump components per view. `expl.py` does the same for the exploded view and the
    close-ups.
  - `samp.py`, `samp2.py`, `samp3.py`: swatches; region medians, quartiles and deciles; lump thirds; cut-end rings;
    leaf base and tips; bark bands.
  - `spark.py`: the VFX sparkles.
- **Layout fitting:** `fit.py` fits the top view and the f34 under the kit front34 camera. `proxy.py` and
  `proxy3.py` hold the layout proxy, projected into every kit camera.
- **Crops:** `f34.png`, `r34.png`, `front.png`, `side.png`, `rear.png`, `top.png`, `expl.png`, `cu_junc.png`,
  `cu_under.png`, `cu_end.png`, `pal.png`, `vfx.png` and `notes.png`.
- **Grids and mask previews:** grids `g_*.png` (a 10 % grid on the silhouette bbox); mask previews `cls_front.png`,
  `cls_top.png`, `cls_f34.png`, `cls_rear.png` and `cls_side.png`.
- **Zooms:**
  - Exploded view: `z_expl_body.png`, `z_expl_biglump.png`, `z_expl_leafB.png`, `z_expl_leafTR.png`,
    `z_expl_leafL.png`, `z_expl_bottom.png`.
  - Front three-quarter: `z_f34_biglump.png`, `z_f34_small_top.png`, `z_f34_bend.png`.
  - Close-ups and VFX: `z_cu_junc.png`, `z_cu_under.png`, `z_cu_end.png`, `z_vfx.png`.
- **To run the scripts on our renders,** point `R` (in `m.py`) at the render and set `P` to the render's background
  colour.

## 1. Study (2a)

### 1.1 Classification, what it is, size

- **Classification:** full asset (a resource node). The hero budget is 4000 tris and each part must stay under 1000.
  The plan in §4.3 lands at about 1900–2200.
- **Overall read (check this first).** The object is one cohesive fallen, forked branch lying in an X. It must not read
  as a pile of separate logs and balls. The pieces:
  - **A, the main limb.** A thick limb lies on the ground at the front-left (A_low), runs into a fused fork (the
    junction J) and rises from J as a steep arm (A_up, about 45°) to a pale cut end at the back-right. A_up's cut end
    is the tallest wood point.
  - **B, the lying log.** A second log lies across A, from a low back-left end through J to a cut end on the ground
    at the front-right.
  - **C and D, two stubs.** C rises from J toward the back and carries a leaf clump. D rises from B toward the right
    and carries the small resin lump and a leaf clump.
  - **Two chunky orange resin lumps** sit on the wood. The large one (about 2.5 log diameters) straddles A_low at the
    front-left. The small one (about 1.7 log diameters) sits high on D at the right, beside A_up.
  - **Five small bright-green leaf clumps** (five-leaf stars) tuck into the X's notches and the stub tips.
  - **Every log end is a thick, faceted, cream cut-end insert** with faint rings.
  - In the hero, the resin is about 30 % of the silhouette, the bark about 49 %, the leaves 16 % and the cut ends 6 %.
- **Focal silhouettes, in order:**
  1. The two resin lumps' outlines: rounded 8–10-corner polygons made of broad facets, not jewels and not balls.
  2. A_up's diagonal with its cut end on top.
  3. The B log running down to its round cut end at the front-right.
  4. The leaf clumps' broad pointed leaves.
- **Target size: about 7.0 W × 5.9 D × 4.45 H studs** (H = 0.81 of the 5.5-stud character). Log diameter is about 1.05–1.2,
  the large lump is 2.7 across and the small lump 1.8. Tolerances: W ±0.35, D ±0.35, H ±0.2. This is the sheet's own
  proportions × 1.2; decision §8.1.
  - **How it was derived.** The sheet has no character. The natural anchor is the log: the B front cut end measures
    66 px and the A top cut end 63 px in the f34 cell. At 74 px per stud (f34 cell) that makes the logs Ø 0.89, the
    large lump 2.24 (166 px), the small lump 1.49 (110 px) and the node about 5.85 × 4.9 × 3.7. That is 0.67 C tall:
    a knee-to-waist pile.
  - **Why × 1.2.** WorldModeling §3.2 has no row for a log/resin node, and the design doc only says to size against
    the character. A harvestable must read at gameplay distance, so the lumps (the target) should be about 2.7 / 1.8,
    and the node then sits between M017 Berry Bush (6 × 4.8 × 5) and M012 Amber (9 × 7.2 × 7).
  - **Repo neighbours.** R06 `ResinNode` is 11.7 × 11.6 × 8.8 (too big for a branch pile); R06 `CutLog` 8 × 2.4 × 2.4.
    Our logs are branches, so they are thinner.
- **Build frame:** front −Y, +X right, ground z 0, origin = the plan centre of the layout (§2). Re-centre to the
  bbox bottom centre in stage 2.

### 1.2 Measured views (`measure.py`, `comps.py`)

| View (box) | Silhouette bbox (px) | W : H | Leaves L | Resin R | Cut C | Bark B |
| --- | --- | --- | --- | --- | --- | --- |
| Front three-quarter (15,105,510,450) | 51–476 × 107–430 | 1.316 | 15.6 % | 30.2 % | 5.6 % | 48.7 % |
| Rear three-quarter (515,105,1010,450) | 560–979 × 110–439 | 1.274 | 18.4 % | 16.9 % | 5.2 % | 59.5 % |
| "Front" (15,495,285,712) | 28–266 × 506–695 | 1.259 | 15.8 % | 30.0 % | 5.6 % | 48.6 % |
| Side (288,495,512,712) | 325–480 × 506–698 | 0.807 | 13.3 % | 45.3 % | 3.9 % | 37.6 % |
| Rear (515,495,772,712) | 542–752 × 510–696 | 1.129 | 26.4 % | 24.9 % | 6.5 % | 42.2 % |
| Top (775,495,1012,712) | 808–1000 × 519–691 | 1.116 (W : D) | 17.7 % | 28.4 % | 8.9 % | 44.9 % |

- **The "Front" cell is the f34 drawing again,** at 0.56 scale. All its parts sit at the same fractions (big lump
  f .197/.193, small lump .794/.789, A top end .691/.692, B front end .940/.939, the four clumps likewise). The sheet
  has **no true front orthographic** (§3.1).
- **Verifier check:** shares ±4 points (C ±2); positions ±0.06 of W/H unless stated otherwise.

**Top profiles.** The highest silhouette pixel per column, as a fraction of H, every 0.05 f:

| f | .00 | .05 | .10 | .15 | .20 | .25 | .30 | .35 | .40 | .45 | .50 | .55 | .60 | .65 | .70 | .75 | .80 | .85 | .90 | .95 | 1.0 |
| --- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- |
| f34 | .25 | .50 | .58 | .62 | .82 | .80 | .78 | .80 | .74 | .70 | .77 | .85 | .93 | .96 | .98 | .98 | .94 | .99 | 1.0 | .81 | .14 |
| r34 | .60 | .83 | .83 | .78 | .79 | .81 | .77 | .71 | .71 | .79 | .88 | .93 | .96 | .98 | .93 | .98 | 1.0 | .81 | .34 | .23 | .13 |
| Side | .36 | .43 | .49 | .53 | .57 | .62 | .63 | .74 | .71 | .82 | .93 | .97 | .99 | .99 | .97 | .90 | .91 | .95 | .96 | .97 | .78 |
| Rear | .32 | .68 | .70 | .69 | .96 | .99 | .99 | .96 | .95 | .89 | .83 | .85 | .90 | .98 | .92 | .87 | .89 | .91 | .63 | .62 | .52 |
| Top (h = back) | .88 | .93 | .95 | .94 | .91 | .87 | .83 | .85 | 1.0 | .98 | .94 | .91 | .92 | .83 | .87 | .90 | .91 | .88 | .83 | .55 | .51 |

**Width per height.** Silhouette width / W at h = 0.0, 0.1 … 1.0; the start f follows the @.

```
f34    .01@.65 .97@.03 .97@.01 .85@.01 .80@.02 .84@.05 .79@.12 .66@.23 .76@.20 .32@.58 .03@.92
r34    .02@.90 .96@.03 .94@.04 .80@.05 .78@.05 .74@.07 .82@.00 .70@.09 .81@.05 .28@.51 .01@.80
side   .15@.32 .83@.05 .86@.01 .79@.01 .68@.03 .85@.11 .71@.26 .59@.32 .52@.45 .48@.48 .02@.61
rear   .02@.82 .79@.05 .86@.00 .78@.00 .85@.07 .95@.05 .90@.07 .74@.09 .64@.21 .67@.20 .01@.27
top    .02@.79 .44@.47 .82@.07 .83@.03 .92@.03 .92@.08 .86@.05 .81@.08 .90@.00 .80@.02 .02@.39
```

- **Ground contact (f34 bottom profile).** The pile touches the ground almost everywhere from f .05 to .95, at h .00–.06.
  There is no see-through gap under the logs in the hero; the junction underside is hidden by the front clump.
- **f34 masses.** Below h 0.6 the pile is wide (0.80–0.97 W). Above h 0.8 only A_up's top and the TR clump remain
  (0.32 W at h .9, starting at f .58).

**Components** (`comps.py`): centre (f, h), size as a fraction of W × H.

| View | Large lump | Small lump | Cut ends (centre f, h) | Leaf clumps (centre f, h) |
| --- | --- | --- | --- | --- |
| f34 | .193, .380; .39 × .50 | .789, .583; .26 × .35 | A top .692, .909 (.148 W); B front .939, .118 (.132 × .204) | TL .297, .708; F .559, .104; R-low .787, .379; TR .857, .863 |
| Top | .218, .360; .40 × .45 | .738, .366; .26 × .32 | B back .075, .874; A top .808, .803; B front .836, .076 | L .110, .602; back .473, .845; F .478, .206; right .884, .511 |
| r34 | .155, .382; .24 × .34 | .705, .569; .25 × .36 | .250, .773 (raised); .603, .910 (top); .944, .110 (ground) | .107, .660; .260, .162; .751, .850; .821, .381 |
| Rear | .193, .242; .40 × .47 | .602, .345 (half hidden) | .291, .945 (top-left); .907, .514 (right, mid-height) | .155, .590; .710, .801; .733, .183 |
| Side | .296, .322; .61 × .52 | .827, .555; .28 × .31 | .610, .927 (top) | .341, .651; .791, .156; .864, .826 |

### 1.3 Silhouette and composition per view

**Front three-quarter (the hero, governs; `g_f34.png`).**
- **A_up:** a thick log rising from the junction (about f .50, h .30) to its cut end at the top (f .69, h .91; the
  disc 63 × 54 px, face toward the camera and up). On screen it looks about 50° steep.
- **Large lump:** at the left, f .005–.39, h .13–.63, an irregular rounded 9-corner outline. Its lower half sags
  over the front of A_low.
- **Bark tip at the far left:** a sliver of bark at f 0.0, h .22 pokes out under the large lump's left edge: B's
  back end (§2).
- **B:** runs from behind A_up at the junction down to the lower right. Its 10-sided cut end faces camera-right
  (f .94, h .12; 56 × 66 px), and its underside is on the ground.
- **Small lump:** at the right, against A_up's right flank (f .66–.92, h .41–.76), with pale highlight facets at its
  top-left.
- **Leaf clumps:**
  - TL (behind and above the large lump, f .19–.40, h .60–.83);
  - TR (beside A_up's top, f .76–.97, h .72–1.0, the top-right extreme);
  - R-low (below the small lump, poking right, f .71–.87, h .32–.44, in shade);
  - F (on the ground in front of the junction, f .45–.66, h 0–.21, leaves pointing at the camera).
- **Bark facets:** 3 faces show across each log (lit top, mid side, dark underside). The facets are long and split
  into big irregular triangles along the log, with a slight taper (`z_f34_bend.png`).

**Top (`g_top.png`; image top = back).** An **X**:
- B runs back-left → front-right. Its back-left cut end (f .075, h .874) and its front-right cut end (.836, .076)
  both show as cream ellipses.
- A_up's cut end is at the back-right (.808, .803), seen nearly face-on: A_up rises toward it.
- The large lump covers the front-left arm (.218, .36). The small lump is right of centre (.738, .366).
- The clumps sit in the four notches: back (.473, .845, the biggest), right (.884, .511, elongated front-to-back:
  TR plus R-low), left (.110, .602, small) and front (.478, .206).

**Rear three-quarter (`g_r34.png`).** Three cut ends: a raised one at the left (.25, .77), the top one (.60, .91) and
a ground one at the far right (.944, .11). It matches the kit rear34 **flipped left-right** (§3.3).

**Rear (`g_rear.png`; camera at +Y, screen right = −X).**
- A_up's cut end is at the upper left (+X) ✓ (it is at +X).
- B's back end shows at the right (−X) with its cut face toward camera-right, centred at h .51 (raised; §3.2).
- The lumps are swapped: the large lump is at the lower left (+X), the small one half hidden under B at the centre
  right (§3.4).
- Three clumps.

**Side (`g_side.png`).** A narrow (0.81) drawing: one near-vertical log with its cut end on top, the large lump at the
lower left, the small lump at the right, three clumps. No camera reproduces it from an X-shaped footprint (§3.5).

**Close-ups.**
- **Branch Junction** (706,800,1005,940): the fork's crotch is filled with broad facets, so the bark flows from one
  arm into the other (no cylinder-through-cylinder seam). The small lump sits right of the junction with a clump
  behind it.
- **Resin Attachment (Underside)** (706,985,1005,1123): from below, the lump sits on a **tan hexagonal block**
  (67 × 83 px against the lump's 121 × 99): a flat cut face, the "Flat Join Surface", standing slightly proud of the
  bark. It is cut wood, more saturated than the ends (`#E4AA65`, §5.2).
- **Cut End Detail** (706,1165,1005,1273): the disc is a **10-sided thick insert**, the same Ø as the bark, protruding
  about 0.15 Ø past a thin darker bark lip. Its face is faintly faceted with 2 subtle concentric ring bands
  (§5.3, "Cut ends").

### 1.4 Parts (Exploded Asset Breakdown (15,770,690,1280), `expl.png`, `z_expl_body.png`)

Scale: the exploded cut-end discs measure 62–64 px, which is log Ø 0.89 → **about 70 px per stud** (× 1.0). Facet
language: broad flat-shaded facets, irregular triangles, no smoothing.

#### Main Branch Body (182,820,528,1119), 347 × 300 px

- **What the body is.** Two crossing logs plus two stubs, fused into one body.
  - **A, the big rising log.** Thickest at its lower-left section, which lies on the ground; it ends in a floating
    cut-end disc (174,1125,236,1196). A rises to the upper right to an attached cut end (390,807,454,859; 64 × 52 px).
  - **B, the lying log.** It comes from behind A and runs to the lower right, ending in an attached cut end
    (481,1041,538,1113) plus a floating disc (564,1129,628,1203). Its back end is hidden behind A.
  - **C, a short stub.** It rises steeply up-left from behind A (240,854–277,876 is its cut end, 38 × 23) and has
    a dashed leader to the top-left leaf clump.
  - **D, a short stub.** It rises from B toward the upper right, parallel to A (its cut end 467,885–501,913), with
    a dashed leader to the small lump.
- **Dashed join outlines.** A dashed **hexagon on A's upper-left flank**, just above the crossing, is where the large
  lump attaches. A dashed patch on D's right flank is where the small lump attaches. Both are the "Flat Join Surface".
- **Proportions** (at 70 px/stud × 1.0):
  - A lower section Ø about 1.05 (75 px), A top Ø 0.9;
  - B Ø 0.85–0.9;
  - C Ø 0.75 (55 px) → 0.55 at its end;
  - D Ø 0.65 → 0.6.
- **Construction:**
  - **Log tubes:** `_log(path, radii, sides=8, seed)` builds 8-sided tubes along 4–6 rings. Ring radius ±6 %,
    ±10° twist per ring, vertex jitter ±0.04, beauty triangulation (the sheet's irregular triangles), and a slight
    taper toward each end.
  - **The junction:** a hull **knot** of about 12 points, Ø 1.3 × log Ø, at J fills the crotch the way the close-up
    shows. Everything is joined with one exact union.
  - **Ends:** each log end is a flat plane perpendicular to the axis (oblique for B's back end, §2), with a 4 % bark
    lip flare. The cut-end insert is unioned onto it.
- **Triangles:** about 110 (A, bent) + 100 (B) + 45 (C) + 40 (D) + 30 (knot) + 48 (2 join pads) ≈ 375 before the union,
  about 450–520 after.

#### Branch Cut End: floating discs (174,1125,236,1196) 62 × 71 px and (564,1129,628,1203) 64 × 74; close-up (817,1168,909,1271)

- **Shape:** a **10-sided** thick disc (9–11 is acceptable), Ø = 0.95 × the bark end. Thickness 0.20 Ø, of which
  0.08 Ø stands proud of the bark lip. The face is very slightly domed (centre +0.03 Ø) and broken into
  2 concentric ring bands.
- **Construction:** `_cut_end(r, seed)`:
  - face loops at 0.22, 0.38, 0.62, 0.78 and 1.0 R (centre fan + 4 bands), so the rings are real edges for §5.5;
  - one side band;
  - the back face is left in the bark (removed by the union);
  - loop radii jitter ±3 %, so the outline is a faceted polygon, not a perfect circle.
- **Triangles:** 10 + 4 × 20 + 20 = **110**. Six caps on the hero (A_low end, hidden under the large lump; A_up end;
  B back end; B front end; C end; D end). Option: 1 ring band, 70 tris (decision §8.4).

#### Resin Lump (Large): exploded (88,899,228,1047) 140 × 148 px; hero f34 166 × 162

- **Shape:** a chunky, rounded, broad-faceted nodule, **W : H ≈ 1.0** (f34 1.02; exploded 0.95). In the hero
  silhouette it is an irregular 8–10-corner polygon. The faces are big flat pentagons, hexagons and quads, each
  subtly split into 3–5 triangles of slightly different tone (`z_f34_biglump.png`). There is a pale, nearly
  pentagonal top face.
- **Size:** **Ø 2.7** (× 1.2; 2.24 × 1.0). That is 2.3–2.5 log diameters in the hero (the exploded's 2.2 is drawn
  smaller; the hero governs).
- **Construction:** `_lump(radius, seed, n)`:
  - the convex hull of **n ≈ 26** jittered Fibonacci-sphere points, radius ±6 %, squash (1.0, 0.95, 0.93);
  - this gives about 48 big triangles, which pair into about 20 broad faces;
  - then **poke the ~10 largest faces** with the centre raised +2.5 % R, giving the sheet's within-face facets;
  - result about **70–90 tris**. Check that the silhouette has 8–10 corners from front34 and that no face is a sliver.
- **Not** an ico-2 (a smooth ball) and **not** a bare icosahedron or dodecahedron (a jewel; WorldModeling §18
  "looks like jewels").

#### Resin Lump (Small): exploded (518,914,591,996) 73 × 82 px; hero f34 110 × 112

- **Shape:** the same family, slightly more triangulated. The f34 shows a 5-triangle fan at its centre-left (an
  ico-like vertex). W : H 1.0.
- **Size:** **Ø 1.8** (× 1.2; 1.49 × 1.0) = 0.66 of the large lump (f34 .66, front .67, top .64). The exploded's 0.52 is
  overruled.
- **Construction:** `_lump(0.9, seed, n=20)` → about 36 tris, poke about 6 faces → about 50–60.

#### Resin join pad (the "Flat Join Surface"; underside close-up (827,1013,894,1096))

- **Shape:** a 6-sided prism. Ø = 0.5 × the lump Ø (the close-up's 67 px against 121), standing 0.2 proud of the bark
  along the line from the log axis to the lump centre. The lump is centred on its face and sunk 0.15 Ø into it.
- **Visible part:** only its rim and underside, below the lump. This is the contact surface WorldModeling §6.7 asks
  for ("Give it a contact surface; do not suspend it in front of a tree").
- **Construction:** `_pad(r, h)`: 6 sides, 24 tris, part of the Main Branch Body.

#### Leaf Clump: exploded (65,1076,151,1164), (157,788,232,864), (344,1104,434,1202), (484,774,556,871), (562,1032,647,1109): 72–90 × 76–98 px

- **Shape:** a **five-leaf star** radiating from one hub (`z_expl_leafB.png`: 5 leaves at about 72° apart, ±12°).
  - Each leaf is a **broad pointed leaf**: a narrow base, widest at 0.5 L, straight sides to a pointed tip.
    **W : L ≈ 0.45–0.5.** A midrib fold splits each leaf into a lit and a shaded half.
  - The leaves rise 20–35° from the hub's plane, and the tips droop slightly.
  - Seen from the side, it is a fan of 3–4 leaves (`z_expl_leafTR.png`).
- **Size:** clump span **1.5** (× 1.2; 85 px / 70 = 1.2 × 1.0; f34 clumps 89–93 px / 74 = 1.2–1.26). Leaf L about
  0.85, W about 0.40.
- **Construction:**
  - `_leaf_clump(span, seed)` makes 5 leaves with `K.leaf(shape=<kite>)`, the M018 recipe: an 8-point outline
    `[(0.25, 0.40), (0.55, 0.50), (0.82, 0.28)]`, camber 0.08 L, keel 0.04 L. 16 tris each.
  - A hidden 5-sided hub cone (10 tris) gives the leaf bases something to overlap.
  - Per leaf: ±8 % L, ±6 % W, ±10° yaw, ±5° roll by seed.
  - About **90 tris** per clump.
- **Broad, not spiky.** No cones or narrow blades (WorldModeling §6.1 and §18; lesson from recent models).

## 2. Layout (× 1.2 recommended size; starting values, tune on renders)

Coordinates are in studs, in the build frame (front −Y, +X right, ground z 0, origin = the plan centre). They come from
`fit.py` and `proxy3.py`.
- **Method:** each element's top-view position was moved along the front34 camera's screen-right axis
  (0.883, −0.469) until it matches the f34 drawing. Residuals were ≤ 0.6 stud before the move. So **both** the
  front34 render and the top render land on the sheet.
- **The tuning rule.** To move a piece without changing the hero, **slide it along the front34 depth axis**
  (±(0.469, 0.883) in XY, with dz = −(0.0975 dX + 0.1836 dY) / 0.978). Use it whenever a clump or lump must be slid
  into contact.

### 2.1 Logs and stubs (Main Branch Body)

| Piece | From → to (axis centres) | Ø (start → end) | Notes |
| --- | --- | --- | --- |
| Junction J | (−0.42, 0.06, 0.74) | knot Ø 1.45 | crotch filler; its underside sinks to z ≈ 0.05 (floor cut) |
| A_low | J → (−2.94, −0.90, 0.60) | 1.20 → 1.13 | lies on the ground; its end is hidden under the large lump (f34 and top); cap 1 |
| A_up | J → (2.46, 1.58, 3.96) | 1.15 → 1.00 | about 45° steep; cut face ⟂ the axis, so it shows to the front34, top and rear; cap 2; the tallest wood point |
| B_back | J → (−2.58, 2.14, 1.02) | 1.08 → 1.02 | lifts gently to its back end; **cut face oblique**, normal tilted 30° up from the axis, so it shows in the top and rear; pokes about 0.3 out of the large lump's left edge in front34 (the f .0, h .22 sliver); cap 3 |
| B_front | J → (2.21, −2.52, 0.54) | 1.10 → 1.06 | lies on the ground; the cut face points front-right (front34 f .94, h .12); cap 4 |
| C stub | (−0.72, 0.42, 0.90) → (−0.58, 1.86, 2.58) | 0.82 → 0.72 | rises steeply toward the back from J's back side; the TL clump sits on its end; cap 5 (mostly under the clump) |
| D stub | (0.74, −1.10, 0.72) on B → (2.40, 0.18, 3.30) | 0.72 → 0.65 | rises right-back, mostly behind the small lump; the TR clump sits on its end; cap 6 |

- A and B are straight from J to each end. A has a **bend at J** (A_low to A_up is about 135° in elevation).
  WorldModeling §6.3 allows 2–5 major direction changes.
- Each arm is built as its own tube from J. They are fused through the knot by the union, so one continuous bark skin
  runs from arm to arm.

### 2.2 Resin, join pads, clumps

| Piece | Centre | Size | Sheet evidence | Notes |
| --- | --- | --- | --- | --- |
| Large lump | (−2.34, −0.72, 1.94) | Ø 2.7 (r 1.35, squash 1.0/0.95/0.93) | f34 .193, .380; top .218, .360 | straddles A_low; its lower front sags to about z 0.65 in front of the log; sits on pad 1 |
| Pad 1 | on A_low's upper-front surface under the large lump's centre, normal = log axis → lump centre | Ø 1.35, 0.2 proud | underside close-up | rim visible below the lump's front-bottom |
| Small lump | (1.90, −0.86, 2.70) | Ø 1.8 | f34 .789, .583; top .738, .366 | on D's front flank (centre about 0.95 from D's axis); against A_up's right flank in front34 |
| Pad 2 | on D's front flank toward the small lump | Ø 0.9, 0.15 proud | exploded dashed patch on D | |
| Clump TL (back) | about (−0.38, 2.14, 3.06); hub at C's end | span 1.5, fanning up and back | f34 .297, .708; top .473, .845 | the biggest clump in the top view |
| Clump TR | about (2.76, 0.06, 3.84); hub at D's end | span 1.5, fanning up and right | f34 .857, .863; top .884, .511 (back part) | the top-right extreme of front34 |
| Clump R-low | about (2.22, −0.30, 1.56) | span 1.2 | f34 .787, .379; top .884, .511 (front part) | under the small lump; slide along the front34 depth axis until its hub touches D, the pad or the lump's underside |
| Clump F (front) | about (−0.34, −1.74, 0.50) | span 1.5, leaves splayed toward the camera | f34 .559, .104; top .478, .206 | on the ground in the front notch; hub against J/A_low |
| Clump L (left) | about (−2.58, 0.66, 1.20) | span 1.3 | top .110, .602 only | left notch between A_low and B_back; hidden behind the large lump in front34 |

**Expected hero:** about 7.0 × 5.9 × 4.45 (A_up's cut-end top about 4.45; TR clump top about 4.4).
- **Front34 checks:** W : H 1.28–1.38 (sheet 1.316).
- **Top checks:** W : D 1.10–1.20 (sheet 1.116).

## 3. View conflicts and resolutions

### 3.1 The "Front" cell is the front three-quarter drawing

- **Evidence.** Every part sits at the same fractions in both cells (§1.2), and the W : H is 1.26 against 1.32.
- **Resolution.** Compare the sheet's Front cell with the kit **front34 (−28, 12)** and an extra **`front_sheet (−28, 6)`**.
  The kit `front (0, 4)` has no sheet counterpart: use it only for self-consistency and record that. The hero
  (front34) governs (WorldModeling §1.1).

### 3.2 B's back end: low in the f34, mid-height in the rear

- **Evidence.**
  - The f34 shows only a sliver of bark at the far left, at h .22 (z ≈ 0.95), under the large lump.
  - The rear shows B's back end at h .51 (z ≈ 2.2 at that cell's scale), cut face to camera-right.
  - The top shows its cut face as a full ellipse.
- **Resolution.** Put the end centre at z 1.02 with an **oblique cut face** (normal 30° up). The face then reads in the
  top and rear, while the end stays low enough in front34 to tuck mostly behind the large lump. The rear profile
  tolerance at f .85–1.0 is ±0.15.

### 3.3 The rear three-quarter is a mirror image

- **Evidence.** Its cut ends (raised left, top, ground at the far right) and lumps line up with the kit
  `rear34 (152, 12)` **flipped left-right** (proxy flipped: small lump .79, A top .71, B front .93, large lump .31;
  sheet .705, .603, .944, .155). The unflipped render puts the lumps on the wrong sides.
- **Resolution.** Compare the r34 with the flipped kit rear34. Judge it by shares, cut-end count (3), lump count and
  sizes, and clump count (4), as in M018 §3.3.

### 3.4 The rear cell's lumps are swapped

- **Evidence.**
  - The logs fit a camera at +Y: A_up's end is upper left (+X), B's back end right (−X).
  - But the large lump is drawn at the lower left (+X) and the small one centre right. On the build they are at −X
    (front-left) and +X.
- **Resolution.** The logs govern. Compare the rear by the cut ends' positions (A top f .29, h .95; B back f .91,
  h .51; ±0.12), shares, lump count and clump count (3–4). Record the lump positions as a known miss.

### 3.5 The side cell is not reproducible

- **Evidence.** W : H 0.81. Any camera on a 7.0 × 5.9 X-shaped footprint gives about 1.0–1.3 (kit side 90: about 1.1
  for the real mesh). Its lumps are far apart left/right while its single log stands vertical, which no azimuth
  gives together.
- **Resolution.** Compare by shares (R 45 %: a lump-dominated view; ours will be about 30–35 %), lump count, one cut
  end on top, three clumps. Use the kit `side (90, 4)`: screen right = +Y = the back, as in M016/M017. Record the miss.

### 3.6 Top against front three-quarter

- **Evidence.** Residuals ≤ 0.6 stud along the front34 screen axis (`fit.py`), resolved by the compromise
  positions in §2. The top drawing's lump sizes (76 / 49 px) imply about 34 px/stud; the f34's imply 74.
- **Resolution.** The f34 governs the sizes.

### 3.7 Exploded against hero

- **Small lump size:** the exploded's small lump is 0.52 of the large one; the hero's is 0.66. The hero governs.
- **C, the upper-left stub:** in the exploded it looks like B's continuation, but the top view shows B's own back end
  at the far back-left. C is built as a separate stub from J toward the back, carrying the TL clump. That fits the f34
  (TL clump over the large lump), the top (back clump at .473, .845) and the exploded (C's leader to the TL clump).
- **D:** hidden in every hero view (behind the small lump and the TR clump), but drawn in the exploded. It is kept as
  the small lump's support (decision §8.3).
- **Cut ends:** 6 (all log and stub ends). The exploded draws 4 attached and 2 floating; the hero shows 2–3 at once.

### 3.8 Five leaf clumps; the hero shows four at once

- Every hero cell shows 3–4 clumps. The top shows 4 notches (with the right one doubled), and the exploded draws 5.
- **Resolution:** 5 clumps (§2.2). From front34, 4 must show (TL, TR, R-low, F) and L must stay hidden.

### 3.9 "Solid colors, no gradients" against the user's blended-colour rule

- The user's rule wins, and the sheet itself shows the gradients:
  - each lump is yellow-amber on top and red-orange at the bottom (paint, not only light: the bottom third's *lit*
    quartile is still redder, §5.3);
  - the leaves are darker at the base and lime at the tips;
  - the bark is lighter near the cut ends ("Wood (Inner)").
- Keep Tint low so it still reads "clean".

### 3.10 Effects: "optional" overlay against the user's rule

- The user's rule ("effects shipped where the sheet shows them") wins. Ship the sparkles as VFX sockets (§7).
- The sheet's own words, "No glow baked into model", rule out emission and Neon.

## 4. Construction plan (Build agent, stages 1–3)

1. **Parts first,** each from its own function and checked against its cell:
   - `body()`: `ResinBranchBody`, the 4 arms + C + D + knot + 2 pads, without the caps. Compare with the exploded
     body: an X with A thickest, C up-left, D up-right.
   - `cut_end()`: `ResinBranchCutEnd`, Ø 1.05, 10 sides, 2 ring bands, 110 tris.
   - `lump_large()` and `lump_small()`: `ResinBranchLumpLarge` Ø 2.7 and `ResinBranchLumpSmall` Ø 1.8.
   - `leaf_clump()`: `ResinBranchLeafClump`, span 1.5, 5 leaves.
   - Render a parts shot (`extra`, about (−25, 15)) laid out like the exploded. Compare:
     - the lump outline corner count (8–10);
     - the lump W : H (1.0);
     - the cut-end side count (10) and thickness (0.2 Ø);
     - the leaf W : L (0.45–0.5);
     - the clump's 5-star.
2. **Hero:**
   1. `_paste` (m011 pattern) the body, 6 caps (each oriented to its arm's end, sunk 0.12 Ø), 2 lumps (on their pads)
      and 5 clumps (each with its own seed and yaw) at §2.
   2. One exact self-union, then `union_loose`, then `m004.floor_cut` at z 0.
   3. Origin at the bbox bottom centre; transforms applied. One closed shell (decision §8.6).
3. **Budget** (§4.3): hero about 1900–2200 (limit 4000), each part under 520 (limit 1000). Don't refine the logs: the
   sheet shows 3 faces across a log and 3–5 long facets along it.
4. **Placeholder keys** (stage 1): `m019_bark`, `m019_cut`, `m019_resin`, `m019_leaf`. Stage 4 adds the rest (§5.4).
5. **Stage 1 acceptance** (render, compare every view, measure):
   1. **Overall read:** one fused forked branch: the arms flow through the knot, and no seam line or gap shows at the
      junction (close-up check: an extra `junction_cu (−10, 20)` framed on J).
   2. **Front34 against the f34 cell** (and the front cell, via `front_sheet (−28, 6)`):
      - shares within ±4 (C ±2) of 15.6 / 30.2 / 5.6 / 48.7;
      - top profile within ±0.07;
      - component centres within ±0.06 (§1.2 table);
      - large lump 0.36–0.42 W, small lump 0.23–0.29 W;
      - exactly 2 cut ends visible (A top, B front) plus at most a sliver of B's back end at the far left.
   3. **Top:** the X; 3 cut ends visible (B back, A top, B front) at §1.2 ±0.07; the lumps and 4 clumps at §1.2
      ±0.07; W : D 1.10–1.20.
   4. **rear34 flipped against the r34:** shares ±5, 3 cut ends, 2 lumps, 4 clumps.
   5. **Rear:** A top f .29 h .95 and B back f .91 h .51, ±0.12; 2–3 clumps; lumps present (sides recorded as a miss).
   6. **Side (90):** shares and counts only (§3.5).
   7. **Parts against their cells** (§4.1).
   8. **Hero size** 7.0 × 5.9 × 4.45 (±0.35 / ±0.35 / ±0.2).
6. **Stage 2:**
   - zero non-manifold, boundary, wire and loose elements; no zero-area faces or n-gons; no faces under 5° where
     6 caps, 2 pads and 5 hubs meet bark (m011 `_tidy` / `_desliver`);
   - don't decimate the cut-end ring loops (they carry §5.5's rings) or the lump hulls below about 20 broad faces.
7. **Stage 3:** smart UV, margin ≥ 0.008, no overlaps, even texel density.

### 4.3 Budget table (× 1.2 sizes)

| Piece | Count | Tris each | Total |
| --- | --- | --- | --- |
| A (bent; 8 sides, 6 rings) | 1 | 110 | 110 |
| B (8 sides, 6 rings) | 1 | 100 | 100 |
| C, D stubs (7 / 6 sides, 3 rings) | 2 | 40–45 | 85 |
| Junction knot (hull) | 1 | 30 | 30 |
| Join pads (6-sided) | 2 | 24 | 48 |
| Cut-end caps (10 sides, 2 ring bands) | 6 | 110 | 660 |
| Large lump (hull 26 + pokes) | 1 | 80 | 80 |
| Small lump (hull 20 + pokes) | 1 | 55 | 55 |
| Leaf clumps (5 × 16 + hub 10) | 5 | 90 | 450 |
| **Sum before union** | | | **about 1620** |
| **Hero after union** | | | **about 1900–2200** (limit 4000) |
| Parts: Body / CutEnd / LumpLarge / LumpSmall / LeafClump | | | about 470 / 110 / 80 / 55 / 90 (limit 1000) |

## 5. Colour plan (Finish agent, stage 4)

### 5.1 Swatches (flat; medians of a 36 × 23 box inside each, x 44–80)

| Swatch | Box | Hex | HSV |
| --- | --- | --- | --- |
| Wood (Bark) | (44,1329,80,1352) | `#85573B` | 23°, 0.56, 0.52 |
| Wood (Inner) | (44,1364,80,1388) | `#AD734C` | 24°, 0.56, 0.68 |
| Resin | (44,1399,80,1422) | `#FE9D08` | 36°, 0.97, 1.00 |
| Cut End Wood | (44,1434,80,1457) | `#E9BD85` | 34°, 0.43, 0.91 |
| Leaves | (44,1469,80,1492) | `#528B2A` | 95°, 0.70, 0.55 |

- **Bark:** the swatch **equals** the unshadowed rendered bark: the exploded body median is `#85573A`.
- **Wood (Inner):** equals the rendered **lit** bark quartile (`#A56C48`–`#AB6E49`). It is the lighter bark that shows
  near the cut ends and on broad lit planes, not a separate material (§5.3).
- **Resin:** about the rendered mid third of the lumps (`#FD9F0C`).
- **Cut End Wood:** equals the close-up disc median (`#E9BD85`). The hero discs render lighter (`#F2C78F`–`#FCD7A3`).
- **Leaves:** darker and less saturated than any rendered leaf (`#5A9B16`–`#61A218`): use the render.

### 5.2 Rendered regions (`samp.py`, `samp2.py`, `samp3.py`; median / lit quartile / shade quartile)

| Region | Box | Mask | Median | Lit | Shade |
| --- | --- | --- | --- | --- | --- |
| Bark, f34 / front / top | V | B | `#7B5036` / `#7D5338` / `#794E34` | `#9F6946` / `#A36C48` / `#9A6847` | `#4D3321` / `#4D3321` / `#5D3B26` |
| Bark, r34 / rear / side | V | B | `#815539` / `#7F5236` / `#815438` | `#A56C49` / `#B2754E` / `#9D6846` | `#593923` / `#4A301E` / `#553725` |
| Bark, exploded body (unshadowed) | (182,820,528,1119) | B | `#85573A` | `#A56C48` | `#66422C` |
| Bark, junction / cut-end close-ups | cu boxes | B | `#8C5B3F` / `#8B593B` | `#AD714A` / `#A96E4A` | `#784E34` / `#66422C` |
| Bark near cut ends (≤ 25 px) / far (> 60 px), f34 | | B | `#875638` / `#774E35` | `#B3764E` / `#9B6645` | `#623D24` / `#493120` |
| Bark by height, f34 h 0–.2 / .2–.4 / .4–.6 / .6–.8 / .8–1 | bands | B | `#603F2B` / `#7F543A` / `#7E5338` / `#825438` / `#865638` | | |
| Bark ring round the small lump, f34 | | B | `#5C391E` | `#75462C` | `#2C1B10` |
| Resin, all lumps (f34 / front / top / side / rear / r34) | V | R | `#FC9205` / `#FC9204` / `#FC9104` / `#FC9504` / `#F28203` / `#FA8A02` | `#FEB525` … | `#DE6E02` … |
| Large lump thirds, f34 (top / mid / bottom) | (53,229,219,391) | R | `#FDA80F` / `#FD9F0C` / `#E57802` | `#FEC84C` / `#FEB625` / `#F08A0A` | `#FD8E02` / `#EA7A02` / `#DA6801` |
| Large lump thirds, exploded | (88,899,228,1047) | R | `#FEAC15` / `#FD9204` / `#E27802` | `#FEC23A` / `#FEB526` / `#F78D03` | |
| Small lump thirds, f34 | (331,182,441,294) | R | `#FD9E06` / `#FD9103` / `#DC7102` | `#FEB522` / `#FEAF1C` / `#FD9806` | `#F37902` / `#EA7001` / `#AC4D01` |
| Resin highlight facets (6 % of each lump, f34) | lump boxes | R (hi) | `#FED467` (43°, 0.59) | `#FEDE85` | `#FED05B` |
| Cut end, B front f34 / front cell / A top f34 / A top (top view) | (421,360,477,426) / (235,654,267,691) / (314,110,377,164) / (946,536,982,571) | C | `#F2C78F` / `#F6CC93` / `#FCD7A3` / `#FDDFB0` | `#F9D39F` / `#FCDCAD` / `#FEE4B9` / `#FDE5B9` | `#EDBD81` / `#F1BF81` / `#EEBC7D` / `#F7D29C` |
| Cut end, B back end (top, rear) / r34 raised | (809,528,837,555) / (712,581,753,621) / (645,168,687,200) | C | `#F7CD95` / `#ECBE84` / `#F6CB92` | | |
| Cut end, exploded discs (floating L / R, B end, A top) | | C | `#E3B77D` / `#E8BA80` / `#EFC388` / `#F8CF98` | | `#CC9A5F` … |
| Cut-end close-up disc | (817,1168,909,1271) | C | `#E9BD85` | `#EDC38C` | `#E5B275` |
| Join pad (underside close-up) | (827,1013,894,1096) | C | `#E4AA65` (33°, 0.56) | `#F0B673` | `#E0A15A` |
| Leaves, f34 / front / top / rear / r34 / side | V | L | `#5A9B16` / `#599D17` / `#5B9A14` / `#509315` / `#559816` / `#569716` | `#89C728` / `#8AC72A` / `#90CA28` / `#85C326` / `#88C629` / `#89C729` | `#2D610C` / `#2F630C` / `#2D5F0A` / `#2D600C` / `#2A5E0C` / `#2D5F0D` |
| Leaf clumps, exploded (TL / TR / R / L / B) | §1.4 boxes | L | `#61A218` / `#5C9F16` / `#5A9F15` / `#5A9F18` / `#5CA017` | `#93CD2E` / `#8CCA25` / `#8CCA27` / `#86C424` / `#8BC827` | |
| Ground shadow, f34 | (60,425,470,445) | O | `#D7CEC4` | `#DED6CD` | `#CAC0B5` |

Deciles (dark → light), f34:

```
bark   #3C2719 #513624 #62402B #6F482F #774D34 #7E5338 #84563B #8C5A3C #9A6544 #AF734D
resin  #CA6101 #E27002 #EA7B02 #F38302 #FC8D02 #FD9504 #FEA005 #FEA90F #FEB31F #FEBF3A
leaves #1E460A #32680D #3F7D10 #478914 #529614 #5EA215 #6CAE18 #75B81E #86C425 #9BD432
```

### 5.3 How the colour works

**Bark.**
- One warm brown family: hue 22–24°, sat 0.55–0.57, everywhere. The lit/shade spread
  (`#3C2719` → `#AF734D`) is mostly the sun on the faceted tube; never paint by facing.
- **Painted signals:**
  1. Lighter near the cut ends: `#875638` within 25 px against `#774E35` far away, +16 levels; the lit quartile
     `#B3764E` ≈ the Wood (Inner) swatch.
  2. Darker at the ground contact: `#603F2B` in the bottom band, partly AO (Roblox has none, so paint some).
  3. A dark seep ring round the lumps' feet: `#5C391E` round the small lump, which is mostly shadow.
- The junction close-up's bark is a touch lighter and more even (`#8C5B3F`): the crotch is not darkened.

**Resin.**
- A pure saturated orange (hue 31–39°, sat 0.94–0.99), with the red channel at clip (#F…/#FE…).
- **Top → bottom painted gradient** (every lump, every view):
  - top third `#FDA80F`–`#FEAC15` (39°, more yellow);
  - mid `#FD9F0C`–`#FD9204` (35°);
  - bottom `#E27802`–`#E57802` (31°, deeper red-orange).
- The bottom third's **lit** quartile is still red-orange (`#F08A0A` against the top's `#FEC84C`), so this is paint,
  not only shade.
- **Highlights:** about 6 % of each lump is pale-yellow facets (`#FED467`–`#FEDE85`) at the upper-left (the key
  light's side). That is gloss on a satin surface; don't paint it (§5.6).

**Cut ends.**
- A pale warm cream-tan (33–37°, sat 0.30–0.47). Up-facing ends render paler (`#FCD7A3`–`#FDDFB0`) than side-facing
  ends (`#F2C78F`–`#F6CC93`): that is light, so paint one colour.
- **Rings** (close-up radial bands): centre `#ECC38E`, ring at 0.2–0.35 R `#E9B87C`, 0.35–0.55 R `#EABE88`,
  ring at 0.55–0.75 R `#E8B97F`, outer `#E8BE86`. So there are two faint darker rings (about 6–10 levels, +0.05 sat).
  WorldModeling §11 asks for "1–2 broad rings or color bands".
- The disc's outer side band is shaded (`#DCA366` shade quartile at 46–56 px): light, not paint.

**Join pads.** Cut wood stained with resin: more saturated and warmer than the ends (`#E4AA65`, sat 0.56).

**Leaves.**
- A very saturated yellow-green (hue 85–95°, sat 0.84–0.88), much more vivid than WorldModeling's `LeafMid`.
- **Base → tip:** the base `#509112`–`#539613`, the tips `#6EAE1D`–`#78BA1E`, tip lit `#9CD534`. Most visible on the
  sunlit clumps (f34 TR base `#509112` → tips `#74B31B`; exploded TR `#539613` → `#78BA1E`).
- **Clumps in shade:** the R-low clump under the small lump is `#33650F`, the f34 front clump `#539617`. That is
  shadow from the lump, not paint: keep R-low on the normal keys and let the lump shade it.

### 5.4 Keys (start from these; `K.calibrate`; write the calibrated hexes into `palette()`)

The calibration targets are rendered medians of **unshadowed** regions, not swatches.
- **`K.sample` kinds:**
  - `"brown"` for the bark (`#85573A`: r − g 46, sat 0.56, passes);
  - `"vivid"` for the resin;
  - `"green"` for the leaves;
  - `"all"` on tight boxes for the cut ends and the pad (cream fails `"brown"`'s sat filter).

| Key | Calibration target | Where | Finish |
| --- | --- | --- | --- |
| `m019_bark` | `#85573A` (exploded body median; swatch `#85573B`) | the whole body | rough 0.9 |
| `m019_bark_light` | `#9E6743` (between the near-cut-end lit `#B3764E` and its median `#875638`; swatch Wood (Inner) `#AD734C`) | within 0.45 of each cut end, broad patches | rough 0.9 |
| `m019_bark_dark` | `#5F3E2A` (ground band `#603F2B`; lump-seep ring `#5C391E`) | ground contact, pad and lump feet | rough 0.95 |
| `m019_cut` | `#F1C68C` (side-facing hero ends `#F2C78F`–`#F6CC93`; exploded B end `#EFC388`; swatch `#E9BD85`) | cap faces and sides | rough 0.85 |
| `m019_cut_ring` | `#E2B074` (the darker close-up ring `#E8B97F`/`#E9B87C`, pushed about 8 levels so it survives the render) | the two ring bands | rough 0.85 |
| `m019_join` | `#E2A862` (pad `#E4AA65`) | the 2 join pads | rough 0.8 |
| `m019_resin` | `#FC9407` (lump medians `#FC9205`–`#FC9504`; mid third `#FD9F0C`) | lump middles | rough 0.35, spec about 0.35, no emission |
| `m019_resin_light` | `#FDAA14` (top thirds `#FDA80F`–`#FEAC15`) | top 30 % of each lump | as resin |
| `m019_resin_dark` | `#E27602` (bottom thirds `#E27802`–`#E57802`) | bottom 30 %, the contact with the pad | as resin |
| `m019_leaf` | `#5C9E16` (view medians `#559816`–`#5B9A14`; exploded clumps `#5A9F15`–`#61A218`) | leaf middles | rough 0.8, `low_spec` |
| `m019_leaf_tip` | `#72B41C` (tips `#6EAE1D`–`#78BA1E`) | outer 30 % of each leaf | rough 0.8, `low_spec` |
| `m019_leaf_base` | `#4F9113` (bases `#509112`–`#539613`) | inner 30 %, keel faces, hub | rough 0.8, `low_spec` |

**Calibration warnings:**
- **Resin is at the clip.** The sheet's red channel is `#FC`–`#FE`; linear calibration cannot push past 1.0. Expect
  the keys to sit at full saturation.
  - If the top third washes to `#FFD0..`, lower the specular rather than the colour.
  - M012's calibrated amber keys are a good start: A_LIGHT `#FDAE30`, A_MID `#F66816`, A_DARK `#924A0E` (which renders
    `#CD5214`). This resin is about 4° yellower than M012's, so start `m019_resin_dark` near `#C8620A` and
    `m019_resin` near `#F7820E` if the first calibration comes out red.
- **Calibrate the lumps on the parts shot** (unshadowed), then re-measure the hero thirds. The hero's bottom third
  also gets shade from the logs.
- **Leaves:** greens calibrate darker than the painted sheet (kit memory); trust the render match. `m019_leaf_tip`
  must stay ≤ 88° (lime) and sat ≥ 0.8. These leaves are far more saturated than M018's; don't reuse M018's keys.
- **Cut ends:** calibrate `m019_cut` on the B front end box `(421,360,477,426)` (side-facing). Then check that A_up's
  end (facing up) comes out paler by itself (`#FCD7A3`) without a separate key.
- **Bark:** calibrate on the parts shot of the body (unshadowed) against `#85573A`, then check the f34 median
  `#7B5036` ±10.

### 5.5 Blending (`K.blend(mode="blend", steps=3)` over explicit face lists; fields are positions, never facing)

- **Bark** (field = distance along each arm's axis from its cut end, plus world z):
  - `bark` base.
  - Within 0.45 of a cut end, blend to 50 % `bark_light`, 3 steps, so the light lip leads into the cream disc.
  - Broad noise patches (`K.patches` scale 0.6, level 0.3) between `bark` and a 35 % `bark_light` mix (the swatch's
    lighter planes). Never single faces.
  - z < 0.3: 40 % `bark_dark` (ground contact).
  - Within 0.3 of each pad: 30 % `bark_dark` (the seep ring).
  - The knot's crotch stays plain `bark` (the junction close-up isn't darker).
- **Resin** (field = height within each lump, 0 at its bottom, 1 at its top, ±0.06 broad noise):
  - < 0.30 → `resin_dark`; 0.30–0.70 → `resin`; > 0.70 → `resin_light`; 3 steps.
  - **Hard** edge only to the pad and bark (material change).
- **Cut ends** (field = radius on the face / R):
  - 0–0.22 → `cut`; 0.22–0.38 → `cut_ring`; 0.38–0.62 → `cut`; 0.62–0.78 → `cut_ring`; 0.78–1.0 → `cut`.
  - Use `mode="blend", steps=2` on the ring edges, so they read as soft bands, not stripes.
  - The side band is `cut` with 20 % `cut_ring`.
  - **Hard** edge to the bark lip.
- **Join pads:** `join`, with a hard edge to bark and resin.
- **Leaves** (field = each leaf's own along-length t from its construction frame):
  - t < 0.3 → `leaf_base`; 0.3–0.7 → `leaf`; t > 0.7 → `leaf_tip`; 3 steps, ±0.08 noise on t.
  - Keel faces → +0.25 toward `leaf_base`. The hub is `leaf_base`.
  - Clump-to-clump: TL and TR (sunlit, high) shift 0.1 toward the tip; F and L as is; R-low as is (the lump shades
    it).
- **Hard edges only** where materials meet: bark | cut, bark | pad, pad | resin, bark | leaf hub.

### 5.6 Texture (Tint) and finish

- **Tint** (`tint_var` per piece about 0.04, so each lump, cap and clump differs slightly):
  - bark: `K.texture` amp 0.05, scale 0.4 (visible broad mottling per facet group);
  - resin: amp 0.025 (clean);
  - cut ends and pads: amp 0.03;
  - leaves: amp 0.035, scale 0.5.
  - Never per-triangle confetti.
- **Finish:**

| Material | Roughness | Specular | Metal | Notes |
| --- | --- | --- | --- | --- |
| Bark keys | 0.9 | normal | 0 | matte |
| Cut / ring / join | 0.85 / 0.85 / 0.8 | normal | 0 | matte sawn wood |
| Resin keys | 0.35 | about 0.35 (tune: the hero's pale-facet share should be 4–8 % of lump pixels, hue > 40.5°, sat 0.42–0.66) | 0 | satin-gloss resin; **opaque, no emission** ("No glow baked into model") |
| Leaf keys | 0.8 | `FOLIAGE_SPEC` (`low_spec=True`) | 0 | matte |

### 5.7 Re-measure (final renders against the sheet, same boxes and masks)

- **Bark:**
  - front34 median within 10 levels of `#7B5036`;
  - parts-shot body within 8 of `#85573A`;
  - near-cut-end bark lighter than far bark by 10–20 levels;
  - bottom band darkest.
- **Resin:**
  - front34 lump median within 10 of `#FC9205`;
  - thirds in order (top yellowest, hue ≥ 37°; bottom reddest, hue ≤ 32°), each within 12;
  - pale-facet share 4–8 %.
- **Cut ends:** B front end within 10 of `#F2C78F`; A_up end paler (≥ `#F8D19A`); both rings visible in a close-up
  extra.
- **Leaves:** front34 median within 12 of `#5A9B16`, sat ≥ 0.75; tips lighter than bases.
- **Shares** per §4, step 5.2.

## 6. Joins and contact (no cracks or seams on this sheet)

- **Arms into the knot:** each arm starts 0.3 inside the knot; one exact union. No visible seam ring at J (close-up).
- **Caps into the ends:** the disc's back half is sunk into the end (0.12 Ø), the face proud 0.08 Ø past a 4 % flared
  bark lip. No coplanar faces: the disc's back face sits inside the tube.
- **Lumps on pads:** each pad sinks 0.1 into the bark, and each lump sinks 0.15 Ø into its pad and touches the bark
  round it. Visibly attached, no floating (WorldModeling §6.7).
- **Clumps:** each hub is sunk 0.1–0.15 into bark, a pad or a lump. No clump floats (slide rule, §2).
- **Ground:** A_low, B_front and the knot underside are floor-cut at z 0 (`m004.floor_cut`). B_back's end is in the
  air (z 0.5 underside): it rests on J. Check from the side that it reads as supported.
- Overlap everything; no coplanar contact (exact booleans, pitfall 12).

## 7. Lighting and VFX plan (Finish agent, stages 5 and 6)

**What the sheet shows.** The VFX overlay cell (700,1315,1008,1500) shows **7 pale four-point sparkle stars** round
the lumps, "separate from geometry":
- **4 round the large lump:** left of it at 0.35–0.9 stud outside its surface, and above-left;
- **3 round the small lump:** above-left, upper right and right.
- **Sparkle colours:** cores `#F9E4C4`–`#F8EACF`, edges `#FBD28E`–`#FBD99A`.
- **Sizes:** 13–34 px against the 78 px large lump, i.e. **0.45–1.2 studs** at the × 1.2 size.
- The text says "No glow baked into model". No light falls on the bark in the overlay, and there's no halo
  (a faint pale wisp beside the large lump is too vague to ship).

### 7.1 Stage 5 (lighting): no emission, no light

- **No emissive faces.** The exporter would turn emission ≥ 1.0 into flat Neon parts, erasing the lumps' facets, and
  the sheet forbids baked glow.
- **No PointLight.** Not shown; WorldModeling §1.2 forbids "an ordinary asset recolored neon with a glow halo".
- Record "Stage 5: nothing to add; the resin's look is colour and gloss only."
- **Studio note (Requires Manual Validation):**
  - check that the resin doesn't clip to flat orange under the game's sun (its red channel is at the limit);
  - check that the top → bottom gradient survives the palette export.

### 7.2 Stage 6 (VFX), kinds in `art/blender/lib/vfx.py`

- **Kinds that exist:** `torch_fire`, `campfire`, `brazier_fire`, `forge_fire`, `chimney_smoke`, `embers`,
  `heat_glow`, `glyph_glow`, `rune_glow`, `waterfall_mist`, `water_foam`, `waterfall_curtain`, `water_flow`, `vapour`,
  `harvest_hit`, `harvest_deplete`, `ore_glint`, `crystal_glow`, `crystal_halo`, `dust`. No new kind is needed.
- **Ship two `ore_glint` sockets** ("sparse twinkles … set color to the ore"; texture `spark_diamond`, a 4-point
  diamond spark, which is exactly the sheet's star). Use `fx=[(kind, loc, overrides)]` in `M.mk`, with the emitter
  overridden like m012's `_glint_fx`:

| Socket | Location (build frame) | Emitter overrides | Why |
| --- | --- | --- | --- |
| `ore_glint` large | the large lump's centre (−2.34, −0.72, 1.94) | `color ["#F9E4C4", "#FBD28E"]`, `size [0, 0.9, 0]`, `rate 2.5`, `lifetime [0.6, 0.9]`, `shape` = the lump's bbox + 0.8 each side ≈ [4.3, 4.0, 4.3] (Roblox X, Y up, Z), `light None` | the 4 stars round the large lump; about 2 visible at once (the sheet's 4 is a still frame of an "optional" overlay; 4 at once would be busy in game) |
| `ore_glint` small | the small lump's centre (1.90, −0.86, 2.70) | same colours, `size [0, 0.65, 0]`, `rate 1.5`, `shape` ≈ [3.2, 3.0, 3.2] | the 3 stars round the small lump |

- Check that the export STATS line reports **2 sockets**, and render with `vfx=True` (kit memory "Kit VFX always").
- **Not recommended:**
  - `crystal_glow`, `crystal_halo` or a PointLight ("No glow baked into model"; nothing lit on the sheet);
  - `dust` (R06 shipped orange motes; the sheet has none);
  - harvest sockets (M009 and M011–M018 decided against them; decision §8.8).

## 8. Naming and decisions for the main session

**Names owned elsewhere.** Found by `git grep` of the repo, plus the zstd-decompressed `FlintbornWorldKit.blend`
searched with `blendnames.py` (`ResinNode` occurs 56 times there, `LeafClump` 33, `ResinLump` 3), plus the sheet
.blends:
- **R06 kit:** `ResinNode`, `ResinNodeWoodyBase`, `ResinNodeResinLump`, `ResinNodeLeafClump`, `ResinNodeBareBranch`,
  `ResinNodeRawResin`, `ResinNodeRawResinSmall`; keys `r06_resin`, `r06_softbark`, `r06_cutwood`, `r06_dirt`,
  `r06_leaf`. Also `SoftwoodLogCutEnd`, `SoftwoodLogBranchStub`.
- **W05:** `LogCutEndCap`, `LogBranchStub`, `OakLeafClump`, `AncientTreeResinBearing` (key `w05_resin`).
- **W06:** `LeafClumpLarge`, `LeafClumpMedium`, `LeafClumpSmall`. **R05:** `BerryShrubLeafClump`.
  **M012:** `Amber*`; R03 `AmberNodule`.
- **`src`:** no resin node id.
- `M.mk` would silently rename a clash to `<name>M019`, so avoid all of these.

**Proposed names.** None of them occur in the repo, the decompressed kit .blend or the sheet .blends; `m019_` is unused.

| Object | Part | Why |
| --- | --- | --- |
| `ResinBranchNode` | hero | R06 owns `ResinNode`; the subject is a resin-bearing branch |
| `ResinBranchBody` | Main Branch Body (with the join pads, no caps) | |
| `ResinBranchLumpLarge` | Resin Lump (Large) | R06 owns `ResinNodeResinLump` |
| `ResinBranchLumpSmall` | Resin Lump (Small) | |
| `ResinBranchLeafClump` | Leaf Clump | W05, W06 and R05 own other `*LeafClump` names |
| `ResinBranchCutEnd` | Branch Cut End | W05 owns `LogCutEndCap`; R06 owns `SoftwoodLogCutEnd` |

- Palette keys `m019_*` (§5.4). Collection `Kit/M019 Resin Node`.

**Decisions needed (a recommendation each):**
1. **Size** (§1.1): **× 1.2 → 7.0 × 5.9 × 4.45**, logs Ø 1.05–1.2, lumps 2.7 / 1.8 (recommended: the lumps read at
   distance, between M017 and M012), or the sheet's own × 1.0 → 5.85 × 4.9 × 3.7 (0.67 C).
2. **Body topology** (§3.7): **A bent at J + straight B + C stub to the back + D stub to the right** (recommended;
   it fits the f34, the top and the exploded at once), or C as B's raised back end (fits only the exploded).
3. **D stub** (§3.7): **include** it as the small lump's support (recommended: the exploded draws it, and it gives the
   lump and the TR clump something to sit on), or omit it and put the small lump on A_up's right flank.
4. **Cut-end rings:** **2 ring bands, 110 tris per cap** (recommended: the close-up shows two), or 1 band, 70 tris.
5. **Join pads:** **include** both (recommended: the "Flat Join Surface" close-up and the exploded outlines), or sink
   the lumps straight into the bark.
6. **Hero packaging:** **one closed shell** (recommended: STAGES default and the repo's one-mesh-per-asset contract;
   the lumps stay addressable as exported parts), or lumps as separate objects.
7. **Exports:** the hero plus 5 parts (`ResinBranchBody`, `ResinBranchLumpLarge`, `ResinBranchLumpSmall`,
   `ResinBranchLeafClump`, `ResinBranchCutEnd`) (recommended). A depleted state (the hero minus lumps, pads showing)
   is not on the sheet and is not built unless asked.
8. **Stage 5/6:** **no emission or light; two `ore_glint` sparkle sockets** with the sheet's colours (recommended),
   or also the R06-style `harvest_hit` / `harvest_deplete` pair (not recommended, for consistency with M009–M018).
9. **Comparison cameras:**
   - the sheet's front and f34 cells against the kit front34 plus an extra `front_sheet (−28, 6)`;
   - the r34 against the kit rear34 **flipped**;
   - the rear by logs only;
   - the side by shares and counts only (recommended, §3).
10. **Names** as proposed.

## 9. Pitfalls to avoid

1. **Separate lumps.** Logs that just pass through each other, lumps floating in front of bark, clumps hovering in
   notches. It must read as one fused fork: knot at J, pads under the lumps, hubs sunk into bark.
2. **Jewel or ball resin.** A bare icosahedron or dodecahedron is a gem; an ico-2 is a smooth ball. Use the
   jittered-hull lump with broad faces and pokes (§1.4): an 8–10-corner outline. The lump outline is the focal
   silhouette: check it first in every view.
3. **Clean prism logs.** The sheet's bark is broken into irregular long triangles with a slight taper. A perfect
   8-sided cylinder reads as a pipe. Ring jitter, twist and vertex jitter, but no subdivision or smoothing.
4. **Flat painted cut ends.** The ends are thick 10-sided inserts proud of a bark lip, with real ring edges.
   WorldModeling §11 asks for "1–2 broad rings"; don't paint rings on a single face.
5. **Spiky leaves.** Each leaf is a broad kite (W : L 0.45–0.5) with a midrib and a keel; five per clump. No cones and
   no narrow blades.
6. **Comparing the sheet's "Front" with the kit front (0, 4).** That cell is the f34 drawing (§3.1). The r34 is a
   mirror (§3.3); the rear's lumps are swapped (§3.4); the side is unreproducible (§3.5).
7. **B's back end sticking out in the hero.** At most a sliver left of the large lump in front34 (f ≈ 0, h ≈ 0.2).
   If it shows more, shorten B_back or slide the large lump along the front34 depth axis, not sideways.
8. **Resin colour by facing.** The pale facets are gloss. The painted gradient is top → bottom by position only.
   `K.check` facing correlation < 0.5.
9. **Brown-on-brown join pads.** The pads are cut wood (`#E4AA65`), not bark. They must show as a cream-orange rim
   under each lump, from below and in the junction close-up.
10. **Emission on the resin.** "No glow baked into model." The sparkle is VFX only.
11. **Dull leaves.** These leaves are vivid (sat 0.85). Calibrating them toward WorldModeling `LeafMid` or M018's keys
    makes them olive.
12. **Exact booleans.** Overlap everything:
    - arms 0.3 into the knot;
    - caps 0.12 Ø into the ends;
    - pads 0.1 into the bark, lumps 0.15 Ø into the pads;
    - hubs 0.1 into their support;
    - floor cut at z 0.

    Remove slivers with m011's `_tidy` / `_desliver`.
13. **Stage 2 over-cleaning.** Don't decimate the cut-end ring loops, the lump hulls (≥ 20 broad faces) or the leaves'
    8-point outlines.
14. **Naming clashes** with R06 `ResinNode*`, W05 `LogCutEndCap`, the `*LeafClump` names (§8). Only one agent drives
    Blender at a time; no commits, pushes or exports in stage agents.

## Decisions (main session, 2026-10-28)

All recommendations are accepted:
1. Size: × 1.2 (about 7.0 × 5.9 × 4.45 studs).
2. Body: A bent at the junction, plus straight B, plus stubs C and D.
3. Keep stub D.
4. Two ring bands per cut end.
5. Include both join pads.
6. One closed shell for the hero.
7. Export the hero plus 5 parts; no depleted variant.
8. No glow and no light; two `ore_glint` sparkle sockets in the sheet's colours; no harvest sockets.
9. Comparison cameras as listed in the study.
10. Names as proposed: `ResinBranchNode`, `ResinBranchBody`, `ResinBranchLumpLarge`, `ResinBranchLumpSmall`, `ResinBranchLeafClump`, `ResinBranchCutEnd`.

## Stage 1: Modelling (modeller, 2026-10-28)

Builder `art/blender/kit/mcp/m019.py` → `build()`; work file `art/blender/assets/kit/wip/M019.blend` (background
session, port 9877). Every part has its own function; the hero is built from the same builders in the build frame.

- **Logs** (`_tube`): 8-sided rings along a polyline path (parallel-transported frames), ring turn ±10°, ring scale
  ±7 %, vertex jitter ±6 % radial and ±10 % of a segment along the axis, inner rings wobble 0.05 off the axis. The cut
  end: last ring flared ×1.06 (bark lip), a flat end face (inner fan in cut wood at 0.82 of the lip, bark annulus
  outside). Buried end: a fan pushed back inside the knot.
- **Layout changes from §2** (tuned on renders against the f34 and top cells):
  - log Ø raised: A_low 1.55 → 1.42, A_up 1.46 → 1.24, B_back 1.34 → 1.26, B_front 1.40 → 1.30, C 0.96 → 0.84,
    D 0.86 → 0.76. The sheet's logs are about 0.2 W thick in the f34; §2's Ø 1.1 read as sticks.
  - Every layout x is scaled by `LAYOUT_SX` 0.91. This narrows W : H and W : D without squashing round parts.
  - **A_up has an elbow** (`A_UP`): straight from J for 70 %, then a 35° turn toward a cut normal that mixes the
    axis, up and the front34 camera direction; the cut is 35° oblique to the last run. A perpendicular cut faced away
    from the front34 camera (the sheet shows the top disc facing it), and a 50° oblique slice read as a blade.
  - `END_TURN`: A_low's end is turned 45° away from the front34 camera (the sheet hides it under the large lump);
    B_front's end is turned 38° toward it (the sheet shows it nearly face-on). B_back's cut tilts 30° up (§3.2).
  - D ends lower (z 3.25), behind the small lump; the TR clump sits beside its end. In the f34 the sheet hides D.
- **Knot** (`_knot`): the convex hull of a 7-point ring 0.38 out along each arm from J, plus two ground points,
  merged at 4°. The crotch fills with broad facets, with no cylinder-through-cylinder seam (junction close-up).
- **Join pads** (`_pad`): 6-sided prisms on A_low and D at the nearest axis point to their lump, leaning 45 % / 50 %
  toward front-down (`PAD_LEAN`), 0.2 / 0.18 proud. The large pad's rim shows under the lump's front-bottom and from
  below (`underside_pad.png`).
- **Cut-end inserts** (`_cap`): the log's cross-section (R = 0.86 × the end radius) projected along the axis onto the
  end plane, so an oblique end gets a matching ellipse. The face stands 0.08 D proud with a 0.03 D dome, in loops at
  0.22, 0.38, 0.62, 0.78 and 1.0 R (two real ring bands), and a 0.025 D bevel to the rim; the side band runs 0.12 D
  back along the axis.
- **Resin lumps** (`_lump`): the solid bounded by n planes tangent to a jittered Fibonacci sphere (`_dual_hull`, the
  polar dual of a point hull). Its faces are broad irregular pentagons and hexagons like the sheet's; a hull of points
  read as an icosahedral jewel. The largest faces are poked +2.5 % R (subtle splits).
  - Large: 16 planes, 10 pokes, r 1.32 (part 2.64 × 2.51 × 2.45).
  - Small: 13 planes, 8 pokes, r 1.0 (part 2.19 × 1.92 × 2.04).
- **Leaf clumps** (`_clump`): five kite leaves (the M018 recipe: 8-point outline, two midrib ridge points, a keel) at
  72° ± 12° round a hidden 5-sided hub cone.
  - Chord rise per clump: TL 26–40° and TR 34–50° (they stand up as fans facing the front34 camera); the others 3–9°.
  - The keel sits below the lowest drooped outline point. A keel above the drooped edges made the leaf inside-out
    there, and the exact boolean dropped it.
  - Leaf bases start 0.16 s below the hub point, so each leaf crosses the hub's surface where it has real thickness.
  - Hero clumps are pre-fused (`_fuse_clump`, below) and pasted; each hub snaps to the nearest bark, pad or lump
    (`CLUMP_SNAP` 0.6).
- **Hero assembly:** the body (8 log, knot and pad shells), 6 caps, 2 lumps and 5 pre-fused clumps; one exact union per
  shell (`M.union_loose`); `m004.floor_cut` at z 0; m016's sliver clean; `_finish` and `_polish` (the m012 procedure).
- **Boolean guards:**
  1. `_fuse_clump` rebuilds a clump with the next leaf seed until its fused shell is one closed, outward shell with no
     self-intersection and no corner under 5°. All five passed at attempt 0 in the final build.
  2. The hero guard turns every clump 9° about its axis and rebuilds if the hero fails the same test. A leaf grazing
     D's cap once left a 4-edge hole; the final build passed at attempt 1 (yaw +9°).
  - A stale `matrix_world` after moving a test object put `split_loose`'s shells 400 studs from their base (no union
    at all). Fixed with a view-layer update.

**Stage 1 measurements** (front34 against the f34 cell, the study's classifier `cls()` run on our render):

| | Sheet f34 | Ours front34 |
| --- | --- | --- |
| W : H | 1.316 | 1.403 |
| Shares L / R / C / B | .156 / .302 / .056 / .487 | .169 / .322 / .073 / .436 |
| Large lump centre; size | .196, .389; .391 × .505 | .245, .350; .380 × .470 |
| Small lump centre; size | .792, .586; .259 × .347 | .750, .560; .266 × .336 |
| A top cut end | .692, .909 (n 2306) | .636, .944 (n 1387) |
| B front cut end | .939, .118 (n 2466) | .919, .175 (n 2446) |
| Clumps TL / F / R-low / TR | .297, .708 / .559, .104 / .787, .379 / .857, .863 | .302, .682 / .530, .130 / .790, .372 / .844, .820 |

Top profile, f 0 → 1:
- sheet `.25 .50 .58 .62 .82 .80 .78 .80 .74 .70 .77 .85 .93 .96 .98 .98 .94 .99 1.0 .81 .14`;
- ours `.33 .44 .49 .55 .66 .81 .76 .80 .69 .60 .72 .94 1.0 1.0 .97 .81 .96 .93 .79 .76 .26`.

- **Hero size 7.15 × 5.91 × 4.59** (target 7.0 × 5.9 × 4.45, ±0.35 / ±0.35 / ±0.2: all in). W : D by dims 1.21.
- **Top view:** the X, with B's back end (.091, .923), A's top end face-on (.752, .720), both lumps and four clumps.
  The sheet's top cell is drawn with some perspective, so its pixel W : H (1.116) and ours (1.42) don't compare
  directly.
- **rear34 (flipped), rear, side:** compare by counts (§3). The side cell is not reproducible (§3.5).

## Stage 2: Optimisation and cleanup

| Object | Tris | Size (studs) | Shells | Non-manifold / boundary / wire | Loose / zero-area / dup verts | Min corner | Self-hits |
| --- | --- | --- | --- | --- | --- | --- | --- |
| ResinBranchNode (hero) | 2322 | 7.15 × 5.91 × 4.59 | 1 | 0 / 0 / 0 | 0 / 0 / 0 | 5.01° | 0 |
| ResinBranchBody | 772 | 6.01 × 5.83 × 4.58 | 1 | 0 / 0 / 0 | 0 / 0 / 0 | 5.03° | 0 |
| ResinBranchCutEnd | 120 | 1.02 × 1.04 × 0.24 | 1 | 0 / 0 / 0 | 0 / 0 / 0 | 17.85° | 0 |
| ResinBranchLumpLarge | 70 | 2.64 × 2.51 × 2.45 | 1 | 0 / 0 / 0 | 0 / 0 / 0 | 5.59° | 0 |
| ResinBranchLumpSmall | 54 | 2.19 × 1.92 × 2.04 | 1 | 0 / 0 / 0 | 0 / 0 / 0 | 9.95° | 0 |
| ResinBranchLeafClump | 154 | 1.72 × 1.68 × 0.34 | 1 | 0 / 0 / 0 | 0 / 0 / 0 | 8.91° | 0 |

- No n-gons; normals outward; no custom split normals; transforms applied; origin at the bottom centre (audit origin
  offset 0, 0, 0 on every object); no modifiers. `K.check`: no problems.
- Hero cleanup: 407 collapses and 17 flips in the sliver pass, 2 forced in the polish; 44 ground faces repainted.

## Stage 3: UV

Smart UV at 45°, each island re-unwrapped ANGLE_BASED (the m016 / m012 `UV`), margin 0.008, then `m012._uv_unfold`
on overlaps.

| Object | Islands | Overlap pairs | Flipped | Min gap | Density min / med / max | Conformal stretch p95 |
| --- | --- | --- | --- | --- | --- | --- |
| Hero | 434 | 0 | 0 | 0.016 | 1.0 / 1.0 / 1.0 | 1.009 |
| Body | 86 | 0 | 0 | 0.016 | 1.0 / 1.0 / 1.0 | 1.016 |
| CutEnd | 6 | 0 | 0 | 0.016 | 1.0 / 1.0 / 1.0 | 1.022 |
| LumpLarge | 11 | 0 | 0 | 0.016 | 1.0 / 1.0 / 1.0 | 1.002 |
| LumpSmall | 10 | 0 | 0 | 0.016 | 1.0 / 1.0 / 1.0 | 1.060 |
| LeafClump | 31 | 0 | 0 | 0.016 | 1.0 / 1.0 / 1.0 | 1.018 |

## Stage 4: Materials, colour and texture

Colour is painted by position inside the builders, before the union; the union and cleanup keep each face's key and
Tint. Nothing is coloured by facing.

**Pass 1** (`calibrate()` on the kit dome; the targets are the §5.4 rendered medians) and the final keys after pass 2:

| Key | Target | Pass 1 | Dome render | Final (pass 2) |
| --- | --- | --- | --- | --- |
| m019_bark | #85573A | #69472F | (131, 88, 60) | #614129 |
| m019_bark_light | #9E6743 | #7D5438 | (157, 103, 69) | #734D33 |
| m019_bark_dark | #5F3E2A | #4C3120 | (96, 64, 46) | #462D1D |
| m019_cut | #F1C68C | #C0A179 | (244, 198, 141) | #CAAA80 |
| m019_cut_ring | #E2B074 | #B19064 | (225, 176, 116) | #BA986A |
| m019_join | #E2A862 | #B28A53 | (226, 169, 98) | #B28A53 |
| m019_resin | #FC9407 | #EA7D00 | (255, 148, 20) | #EC8600 |
| m019_resin_light | #FDAA14 | #F98F08 | (255, 171, 24) | #F99A08 |
| m019_resin_dark | #E27602 | #B56500 | (226, 118, 20) | #E67A02 |
| m019_leaf | #5C9E16 | #4D8215 | (89, 154, 22) | #497C14 |
| m019_leaf_tip | #72B41C | #5E941B | (111, 178, 28) | #6BA51E |
| m019_leaf_base | #4F9113 | #447812 | (78, 141, 19) | #447812 |

**Pass 2** (the hero's front34 against the f34 cell, same classifier; median / lit quartile / shade quartile):

| Region | Sheet f34 | Ours front34 |
| --- | --- | --- |
| Bark | #7B5036 / #9F6946 / #4D3321 | #7C5338 / #865A3E / #4F3422 |
| Resin | #FD9406 / #FEBC33 / #DF6F02 | #FFA011 / #FFBD28 / #CF6E0B |
| Cut ends | #F5CB94 / #FDE2B3 / #EDBC7E | #ECC084 / #FFDB9D / #D1A46B |
| Leaves | #5A9B16 / #89C729 / #2D610B | #5D9C18 / #81CA21 / #3B690D |
| Large lump thirds, top / mid / bottom | #FDB01C / #FDA00C / #E57802 (hue 39.3 / 36.4 / 30.6) | #FFB515 / #FF9E0E / #D8700C (hue 41.3 / 35.9 / 29.7) |
| Pale-facet share, large lump (hue 40.5–56, sat ≥ .42, v ≥ .9) | 0.164 | 0.225 |

The body part's unshadowed bark renders #7D5439, against the exploded body's #85573A.

**Pass 2 changes:**
- The dark resin key was raised to the mid key's brightness (#E67A02). The top → bottom gradient is now carried by hue
  (41° → 30°), not brightness, so `K.check`'s facing correlation on the resin fell from 0.85–0.89 to under 0.5 with no
  waiver.
- Resin specular 0.35 → 0.2 and roughness 0.35 → 0.45 (the top facets washed out to white).
- Bark keys × 0.92; cut keys × 1.05; leaf mid × 0.95, the tip key brighter.

**Blends** (3 steps, `_ladder` / `_pick`; every field is a position):
- **Bark:**
  - within 0.55 of a cut end, up to 50 % bark_light;
  - broad noise patches (scale 0.6, level 0.3), 35 % bark_light;
  - z < 0.15, 30 % bark_dark; within 0.25 of a pad top, 25 % bark_dark;
  - floor-cut faces bark_dark (leaf_base under a leaf).
- **Resin:** by height within each lump (±0.06 noise): dark → mid across 0.18–0.42, mid → light across 0.58–0.82.
- **Cut ends:** by loop: cut, ring, cut, ring, cut rim; side band 25 % ring; a hard edge to the bark lip.
- **Leaves:** along each leaf's own length (±0.08 noise): base → mid across 0.18–0.42, mid → tip across 0.58–0.82.
  Keel faces are pulled toward the base; TL and TR shift 0.1 toward the tips; the hub is leaf_base.
- **Join pads:** m019_join, hard edges.

**Tint** (broad, never per triangle): ±4 % per piece (`tint_var` 0.04); bark amp 0.05, scale 0.4 (±1 % jitter); resin
0.025 / 0.7; cut ends 0.03 / 0.9; leaves 0.035 / 0.5.

**Finish:** bark roughness 0.9 (dark 0.95); cut 0.85; join 0.8; resin 0.45 with Specular IOR Level 0.2
(`_resin_spec`); leaves 0.8 with `FOLIAGE_SPEC`. No metal, no emission.

`K.check`: no problems. Baked shading: hero 0.35, body 0.21, lumps 0.0, clump 0.35 (limit 0.5).

## Stage 5: Lighting

Nothing to add: "No glow baked into model". There is no emissive key (the exporter would flatten the lumps to Neon) and
no light.

Studio note (Requires Manual Validation): check that the resin doesn't clip to flat orange under the game's sun, and
that the top → bottom hue gradient survives the palette export.

## Stage 6: VFX

Two `ore_glint` sockets: the sheet's pale four-point sparkle stars round each lump. Texture `spark_diamond`, colours
`#F9E4C4` → `#FBD28E`, lifetime 0.6–0.9, `light None`.

| Socket | Local position (hero) | Size | Rate | Box (Roblox X, Y, Z) |
| --- | --- | --- | --- | --- |
| VFX_ResinBranchNode_ore_glint_1 (large lump centre) | (−2.30, −0.63, 1.45) | 0.9 | 2.5 | 4.24, 4.06, 4.11 |
| VFX_ResinBranchNode_ore_glint_2 (small lump centre) | (1.61, −0.73, 2.15) | 0.65 | 1.5 | 3.40, 3.34, 3.34 |

Renders are made with `vfx=True`; the sparkles show as small pale diamonds. The export STATS line is for the main
session to check (no exports here).

## Modeller's notes for the verifier

- Compare the sheet's Front cell with `front_sheet.png` (−28, 6) and the f34 with `front34.png`; the r34 with
  `rear34.png` **flipped**; the rear by its logs; the side by counts only (§3).
- **Known misses:**
  - The front34 bark share is .436 against .487 (−5.1; tolerance ±4), and W : H is 1.403 against 1.316 (tolerance
    1.28–1.38). The lumps and clumps take a little more of the picture than the sheet's; thicker logs and a narrower
    layout closed most of the gap.
  - A_up's top cut end is at f .636 (sheet .692) and smaller (n 1387 against 2306). The sheet draws it facing the
    viewer although the log rises away from the camera; the elbow plus the 35° oblique cut is the compromise. From the
    side view A_up's top reads slightly hooked.
  - The large pad shows a small tan corner under the large lump in front34, where the sheet shows none. From below it
    reads as the "Flat Join Surface".
  - rear34 colours are much darker than the sheet's r34 (bark #5B3D2B against #815539). The kit studio lights the rear
    views from behind; the sheet lights every view from the front. Paint can't fix that without breaking the front.
  - The top cell's pixel W : H doesn't compare (the sheet's top is drawn in perspective); W : D by dims is 1.21.
- **Close-ups:**
  - `junction.png`: the crotch is filled by the knot, with no seam;
  - `cut_end.png`: a thick 10-sided insert with two ring bands and a bark lip;
  - `underside_pad.png`: the pad under the large lump.
- The hero clumps are temporary pre-fused objects (`_m019_clump_*`), removed at the end of `build()`; nothing named
  `_m019_*` is left in the file.

## Stage 7 — Verification (round 1)

Independent verifier, 2026-10-28. Read-only background session on port 9881 with `wip/M019_verify.blend` (not saved;
no `build()`). Fresh renders went to the session scratchpad (`v019/renders/M019/`), not to this folder. Every number
below was re-measured. Sheet and render were compared with the study's classifier (`cls()`, the same masks).

**Result: FAIL, 6/10.** The technical side is clean, and the front34 hero, leaves and resin colours match well. One
blocker: A_up's elbow and oblique cut make the main limb read as a hooked horn with no cut end in the side, rear and
rear34 views. The sheet's second focal silhouette is a straight log with a flat cream disc on top.

### Technical (all pass)

| Object | Tris / budget | Size | Shells | NM / bnd / wire | Loose / zero / dup | N-gons | Min corner | Self-hits | Interior / inverted faces | UV overlaps / flips / min gap |
| --- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- |
| ResinBranchNode | 2322 / 4000 | 7.15 × 5.91 × 4.59 | 1 | 0/0/0 | 0/0/0 | 0 | 5.01° | 0 | 0 / 0 | 0 / 0 / 0.016 (434 islands) |
| ResinBranchBody | 772 / 1000 | 6.01 × 5.83 × 4.58 | 1 | 0/0/0 | 0/0/0 | 0 | 5.03° | 0 | 0 / 0 | 0 / 0 / 0.016 |
| ResinBranchCutEnd | 120 / 1000 | 1.02 × 1.04 × 0.24 | 1 | 0/0/0 | 0/0/0 | 0 | 17.85° | 0 | 0 / 0 | 0 / 0 / 0.016 |
| ResinBranchLumpLarge | 70 / 1000 | 2.64 × 2.51 × 2.45 | 1 | 0/0/0 | 0/0/0 | 0 | 5.59° | 0 | 0 / 0 | 0 / 0 / 0.016 |
| ResinBranchLumpSmall | 54 / 1000 | 2.19 × 1.92 × 2.04 | 1 | 0/0/0 | 0/0/0 | 0 | 9.95° | 0 | 0 / 0 | 0 / 0 / 0.016 |
| ResinBranchLeafClump | 154 / 1000 | 1.72 × 1.68 × 0.34 | 1 | 0/0/0 | 0/0/0 | 0 | 8.91° | 0 | 0 / 0 | 0 / 0 / 0.016 |

- **How interior and inverted faces were tested:** a 3-ray parity test on points 1e-3 in front of and behind every face.
- **Every object:**
  - normals outward and no custom normals;
  - rotation 0 and scale 1; no modifiers;
  - origin at the bottom centre (offset 0, 0, 0; world min z 0.0);
  - UV layer `UVMap`, density 1.0 / 1.0 / 1.0;
  - `K.check`: no problems.
- **Size against the decided 7.0 × 5.9 × 4.45 (±0.35 / ±0.35 / ±0.2):** in.
- **Materials:** all Principled, metal 0, emission 0 on every key. Resin: roughness 0.45, spec 0.2. Leaves:
  roughness 0.8. Bark: 0.9 / 0.95.
- **Resin colouring:** the key rank correlates with face height at 0.97 and with normal z at 0.92. On a convex lump,
  height and facing go together. The keys differ mainly in hue: light `#F99A08` 37°, mid `#EC8600` 34°, dark `#E67A02`
  32°, with value only 0.98 → 0.90. `K.check` measures 0.0 baked shading on both lumps. This is a position-based
  painted gradient, which the sheet shows (its lit bottom quartile is still red). **Accepted, not colouring by facing.**
- **VFX:** two `ore_glint` sockets, `spark_diamond`, colours `#F9E4C4` → `#FBD28E`, `light None`.
  - Large: (−2.30, −0.63, 1.45), box 4.24 × 4.06 × 4.11.
  - Small: (1.61, −0.73, 2.15), box 3.40 × 3.34 × 3.34.
  - Both socket points sit inside their lumps, 1.03 and 0.79 below the surface. By Monte Carlo of the spawn box:
    - large: 14 % of spawns below ground and 19 % inside the mesh, so 33 % are wasted;
    - small: 21.5 % inside the mesh.
  - The renders show one sparkle on B's top, about 1.2 studs from the large lump.

### Views (sheet cell against render, same classifier)

| View | W : H | Shares L / R / C / B | Notes |
| --- | --- | --- | --- |
| f34 / front34 | 1.316 / 1.399 | .156 .302 .056 .487 / .169 .322 .073 .436 | Large lump (.245, .349) against (.196, .389); small lump (.747, .561) against (.792, .586). A top cut (.634, .942), 0.124 W, n 1438, against (.692, .909), 0.146 W, n 2306. B front (.916, .189) against (.939, .118). Clumps TL / TR / F / R-low within 0.03. |
| front cell / front_sheet | 1.259 / 1.514 | .158 .300 .056 .486 / .158 .329 .069 .443 | The same picture as f34. |
| r34 / rear34 | 1.274 / 1.794 | .184 .169 .052 .595 / .164 .139 .033 .663 | Compared **unflipped**: it matches better than the flip (§3.3). Large lump .236 against .155. B front end (.943, .189) against (.944, .110). **A_up top disc missing** (sheet .603, .910). The small lump is mostly hidden (n 1106 against 8605). 2 clumps + a sliver against 4. |
| rear | 1.129 / 1.474 | .264 .249 .065 .422 / .146 .131 .053 .671 | **A top disc missing** (sheet .291, .945): A_up ends in a bark point. B back at h .20 (sheet .51). |
| side | 0.807 / 1.046 | .133 .453 .039 .376 / .180 .188 .016 .617 | Known unreproducible. **No disc on top**: A_up reads as a curved blade or horn with a pointed tip. |
| top | 1.116 / 1.404 | .177 .284 .089 .449 / .173 .290 .089 .449 | The X reads. B back and A top discs are present; **B front disc not visible from the top** (turned to the side). Back and right clumps sit about 0.15 off (perspective cell). |

- **front34 against f34 overall.** Good:
  - two broad-faceted lumps at the right places and sizes;
  - leaves vivid, with 4 clumps at the sheet's positions;
  - the B front cut end and the A top cut end show;
  - the logs' thickness matches (A_up perpendicular width about 0.15 W in both).
- **Differences in front34:**
  - A_up rises steeper on screen (about 67° against the sheet's 55°);
  - stubs C and D show (the sheet hides them), plus B_back's end at the far left;
  - so the pile reads slightly more "several sticks" than the sheet's one fused fork.
- **Lumps:** 8–10-corner outlines (pass). The internal facets are coarser than the sheet's: the pokes are barely
  visible, so each lump shows about 9 big faces where the sheet shows the same faces split into tonal triangles.
- **Cut end close-up:** a thick 10-sided insert with two ring bands and a bark lip (pass). The rings are stronger than
  the sheet's faint ones.
- **Junction close-up:** fused, no seam (pass).
- **Join pads:**
  - pad 1 shows in front34 and the junction close-up as a sharp tan triangular shard under the large lump, not a
    hexagonal flat block;
  - pad 2 has no visible faces in the hero (no `m019_join` faces survive near D).

### Colours (sheet / ours, median; lit and shade quartiles where useful)

| Region | Sheet | Ours | Δ (R, G, B) |
| --- | --- | --- | --- |
| Bark f34 | #7B5036 (lit #9F6946, shade #4D3321) | #7B5338 (#865A3E, #503422) | 0, +3, +2 (lit −25, −15, −8) |
| Bark near cut ends / far | #89583A / #6F4B34 (+26 lighter near) | #7A5239 / #7B5338 (no lift) | near −15, −6, −1 |
| Bark ground band | #603F2B | #5E3E29 | −2, −1, −2 |
| Large lump top / mid / bottom | #FDB01C / #FD9F0C / #E57802 (39.5 / 36.6 / 31.2°) | #FFB515 / #FF9E0E / #D8700C (41.0 / 35.9 / 29.4°) | +2, +5, −7 / +2, −1, +2 / −13, −8, +10 |
| Small lump top / mid / bottom | #FD9F07 / #FD9503 / #DC7102 | #FFCB4C / #FFAE28 / #FE801C | **+2, +44, +69** / +2, +25, +37 / +34, +15, +26 |
| Resin, all lumps | #FD9406 (#FEBC32, #DF6F02) | #FFA011 (#FFBD26, #CF6E0B) | +2, +12, +11 |
| Cut end, B front | #F2C78F (#F9D39F, #EDBD81) | #DBB17D (#F8C98F, #CDA16A) | **−23, −22, −18** |
| Cut end, A top | #FCD7A2 | #FFD296 | +3, −5, −12 |
| Leaves f34 | #5A9B16 (#89C728, #2D610C) | #5E9D1C (#83CB26, #3C6910) | +4, +2, +6 |

### Itemised findings

**Blocker**
1. **A_up reads as a hooked horn, and its top cut end is missing from the side, rear and rear34.**
   - **What's wrong.** The sheet shows A_up as a straight log with a flat cream disc on top in 5 of 6 views. Ours shows
     the disc only in front34 and top.
   - **Cause.** The elbow (`A_UP` elbow 0.7, turn 0.5, last 1.15) bends the last 1.15 studs 50 % toward a cut normal
     leaning toward the front34 camera. From +X and +Y the end is a curved blade with a pointed bark tip.
   - **Fix (in `m019.py`):**
     - set `A_UP["turn"] = 0` (a straight log from J to `aim`);
     - set the cut normal mostly up with a small front lean, e.g. `A_UP["n"] = (0.45, 0.8, 0.3)` (about 30–35° off
       the axis);
     - keep the top of the cut at z ≈ 4.45–4.6;
     - check that the 10-sided cap is still pasted on the new end plane.
   - **Acceptance:**
     - front34: A top disc n ≥ 1400 px at 480 × 400, centre within 0.06 of (.692, .909);
     - side and rear: A_up ends in a flat top with a cream disc rim (C component ≥ 150 px at the top), and no pointed
       or hooked tip;
     - rear34: the disc rim is visible (the kit's 12° camera can't show it face-on; record that);
     - all stage-2 numbers still clean.

**Minor**

2. **Large join pad: a tan shard under the large lump** in front34 and the junction close-up (`PAD_LEAN` 45 % front-down
   makes a corner stick out). Small lump's pad 2 is invisible.
   - **Fix:** aim pad 1 along the line from the log axis to the lump centre, with `PAD_LEAN` reduced to about 15 %, so
     only an even hexagonal rim shows under the lump front-bottom (no corner past the lump's silhouette in front34).
   - Give pad 2 about 0.05 more height so its rim survives the union.
3. **The small lump's top third washes to pale cream** (`#FFCB4C` against `#FD9F07`). 301 px of it classify as cut
   wood in front34.
   - **Fix:** on the small lump only, cap the top band at `resin_x_light_50` (or the light key with value × 0.94).
   - Re-measure the top third within 15 of `#FD9F07`.
4. **The B front cut end renders 20 levels too dark** (`#DBB17D` against `#F2C78F`). The ring bands are too strong.
   - **Fix:** raise `m019_cut` by about 6 %.
   - Pull `m019_cut_ring` to about 60 % of its current contrast against `cut` (the sheet's rings are faint).
5. **No lighter bark near the cut ends in the render** (near `#7A5239` = far `#7B5338`; the sheet is +26 lighter near).
   Lit-quartile bark is 25 levels darker than the sheet.
   - **Fix:** widen the near-cut-end blend to 0.7 and raise it to 70 % `bark_light`, or brighten `bark_light` about 10 %.
6. **Stubs C and D and B_back's end are more visible in front34 than on the sheet** (it reads slightly as several
   sticks).
   - Optional: slide D back about 0.3 behind the small lump (front34 depth rule §2) and shorten B_back about 0.3.
7. **VFX spawn boxes partly buried.**
   - **What's wrong.** The socket points are inside the lumps, and the large box reaches z −0.58: 33 % (large) and 21 %
     (small) of spawns are hidden.
   - **Fix:**
     - large: raise the socket to z 1.95 and set its box height (Roblox Y) to 3.0, so the bottom is at about 0.45;
     - optionally move both sockets about 0.3 toward the upper-front-left of their lumps (where the sheet's stars are).
   - Re-run the Monte Carlo: target ≤ 15 % hidden.
8. **The B front disc isn't visible from the top** (sheet .836, .076): it's turned 38° toward front34. This is
   accepted as a hero-first compromise; record it.
9. **Lump facets are coarser than the sheet's** (pokes at +2.5 % R hardly read).
   - Optional: poke height 4–5 %, or a 0.03 tone offset per poked triangle via Tint.
10. **Small lump part bbox is 2.19 × 1.92 × 2.04** against the decided Ø 1.8 (it reads right in the hero: 0.259 W
    against the sheet's 0.256).
    - Optional: tighten its x squash.
11. **The leaf blend materials** (`m019_leaf_x_*`, `m019_leaf_base_x_*`) **have spec 0.2,** where the base keys have
    the low foliage spec 0.06. This is render-only (Roblox ignores it); add the mix keys to `LOW_SPEC` for consistent
    renders.
12. **Exploded shot:** the large lump overlaps the body and two clumps hide behind the lumps. This is the comparison
    render only.

**Known misses accepted per the study:**
- the rear's swapped lumps (§3.4);
- the side's narrow W : H (§3.5);
- the top's perspective (§3.6);
- rear34 lighting (the kit lights the rear from behind);
- front34 W : H 1.40 against 1.28–1.38 and bark share −5.1 (borderline; they should improve with fix 1).

## Round 2 fixes (modeller)

Fresh modeller, 2026-10-28. Background session on port 9878 with `wip/M019.blend` (saved after the final build).
Everything changed is in `m019.py` (`build()`); no shared helper was touched. Measured with the study's classifier
(`cls()`) through the verifier's `cmp.py`, `thirds.py` and `sock.py`, on the new renders in this folder.

### Findings

| # | Finding | Result | Measured (sheet / ours) |
| --- | --- | --- | --- |
| 1 | **Blocker: A_up a hooked horn** | **Fixed** | A straight log with a flat cut top and a cream disc or rim in every view (below). |
| 2 | Large pad shows a tan shard; pad 2 invisible | Shard gone; both pads now hidden | 0 `m019_join` faces in the hero (§2 below). |
| 3 | Small lump top washes to cream | Fixed | top / mid / bottom: #FD9F07 / #FD9503 / #DC7102 against #FF9C12 / #FF970E / #E97809 (top +2, −3, +11) |
| 4 | B front cut end 20 levels dark; rings too strong | Fixed | #F2C78F against #ECBE87 (−6, −9, −8); rings at about 40 % of round 1's contrast |
| 5 | No lighter bark near the cut ends | Fixed | near / far: #89583A / #6F4B34 against #82583D / #67442D (luma lift: sheet +16, ours +22) |
| 6 | Stubs and B_back show ("several sticks") | Partly | B_back 0.3 shorter and D 0.25 further back; D still shows between A_up and the small lump |
| 7 | VFX spawn boxes buried | Fixed | hidden: large 33 % → 13.2 %, small 21.5 % → 13.2 %; 0 % below the ground |
| 8 | B front disc not visible from the top | Accepted (hero first) | B_front's turn is now −30° (was −38°); still not seen from the top |
| 9 | Lump facets coarser than the sheet's | Not done (optional) | |
| 10 | Small lump part 2.19 wide | Fixed (optional) | x squash 1.0 → 0.92: the part is 2.04 × 1.88 × 2.04 |
| 11 | Leaf blend materials at spec 0.2 | Fixed | all 9 `m019_leaf*` materials at 0.06 |
| — | §3.3 mirror claim | Corrected | The rear34 matches the sheet's r34 **unflipped**, not mirrored, as the verifier found. §3.3 and the modeller's note to the verifier are wrong. |

### 1. A_up (the blocker)

**What changed:**
- **A straight log.** `A_UP = dict(aim=(3.1, 1.75, 4.1), tilt=(20, 0))` gives a two-point path from J to the cut
  end's centre. The elbow code is gone.
- **The cut.** Its normal is tilted 20° off vertical toward the front (azimuth 0), about 57° off the log axis.
- **Ring clearance.** `_tube(end_clear=…)` (`END_CLEAR["A_up"] = 1.3`) pulls the inner rings back along the straight
  axis, so the ring before the end clears the slanted cut's low side.
  - Without it, the end ring crossed the previous ring.
  - The body alone still unioned, but the hero failed every guard attempt (7 shells, 6 self-hits).
- **A thicker log.** Ø 1.50 → 1.38 (was 1.46 → 1.24): the sheet's top disc is 0.146 W wide, round 1's 0.124.
- **A thicker insert with a deeper rim chamfer.**
  - `CAP_PROUD_END["A_up"]` is 0.18 D (other ends 0.08); `CAP_BEVEL_END["A_up"]` is 0.10 D (others 0.025).
  - The chamfer facets face sideways, so a lit cream rim shows from the rear and rear34, where the face itself turns
    away.
- **Heights.** The cut top is at z 4.55. The hero's z of 4.63 is the TR leaf tip.

**Acceptance** (renders in this folder at 480 × 400; the C component at the top):

| View | Sheet | Ours | Pass |
| --- | --- | --- | --- |
| front34 | disc (.692, .909), n 2306 | disc (.683, .933), n 1531, 0.026 off | ✓ (n ≥ 1400, within 0.06) |
| side | disc (.610, .927), n 574 | flat slanted cream face (.772, .921), n 1487 | ✓ (n ≥ 150) |
| rear | disc (.291, .945), n 461 | cream rim along a flat top (.150, .972), n 380 | ✓ (n ≥ 150) |
| rear34 | disc (.603, .910) | cream rim (.218, .972), n 568 | ✓ rim visible; the kit's 12° camera can't show the face |

**Shape.** There is no hook or bark point in any view.
- From the side, A_up is a straight log with a flat slanted cut, and its cream face shows.
- From the rear and rear34, it is a straight log whose top is a flat slanted cut with a cream rim.
- The slant is the price of the front34 disc. On a 47° log, a cut that faces the front34 camera is about 57°
  oblique. From the side its high end makes an acute corner, but the cream face shows there, so it reads as a saw
  cut, not a point.

**Tried and rejected:**

| Cut normal | front34 disc | Why rejected |
| --- | --- | --- |
| The verifier's example, weights (0.45, 0.8, 0.3) | n 281, a sliver | Fails the 1400 px acceptance. |
| 12–15° toward the front34 camera | n 1322–1659 | Passes, but the side shows a sharper blade with no face visible. |
| 54° off the axis, straight at the camera | n 1399 | A big face from the side, but no cream at all from the rear. |

### 2. Join pads

**Why they can't show.** Both lumps straddle their logs: the large lump's centre is 0.80 from A_low's axis (inside
the log's top), and the small lump's centre is 0.27 from D's axis.
- Aimed from the axis at the lump with a lean of 0.15, the pad ends wholly inside the lump.
- Leans of 0.3–0.4 also stay hidden, and 0.45 pokes round 1's corner out.
- A 0.7-radius block leaning 85 % to the front-left showed a large tan hexagon under the large lump in front34. The
  sheet shows nothing there.

**Result.**
- The hero has no tan shard in front34 and no pad from below.
- The Body part keeps both pads (the sheet's "Flat Join Surface").
- Pad 2 is 0.05 prouder (0.23), as asked, but is still inside the lump.

**For the main session.** The sheet's underside close-up shows a lump sitting on a hexagonal block. That doesn't fit
the sheet's own hero, where the lump hangs over A_low.

### 3–5 and 11. Colour

**Bark near the cut ends (finding 5).**
- Round 1 measured the straight distance from a face to the end's centre, with a 0.55 limit. No bark face is that
  close on a 1.3-stud log, so nothing was lifted.
- `end_dist` now measures back along each log's axis from its (oblique) end plane, for faces within 2 r of the axis.
- Up to 75 % `bark_light` within about 0.33 of the lip, fading to nothing at 1.0 (`BARK_FIELD` near 1.0, near_mix
  0.75).

**The small lump.**
- Its top band stops at ladder index 6 (`resin_x_light_50`, `LUMP_TOP`).
- It has a uniform Tint factor of 0.78 (`LUMP_TINT`). It sits high in the key light and rendered brighter than the
  large lump.

**The washed facets were specular, not paint.**
- The small lump's upper-left facets caught a grazing white reflection: #FFDE9A, about 820 px classed as cut wood.
  With specular 0 they render #FE8701.
- `RESIN_SPEC` 0.2 → 0.08 and resin roughness 0.45 → 0.7. No washed facet is left: 0 C-class pixels on the small
  lump.
- `_resin_spec()` now:
  - sets every resin key, mix keys included, to that roughness;
  - sets every `m019_leaf*` key to the kit's foliage spec, 0.06. K.mix_key creates a mix key's material after setting
    its colour, so those materials kept flintkit's 0.2.

**Calibration pass 1** (`calibrate()` on the kit dome, the changed keys):
- bark #66442B and bark_light #7A5236 (both converged at once);
- cut #BDA178 and cut_ring #B29064;
- resin #E97D00, resin_light #F78D0C and resin_dark #B46600, at the new finish.

**Calibration pass 2** (the hero's front34 against the sheet's f34, same classifier):

| Region | Sheet (median / lit / shade) | Ours (median / lit / shade) |
| --- | --- | --- |
| Bark | #7B5036 / #9F6946 / #4D3321 | #81573B / #916142 / #5B3A26 |
| Resin | #FD9406 / #FEBC32 / #DF6F02 | #FF9B0C / #FFB50F / #CF6A04 |
| Cut ends | #F5CB94 / #FDE2B3 / #EDBC7E | #F7CD95 / #FFEDAE / #E0B37C |
| Leaves | #5A9B16 / #89C728 / #2D610C | #5C9A18 / #81CA20 / #3B660E |
| Large lump, top / mid / bottom | #FDB01C / #FD9F0C / #E57802 | #FFB60F / #FF9E08 / #D96F06 |
| A top cut end (median) | #FCD7A2 | #FFE4A3 |

**Final keys (`PALETTE`):**

| Key | Hex | Source |
| --- | --- | --- |
| bark | #614129 | round 1's pass-2 value; the dome's #66442B made the hero median 12 levels light |
| bark_light | #7A5236 | the dome value |
| bark_dark | #462D1D | unchanged |
| cut | #E6C192 | pass 1 × 1.18, from pass 2 on B's front end |
| cut_ring | #D8B384 | about 40 % of round 1's contrast against cut |
| join | #B28A53 | unchanged |
| resin | #EC8600 | unchanged; pass 2 still matches at the new finish |
| resin_light | #F99A08 | unchanged |
| resin_dark | #E67A02 | unchanged |
| leaves | unchanged | |

**Finish:**
- resin: roughness 0.7, spec 0.08;
- leaves: 0.8, spec 0.06, mix keys included;
- bark: 0.9 / 0.95;
- cut: 0.85.

### 6, 7 and 10. Layout, VFX and the small lump

**Layout.**
- B_back's end (−2.8, 2.7, 1.05) → (−2.60, 2.48, 1.02).
- D: (0.74, −1.10) → (2.85, 0.0) is now (0.74, −0.85) → (2.85, 0.25). Its foot is still inside B.
- B_front's end turn −38° → −30°. Its disc was 0.157 × 0.247 of the front34, against the sheet's 0.132 × 0.204.

**VFX** (`GLINTS`, a shift from the lump centre plus a box height; Monte Carlo of 3000 points, 3-ray parity):

| Socket | Position (shift) | Box (Roblox X, Y, Z) | z range | Hidden |
| --- | --- | --- | --- | --- |
| Large | (−2.67, −1.04, 2.30); shift (−0.35, −0.55, +0.85) | 4.24, 3.0, 4.11 | 0.8–3.8 | 13.2 % |
| Small | (1.19, −1.29, 3.05); shift (−0.4, −0.7, +0.9) | 3.24, 2.6, 3.34 | 1.75–4.35 | 13.2 % |

- Both shifts go toward each lump's upper front-left.
- Nothing is below the ground.
- The verifier's suggested z of 1.95 for the large socket still left 19.9 % hidden.

**The small lump.** Its x squash is 1.0 → 0.92.

**Tried and rejected: thicker logs** (+3–5 % on A_up, B and the stubs, to recover bark share). The B share rose to
.449, but the hero guard failed every attempt (6–12 self-hits), so they were reverted.

### Technical (final build, all re-measured)

| Object | Tris / budget | Size | Shells | NM / bnd / wire | Min corner | Self-hits | UV islands / overlaps / min gap |
| --- | --- | --- | --- | --- | --- | --- | --- |
| ResinBranchNode | 2362 / 4000 | 7.19 × 5.75 × 4.63 | 1 | 0 / 0 / 0 | 5.06° | 0 | 439 / 0 / 0.016 |
| ResinBranchBody | 784 / 1000 | 6.94 × 5.71 × 4.43 | 1 | 0 / 0 / 0 | 5.06° | 0 | 104 / 0 / 0.016 |
| ResinBranchCutEnd | 120 / 1000 | 1.02 × 1.04 × 0.24 | 1 | 0 / 0 / 0 | 17.85° | 0 | 6 / 0 / 0.016 |
| ResinBranchLumpLarge | 70 / 1000 | 2.64 × 2.51 × 2.45 | 1 | 0 / 0 / 0 | 5.59° | 0 | 11 / 0 / 0.016 |
| ResinBranchLumpSmall | 54 / 1000 | 2.04 × 1.88 × 2.04 | 1 | 0 / 0 / 0 | 7.29° | 0 | 12 / 0 / 0.016 |
| ResinBranchLeafClump | 154 / 1000 | 1.72 × 1.68 × 0.34 | 1 | 0 / 0 / 0 | 8.91° | 0 | 31 / 0 / 0.016 |

- Every object: normals outward; no n-gons; no loose or zero-area elements; UV density 1.0 / 1.0 / 1.0.
- `K.check`: no problems. The hero passed at guard attempt 0. No `_m019_*` objects are left.
- Size against 7.0 × 5.9 × 4.45 (±0.35 / ±0.35 / ±0.2): in.

### Views now (front34 against the sheet's f34)

| | Sheet | Round 1 | Round 2 |
| --- | --- | --- | --- |
| W : H (tolerance 1.28–1.38) | 1.316 | 1.399 | **1.324** |
| Shares L / R / C / B | .156 / .302 / .056 / .487 | .169 / .322 / .073 / .436 | .169 / .341 / .059 / .430 |
| Large lump | (.196, .389) | (.245, .349) | (.225, .353) |
| Small lump | (.792, .586) | (.747, .561) | (.748, .577) |
| B front disc | (.939, .118) | (.916, .189) | (.940, .187) |

**The bark share is still −5.7.** Two things cause it:
- With the spec fix, the lumps' former pale and washed pixels now class as resin (R +3.9, inside ±4).
- The shorter B_back removed some bark. W : H needs that change: without it, W : H is 1.399.

Thicker logs would recover the bark share, but they broke the union (above).

**Other views.**
- **B front disc:** still 0.07 too high in the image, as in round 1.
- **Top:** the A disc is now a large slanted ellipse, 0.31 × 0.37 against the sheet's 0.18 × 0.20. It faces up, so it
  reads strongly from the top.
- **Rear and side:** as in the acceptance table. The known misses (§3.4–3.6) and the rear lighting are unchanged.

## Stage 7 — Verification (round 2)

Independent verifier (not the round-1 verifier, no other stage), 2026-10-28. Read-only background session on port 9881
with `wip/M019_verify.blend` (not saved; no `build()`). Fresh renders (`render_views`, vfx on) went to the session
scratchpad `v019r2/renders/M019/`, not to this folder. Every number below was re-measured; sheet and renders were
compared with the study's classifier (`cls()`, same boxes and masks).

**Result: PASS, 7/10.** Technically clean; the hero front34 matches the sheet's f34 in layout, sizes and colour, and
the round-1 hook is gone. The main leftover is A_up's steep oblique cut, which reads as a chisel or plank tip from the
side, rear and rear34. It has no cheap fix: it is forced by the layout (below), so it is recorded rather than failed.

### Technical (all pass)

| Object | Tris / budget | Size | Shells | NM / bnd / wire | Loose / zero / dup | N-gons | Min corner | Self-hits | Interior / inverted | UV islands / overlaps / flips / min gap / p95 stretch |
| --- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- |
| ResinBranchNode | 2362 / 4000 | 7.19 × 5.75 × 4.63 | 1 | 0/0/0 | 0/0/0 | 0 | 5.06° | 0 | 0 / 0 | 439 / 0 / 0 / 0.016 / 1.016 |
| ResinBranchBody | 784 / 1000 | 6.94 × 5.71 × 4.43 | 1 | 0/0/0 | 0/0/0 | 0 | 5.06° | 0 | 0 / 0 | 104 / 0 / 0 / 0.016 / 1.018 |
| ResinBranchCutEnd | 120 / 1000 | 1.02 × 1.04 × 0.24 | 1 | 0/0/0 | 0/0/0 | 0 | 17.85° | 0 | 0 / 0 | 6 / 0 / 0 / 0.016 / 1.022 |
| ResinBranchLumpLarge | 70 / 1000 | 2.64 × 2.51 × 2.45 | 1 | 0/0/0 | 0/0/0 | 0 | 5.59° | 0 | 0 / 0 | 11 / 0 / 0 / 0.016 / 1.002 |
| ResinBranchLumpSmall | 54 / 1000 | 2.04 × 1.88 × 2.04 | 1 | 0/0/0 | 0/0/0 | 0 | 7.29° | 0 | 0 / 0 | 12 / 0 / 0 / 0.016 / 1.002 |
| ResinBranchLeafClump | 154 / 1000 | 1.72 × 1.68 × 0.34 | 1 | 0/0/0 | 0/0/0 | 0 | 8.91° | 0 | 0 / 0 | 31 / 0 / 0 / 0.016 / 1.018 |

- Interior and inverted faces: 3-ray parity test 1e-3 in front of and behind every face. No face under 5°.
- Every object: normals outward, no custom normals, rotation 0, scale 1, no modifiers, origin at the bottom centre
  (offset 0, 0, 0; world min z 0.0), UV layer `UVMap` at density 1.0 / 1.0 / 1.0, Tint corner colours present.
  `K.check`: no problems. No `_m019_*` leftovers.
- **Size** against 7.0 × 5.9 × 4.45 (±0.35 / ±0.35 / ±0.2): +0.19 / −0.15 / +0.18, in (H only just; the top is the
  TR leaf tip, the A_up cut top is at 4.55).
- **Materials:** 27 keys on the hero, all Principled, metal 0, emission 0. Bark 0.9 (dark 0.95); cut 0.85; resin
  roughness 0.7, spec 0.08 (mix keys too); leaves 0.8, spec 0.06 (all nine `m019_leaf*` keys, round-1 finding 11 fixed).
- **Colour by facing:** the resin key rank correlates with face height at 0.97 / 0.96 (large / small) and with normal z
  at 0.93 / 0.91. That is the convex lump, not facing: the keys differ mainly in hue (light `#F99A08`, mid `#EC8600`,
  dark `#E67A02`), and `K.check` reports 0.0 baked shading on both lumps. Accepted, as in round 1. The small lump's
  top stops at `resin_x_light_50` (no light / light_75 faces), as round 2 intended.
- **VFX:** two `ore_glint` sockets, `spark_diamond`, `#F9E4C4` → `#FBD28E`, `light null`.
  - Large (−2.67, −1.04, 2.30), box 4.24 × 3.0 × 4.11, z 0.80–3.80: 0 % below ground, **13.2 % inside the mesh**.
  - Small (1.19, −1.29, 3.05), box 3.24 × 2.6 × 3.34, z 1.75–4.35: 0 % below ground, **13.2 % inside the mesh**.
  - Monte Carlo, 3000 points per box. Both are under the 15 % target (round 1: 33 % and 21.5 %).

### Round-1 findings

| # | Round 1 | Now |
| --- | --- | --- |
| 1 | **Blocker:** A_up a hooked horn, no cut end from side, rear, rear34 | **Fixed as asked:** a straight log, no hook; cream face or rim in every view. A new leftover follows from it (L1). |
| 2 | Large pad shard; pad 2 invisible | Shard gone. Both pads are now wholly hidden in the hero (L5). |
| 3 | Small lump top washed to cream | Fixed: top / mid / bottom `#FF9C12` / `#FF970E` / `#E97809` against `#FD9F07` / `#FD9503` / `#DC7102`. |
| 4 | B front cut end 20 levels dark; strong rings | Fixed: `#ECBE87` against `#F2C78F` (−6, −9, −8). Rings faint, like the close-up. |
| 5 | No lighter bark near cut ends | Fixed: near / far `#82583D` / `#67452D`, a lift of +21 luma (sheet `#89583A` / `#6F4B34`, +16). |
| 6 | Stubs and B_back show ("several sticks") | Partly: B_back no longer pokes out, but D still shows between A_up and the small lump with a gap behind it (L3). |
| 7 | VFX spawn boxes buried | Fixed (13.2 % / 13.2 %). |
| 8 | B front disc not visible from the top | Accepted as before. |
| 9 | Lump facets coarse | Not done (optional); still a minor. |
| 10 | Small lump part 2.19 wide | Fixed: 2.04 × 1.88 × 2.04. |
| 11 | Leaf mix keys at spec 0.2 | Fixed (0.06). |

### Views (sheet cell / our render, same classifier)

| View | W : H | Shares L / R / C / B | Components |
| --- | --- | --- | --- |
| f34 / front34 | 1.316 / **1.324** ✓ | .156 .302 .056 .487 / .169 .341 .059 .430 (B −5.7, outside ±4) | Large lump (.196, .389) / (.225, .353), .388 × .502 / .399 × .469 ✓. Small lump (.792, .586) / (.748, .577), .256 / .266 W ✓. A top disc (.692, .909) / (.683, .933), n 2306 / 1531 ✓. B front disc (.939, .118) / (.940, .187), Δh .069 (just outside .06). Four clumps at their places. |
| front cell / front_sheet | 1.259 / 1.418 | .158 .300 .056 .486 / .163 .341 .058 .438 | The same picture as the f34. |
| top | 1.116 / 1.371 (perspective cell) | .177 .284 .089 .449 / .158 .257 **.138** .447 | A top disc 0.309 × 0.368 (sheet 0.182 × 0.198, about 3× the area). B back disc ✓. B front disc not seen (accepted). |
| r34 / rear34 | 1.274 / 1.724 | .184 .169 .052 .595 / .133 .114 .048 .705 | Rim of A's top disc only; both lumps; 3 clumps. Dark from the kit's back lighting (known). |
| rear | 1.129 / 1.603 | .264 .249 .065 .422 / .100 .137 .078 .685 | A top: a thin cream rim along a slanted wedge top (.150, .972). Lumps mostly hidden (sheet §3.4 known). |
| side | 0.807 / 1.191 | .133 .453 .039 .376 / .161 .160 .037 .642 | Not reproducible (§3.5). A_up's cut is a 0.353 × 0.22 slanted strip (sheet's disc 0.181 × 0.146). |

Top profile, front34 against f34 (f 0 → 1): sheet `.25 .50 .58 .62 .82 .80 .78 .80 .74 .70 .77 .85 .93 .96 .98 .98
.94 .99 1.0 .81 .14`; ours `.33 .47 .53 .58 .71 .81 .76 .79 .66 .60 .70 .83 .95 .98 .99 .95 1.01 .92 .92 .77 .30`. It
dips 0.10–0.11 at f .20 and .40–.45 (the sheet's fused crotch mass is a gap between sticks in ours).

**By eye, view by view:**
- **Front34 (hero):** right composition. Two broad-faceted lumps of the right size and place, A_up straight with a
  cream disc on top, B running down to its cut end, four vivid five-leaf clumps. It reads a little more as separate
  sticks than the sheet's one fused fork, because D and C show as their own sticks and there is background between
  A_up and D.
- **Straight A_up with its cut top:** straight now. The cut is 58.5° oblique to a 42.9° log, so the cream face
  measures 2.44 × 1.62 (log Ø 1.38) and runs 1.37 studs down the log. From the side, rear and rear34 the last third of
  A_up reads as a chisel or plank tip with a thin cream rim, where the sheet draws a round log with a disc.
- **Forked log X and cut ends:** the X reads from the top. All six ends carry a thick 10-sided insert with two faint
  ring bands and a bark lip (`cut_end.png` matches the "Cut End Detail" close-up). The junction close-up is fused,
  with no seam.
- **Resin lumps:** chunky, 8–10-corner outlines, yellow top to red-orange bottom, as on the sheet. The sheet's small
  tonal sub-facets and its pale highlight facets are missing (L6).
- **Leaf clumps:** broad pointed five-leaf stars, vivid, darker bases and lime tips. R-low under the small lump shows
  only as two or three thin leaves.
- **Bark lighter near the cut ends:** present and measured (above).
- **Underside:** no tan join pad shows; the sheet's "Flat Join Surface" close-up has one (L5).

### Colours (sheet / ours, front34 against f34; median, lit / shade quartile; Δ R, G, B)

| Region | Sheet | Ours | Δ |
| --- | --- | --- | --- |
| Bark | `#7B5036` (`#9F6946` / `#4D3321`) | `#81573B` (`#906142` / `#5B3B26`) | +6, +7, +5 (lit −15, −8, −4) |
| Bark near / far a cut end | `#89583A` / `#6F4B34` | `#82583D` / `#67452D` | −7, 0, +3 / −8, −6, −7 |
| Bark ground band (h 0–.2) | `#603F2B` | `#5F3F2A` | −1, 0, −1 |
| Resin, all | `#FD9406` (`#FEBC32` / `#DF6F02`) | `#FF9B0C` (`#FFB50F` / `#CF6A04`) | +2, +7, +6 |
| Large lump top / mid / bottom | `#FDB01C` / `#FD9F0C` / `#E57802` (39.5 / 36.6 / 31.2°) | `#FFB60F` / `#FF9E08` / `#D96F06` (41.8 / 36.4 / 29.9°) | +2, +6, −13 / +2, −1, −4 / −12, −9, +4 |
| Small lump top / mid / bottom | `#FD9F07` / `#FD9503` / `#DC7102` | `#FF9C12` / `#FF970E` / `#E97809` | +2, −3, +11 / +2, +2, +11 / +13, +7, +7 |
| Pale highlight facets (share of lump) | 5.3 % / 5.6 % | 0.0 % / 1.6 % | |
| Cut ends, all | `#F5CB94` | `#F7CD95` | +2, +2, +1 |
| Cut end, B front | `#F2C78F` | `#ECBE87` | −6, −9, −8 |
| Cut end, A top | `#FCD7A2` | `#FFE4A3` | +3, +13, +1 |
| Leaves | `#5A9B16` (`#89C728` / `#2D610C`) | `#5C9A18` (`#81CA20` / `#3B660E`) | +2, −1, +2 |
| Top view: bark / resin / cut / leaves | `#794E34` / `#FC9304` / `#F7D29E` / `#5B9A14` | `#81573C` / `#FFA10D` / `#FFE2A2` / `#5E9B19` | +8, +9, +8 / +3, +14, +9 / +8, +16, +4 / +3, +1, +5 |

Every front34 median is within 10 levels per channel. The rear views are 30–40 levels darker (the kit lights the rear
from behind; known, not paint).

### Itemised list

**Blockers:** none.

**Minors and leftovers** (for the main session; commit with these noted):
- **L1. A_up's chisel tip (the largest leftover; no cheap fix).**
  - The cut is 58.5° oblique, and the face is 2.44 × 1.62 on a Ø 1.38 log. From the side, rear and rear34 the top
    third of A_up reads as a wedge or plank with a thin cream rim, not as the sheet's round log with a disc. From the
    top the disc is about 3× the sheet's area, which puts the top view's C share at .138 against .089.
  - **Why it can't be cut less steeply:** A_up's axis (0.648, 0.342, 0.680) points 117° away from the front34
    camera. Any cut that shows the front34 the disc it needs (within about 60° of the camera) must be at least about
    57° oblique, and 58.5° is already that minimum.
  - A real fix moves A_up's aim forward (less +Y) so the log rises across the camera rather than away from it. That
    also moves D, the TR clump and the small lump, so it is a re-layout, not a tweak. Only worth doing if the main
    session judges the side and rear read unacceptable.
- **L2. A bark spike under the large lump in front34 (cheap).**
  - At about px (90–100, 290–345) of 480 × 400 there is a fang of bark below the large lump's lower left. Ray-cast:
    A_low's end lip at (−3.0, −1.3, 0.4–0.9). It is the acute side of the 45° `END_TURN["A_low"]`. The sheet shows a
    broad blunt log base there.
  - **Fix:** in `m019.py` set `END_TURN["A_low"]` from (−45, 0) to about (−15, 0), or shorten A_low's end
    (−2.70, −0.45) about 0.3 toward J. Check that the end stays tucked under the lump in front34 and that the hero guard
    still passes.
- **L3. "Several sticks".** D (and C under the TL clump) show as their own sticks, with background between A_up and D.
  So the front34 bark share is .430 against .487 (−5.7, tolerance ±4), and the top profile dips 0.10 at f .20 and .45.
  Round 2 tried thicker logs and the union broke, so leave it.
- **L4. The B front disc sits 0.069 H high in front34** (tolerance 0.06). Marginal.
- **L5. Join pads are hidden in the hero.** The sheet's "Flat Join Surface" close-up shows a tan block under the lump.
  The body part keeps both pads. This is a sheet conflict (the hero's lump hangs over A_low), so the main session
  should rule on it; nothing to fix.
- **L6. Resin pale highlight facets: 0–1.6 % against the sheet's 5–6 %.** They went with the spec drop (0.2 → 0.08)
  that fixed the washed small lump. Roblox applies its own specular, so leave it. Sub-facet tonal splits are still
  coarser than the sheet's (round-1 finding 9, optional).
- **L7. The R-low clump** under the small lump reads as two or three thin leaves rather than a star. Cosmetic.
- **Known misses, accepted per the study:** the rear's swapped lumps (§3.4); the side's narrow W : H (§3.5); the
  top's perspective (§3.6); the rear-view lighting; the B front disc not visible from the top.

## Main session after verification round 2 (2026-10-28)

Applied L2: `END_TURN["A_low"]` is (−15, 0), down from (−45, 0), so the bark spike under the large lump in front34 is gone. The rebuild in the kit file gave a hero of 2334 tris, 7.19 × 5.75 × 4.63, one shell, 0 non-manifold, `problems` empty, `K.check` clean. Export: 6 assets, 2 vfx sockets, 0 problems. L1 (the chisel-like A_up top from the side) needs a re-layout and is recorded as a minor.
