# 030 Mooncap — spec

Reference: `art/blender/assets/references/030.png`. The sheet's own title is "MOONCAP", subtitle "STYLIZED ENVIRONMENT
ASSET / INDIVIDUAL MODEL REFERENCE", footer "FLINTBORN — INDIVIDUAL MODEL STUDY", "PAGE 31/132" (INDEX.md row 30 calls it
"Mooncap Flintborn model study"; the page number on the sheet is not the index number). The image is 1024 × 1536 px.
Builder: `art/blender/kit/mcp/m030.py` → `build()` (not written yet). Procedure: `art/blender/kit/mcp/STAGES.md`
(one modeller does stages 1–6 in a background Blender, then a fresh verifier does stage 7).

User direction for every model: shapes must match the sheet; colours "need to match the master reference and blend
into the colors nearby. please ensure all color and textures are being made and applied." Effects ship wherever the
sheet shows them. **This sheet shows glowing cyan spot gems on the caps** ("bioluminescent"), but no halo, light spill
or particles (§7).

Sheet text:
- **Header:** "A cluster of bioluminescent cave mushrooms. Chunky, low-poly, hand-crafted geometry with broad
  flat-shaded faces. Simple, readable forms and solid colors. Designed for fantasy environment use in FLINTBORN."
- **Views:** Front Three-Quarter, Rear Three-Quarter, Front, Side, Rear, Top.
- **Exploded Construction:** labels Cap Shell, Spot Insert (with an illegible scribble under it), Stem (Large),
  Stem (Small), Base, Leaf Clump. It draws **three** mushrooms (the big cap over Stem (Large), a small mushroom at the
  right on Stem (Small), and an unlabelled second small mushroom at the left), one loose spot insert beside the big
  cap, one leaf clump, and the base (a dirt slab ringed by about ten boulders) with **two** stem holes (centre and
  right). Dashed arrows run from each stem down into the base (§3.5).
- **Close-up details:**
  - "Cap Underside": "Simple faceted underside. Consistent low-poly thickness." (a thick rim band and a shallow
    radial-faceted cone rising to the stem).
  - "Spot Junction": "Spot insert sits in shallow recess on cap. Clean join. No thin geometry." (an 8-sided gem with a
    flat table and a bevel ring, sunk in an 8-sided pocket with a dark purple wall).
  - "Base Junction": "Stems slot into base rocks. Flat joining surfaces. Keep forms chunky and simple."
- **Material palette:** Cap, Cap (Light), Spot, Stem, Rock (Dark), Rock (Light), Leaf (§5.1).
- **Modeling notes:** "Keep geometry low-poly, with broad, flat faces and clean silhouettes."; "Use separate, reusable
  parts: cap shell, spot inserts, stems, base rocks, leaf clump."; "Maintain consistent form and proportions across
  all views."; "Spots are separate meshes, not baked into the cap."; "Keep thickness on caps and clean, simple
  junctions."; "Optimize for readability at a distance."
- **Game context:** `src` has no Mooncap node or event (`EventCatalog.luau` has `Emberbloom`, `StarfallLotus` and the
  others; `NodeCatalog.luau` has only `CaveMushroomPatch` / `RedcapMushroomPatch` / `ChestnutMushroomPatch` as 2-stud
  balls). WorldModeling §11 groups it with the event flora: "Emberbloom / Frost Shrub / Mooncap / Ancient Root: Keep
  event inserts separate: … cap spots … Effects, if later requested, must not conceal the geometry during approval."
  §6.8 gives the mushroom recipe (ring-based cap with a real underside, tapered stalk with a load-bearing connection).
  The old **R08 kit sheet** has `Mooncap` (hero 10.06 × 7.46 × 8.12, 896 tris; `glyph_glow` × 2, `dust` spores,
  `harvest_hit`) and owns its names (§8). MODEL_PROGRESS row R08 marks it "partial — small flat caps, oversized spots;
  thin stem; no spot glow".

**Pixel boxes and masks.** All pixel boxes are sheet pixels `(x0, y0, x1, y1)`, origin top left. The paper is about
`#F1EBE4` (241, 235, 228); each view's paper is the median of its box's top and bottom 4 rows. The view boxes start
below the cell labels, so no blanking is needed. The masks are `cls()` in `m.py` (HSV; background = within 18 of the
paper). **The ground shadow is background**: it is pale and grey (sat ≤ 0.08, v ≥ 0.8), lands in `O` and is never
counted in a share or a bbox.
- **P, cap (purple):** hue 225–300°, sat ≥ 0.20 (both caps, top, flanks and underside).
- **C, spot (cyan glow):** hue 165–225°, sat ≥ 0.20, v ≥ 0.45.
- **G, leaf:** hue 55–130°, sat ≥ 0.35.
- **T, stem (cream):** hue 27–55°, sat 0.12–0.50, v ≥ 0.45, not G. (The hue cut at 27° separates the stems, 31–35°
  even in shade, from the rocks, 12–24°.)
- **R, rock and dirt:** anything else that is not background with v < 0.72.
- **O, other:** the ground shadow and anti-alias fringe; not counted.
- Use the same scripts on both images. Render the `*_sheet` cameras with the studio floor hidden (M027 lesson: a grey
  shadow can fall into R).

**Scratch study material** (no Blender), in
`<temp>\3f83a1be-3b3d-4e4b-ae5a-7b04dbb75bdc\scratchpad\m030_study\`.
Run with the scratch venv `...\scratchpad\venv22\Scripts\python.exe` (Pillow + numpy).
- **Helpers:** `m.py` (masks, view boxes `V`, `cls`, `stats`, `preview`), `lab.py` (connected components), `bb.json`
  (silhouette boxes), `crops.py`, `zoom.py`, `probe.py`.
- **Measurements:** `measure.py` → `measure_out.txt` (bboxes, shares, top and bottom profiles, width per height, region
  extents, shares per 0.1 h); `comps.py` → `comps_out.txt` (caps, stems, leaf clumps and spots per view);
  `runs.py` → `runs_out.txt` (class runs per height); `capprof.py` → `capprof_out.txt` (each cap's top/bottom per
  column, width per cap height); `stems.py` → `stems_out.txt` (stem widths in studs per z); `outline.py` →
  `outline_out.txt` (cap outline corner points); `expl.py` / `partprof.py` → `expl_out.txt` / `partprof_out.txt`
  (exploded parts, width profiles).
- **Colour:** `sw.py` → `sw_out.txt` (swatches), `samp.py` → `samp_out.txt` (views, parts, close-ups), `grad.py` →
  `grad_out.txt` (cap bottom → top, stem top → bottom, leaf base → tip, spot deep/mid/light split).
- **Crops:** `f34.png`, `r34.png`, `front.png`, `side.png`, `rear.png`, `top.png`, `expl.png`, `cu.png`, `pal.png`,
  `notes.png`; mask previews `cls_*.png` (magenta = O).
- **Zooms:** `z_f34_bigcap.png`, `z_f34_small.png`, `z_front_small.png`, `z_side_small.png`, `z_rear_small.png`,
  `z_r34_small.png` (who hides whom, §3.2), `z_cu_under.png`, `z_cu_spot.png`, `z_insert.png`, `z_f34_topspot.png`,
  `z_leaf.png`, `z_expl_base.png`, `z_expl_left.png`.
- **To run the scripts on our renders,** set `M030_IMG=<render.png>` and `M030_BOXES='{"front":[x0,y0,x1,y1],…}'`
  and re-run `measure.py` (it rewrites `bb.json`), then the others. For the top, flip our render left-right first
  (§3.3).

## 1. Study (2a)

### 1.1 Classification, what it is, size

- **Classification:** full asset (a rare/event resource node). Hero budget 4000 tris, each part under 1000. The plan in
  §4.4 lands at about 2600–3300 after the unions.
- **Overall read (check this first).** Two chunky violet toadstools on fat cream pear-shaped stems, standing in a low
  ring of brown-grey boulders, their caps studded with glowing cyan gems. Wider than tall (front W : H 1.29):
  - **a big mushroom** at the back-left: a broad, thick, faceted dome cap (Ø about 5.8) with a flat-topped crown and a
    thick rim band, **its crown over the stem and its rim drooping to the left (−X)**: the cap overhangs further on
    the −X side, whose rim is about 1.9 lower than the +X rim. It stands on a pear-shaped stem (Ø 2.4 at its widest
    low down, 1.5 under the cap) and makes the whole top half of every elevation view;
  - **a small mushroom** at the front-right (cap Ø about 2.8, more domed, **drooping the other way, to the right
    (+X)**), its cap tucked under the big cap's right rim, on a short stem (Ø 1.45 → 0.95);
  - **eleven 8-sided cyan gem spots** set in shallow pockets: six on the big cap (one big Ø 1.4 near the crown), five
    on the small one. They glow: 90–95 % of their pixels are at v ≥ 0.85 in every elevation view, shade side included;
  - **a ring of about ten domed boulders** on a dark dirt slab, hugging both stem feet; the boulders make the bottom
    15–20 % of every elevation view;
  - **two bright yellow-green leaf clumps** (4–5 pointed faceted leaves each) between the boulders at the back, one
    each side of the big stem.
  - Hero shares (front): cap 49 %, spots 7 %, stems 20.5 %, leaves 2 %, rock 21.5 %.
- **Focal silhouettes, in order:**
  1. The big cap: a wide, low, flat-topped polygonal dome, left rim low (h .45), right rim high (h .80), the top flat
     across 0.26 of its width.
  2. The small cap stepping down to the right under the big rim (top h .64, right rim h .27).
  3. The two cream stems, the big one bulging low; the rock band under everything.
- **Target size: about 7.1 W × 5.5 D × 5.5 H studs** (H = 1.0 C of the 5.5-stud character: the big cap's crown at the
  character's head, its rim from hip to shoulder, the small cap at chest height, the boulders knee high).
  Tolerances W ±0.35, D ±0.4, H ±0.25. Decision §8.1.
  - **How it was derived.** The sheet has no character. Mooncap is grouped with Emberbloom in WorldModeling §11 (event
    flora); M025 Emberbloom was decided at 1.0 C (5.5 H), so the family reads at one scale. The front cell (235 × 182
    px) then gives **33.1 px per stud**; the f34 **56.4**, the side **33.5**, the rear **33.6**, the r34 **56.2**, the
    exploded about **50.5** (Stem (Large) 176 px ≙ 3.48 tall) and the exploded base about **64** (392 px ≙ 6.1).
  - **Width:** front W : H 1.291 → 7.10.
  - **Depth:** side D : H 1.005 → 5.52 (§3.1 and §3.4 for why the side cell is the weakest view).
  - **Alternatives:** 1.3 C (× 1.31 → 9.3 × 7.3 × 7.2, close to R08's 10.1 × 7.5 × 8.1; the player could almost walk
    under the big rim), or 0.8 C (5.7 × 4.5 × 4.4).
  - Resulting part sizes: big cap 5.8 × 4.65 (§3.4) × 2.4 thick; small cap 2.8 × 2.25 × 1.45; big stem Ø 2.4 max ×
    3.6; small stem Ø 1.45 max × 2.4; gems Ø 0.3–1.4; boulders Ø 1.2–1.75 × 0.9–1.25; leaf clumps 1.4–1.6 W ×
    1.9–2.3 H; dirt slab 5.0 × 3.8 × 0.3.
- **Build frame:** front −Y, +X right, ground z 0, origin = the base ring's centre on the ground. Stage 2 re-centres
  to the bbox bottom centre (the bbox centre is within 0.1 of the ring centre).
- **Stud mappings used below** (H = 5.5):
  - front cell: X = (f − 0.50) × 7.1, z = h × 5.5 (camera about 8° up);
  - rear cell: X = (0.50 − f) × 6.85 (screen right = −X; the rear is drawn 4 % narrower);
  - side cell: **Y = (0.50 − f) × 5.52, screen right = −Y (the front)**: the sheet's side camera stands at **−X**, not
    at the kit side camera's +X (§3.2);
  - top cell: **mirrored left-right** (image right = −X, image top = back; §3.3); counts and shares only.

### 1.2 Measured views (`measure.py`, `comps.py`, `samp.py`)

| View (box) | Silhouette bbox (px) | W : H | Cap P | Spot C | Stem T | Leaf G | Rock R | C / (P + C) | Spot px at v ≥ 0.85 |
| --- | --- | --- | --- | --- | --- | --- | --- | --- | --- |
| Front three-quarter (16,114,510,450) | 71–495 × 122–431 (425 × 310) | 1.371 | 49.3 % | 8.2 % | 18.7 % | 2.4 % | 21.3 % | 14.3 % | 91 % |
| Rear three-quarter (516,114,1010,450) | 576–955 × 121–429 (380 × 309) | 1.230 | 48.1 % | 3.8 % | 16.1 % | 7.5 % | 24.4 % | 7.4 % | 95 % |
| Front (16,486,266,710) | 31–265 × 509–690 (235 × 182) | 1.291 | 49.1 % | 6.8 % | 20.5 % | 2.2 % | 21.5 % | 12.1 % | 90 % |
| Side (271,486,510,710) | 306–490 × 507–690 (185 × 184) | 1.005 (D : H) | 46.8 % | 2.5 % | 25.4 % | 1.8 % | 23.6 % | 5.0 % | 93 % |
| Rear (515,486,760,710) | 524–753 × 505–689 (230 × 185) | 1.243 | 46.4 % | 3.7 % | 16.9 % | 8.3 % | 24.8 % | 7.4 % | 94 % |
| Top (765,486,1010,710) | 797–991 × 492–689 (195 × 198) | 0.985 (W : D) | 72.2 % | 13.8 % | 0.5 % | 1.5 % | 11.9 % | 16.0 % | 81 % |

- **Reading:** about half of every elevation view is violet cap, a fifth cream stem, a fifth to a quarter rock. The
  glow share is highest from the front (the big crown gem and two front-left gems face it: C 6.8–8.2 %) and lowest
  from the side (2.5 %). The rear shows the leaves most (8.3 %); the front and side hardly at all (2 %).
- **Verifier tolerance:** shares ±4 points (top ±6); **spot share C ±2 points (top ±4)** and C / (P + C) ±3; spot
  bright share (v ≥ 0.85) ≥ 85 % in elevation views (top ≥ 75 %); profile values ±0.06 h; positions ±0.06 of W/H
  unless stated.

**Visible shapes per view** (`comps.py`, `capprof.py`; extents as fractions of the view's silhouette; W : H of the
visible shape in px):

| View | Big cap: f, h, W : H | Small cap: f, h, W : H | Big stem: h visible, max Ø | Small stem: h visible, max Ø | Leaf clumps |
| --- | --- | --- | --- | --- | --- |
| Front | .00–.82, .39–1.00, 1.75 | .60–1.00, .27–.64, 1.37 | .02–.58, 2.40 at z 1.6 | .03–.38, 1.45 at z 0.8–1.2 | f .13–.31 h .21–.38 (L2); a sliver f .65–.68 (L1) |
| F34 | .00–.80, .39–1.00, 1.78 | .57–1.00, .27–.65, 1.54 | .01–.55, 2.46 at z 1.6 | .00–.37, 1.48 at z 1.2 | f .11–.31 h .21–.38; f .62–.66 |
| Side | .00–.77, .45–1.00, 1.42 | .61–.99, .27–.61, 1.14 | .14–.66, 2.16 at z 1.6 | .20–.40 (mostly hidden) | f .14–.29 h .18–.34 (one) |
| Rear | merged with the small cap: .00–1.00, .34–1.00 | (merged) | .00–.62, 2.18–2.36 | .02–.45 behind L1 | f .18–.40 h .18–.48 (L1, 1693 px); f .71–.90 h .17–.39 (L2) |
| R34 | .18–1.00, .42–1.00, 1.73 | .00–.41, .27–.60, 1.52 | .00–.61, 2.39 | .03–.39 behind L1 | f .14–.36 h .16–.43; f .70–.91 h .18–.39 |
| Top | one merged violet mass, big upper right, small lower left | | | | one clump, upper left at the big cap's rim |

- **Cap visible height** (front): the big cap occupies h .39–1.00 (z 2.15–5.5), the small cap h .27–.64 (z 1.5–3.5).
  The big cap's bottom per 0.1 of its width (front): `.45 .39 .41 .44 .49 .52 .57 .56 .61 .67 .79`, top
  `.48 .72 .82 .90 .95 .99 .99 1.00 .98 .93 .81`: **the left rim is the lowest point (h .39–.45), the right rim the
  highest (h .79–.81)**: the rim drops about 1.9 studs across the cap toward −X. **But the crown is not moved
  left:** the flat crown sits at 0.50–0.80 of the cap width (f .38–.60, X −0.8 … +0.7, centre about 0.0, over the
  stem at X −0.2), so the left flank is long (3 facets, rising 3.0 over 2.7) and the right flank short and steep
  (2 facets, 1.05 over 1.6). A rigidly tilted symmetric cap would carry its crown to the −X side with the rim; the
  sheet's cap is **eccentric and drooping** instead (§1.4). The rear and r34 agree (crown at rear f .45–.55, X 0 ±
  0.3, over the stem; the −X rim at screen right lowest). The small cap's bottom `.48 .41 .38 .39 .37 .35 .32 .29 .27
  .27 .29`: its right (+X) rim is lowest, its flat crown (h .61–.64) at f .65–.85, over its stem (f .755).
- **Cap outline corners** (`outline.py`, Douglas–Peucker on the upper outline, rim to rim): big cap 7 segments in the
  front, 8 in the f34, 10 in the r34, with a **flat top segment spanning 0.47–0.73 of the cap width**; small cap 7–8
  segments. Faceted polygons, not round domes.

**Top profiles** (highest silhouette pixel per column as a fraction of H, every 0.05 f):

| f | .00 | .05 | .10 | .15 | .20 | .25 | .30 | .35 | .40 | .45 | .50 | .55 | .60 | .65 | .70 | .75 | .80 | .85 | .90 | .95 | 1.0 |
| --- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- |
| f34 | .47 | .68 | .76 | .83 | .88 | .91 | .94 | .97 | .99 | 1.0 | 1.0 | 1.0 | .99 | .97 | .95 | .88 | .80 | .64 | .60 | .53 | .38 |
| Front | .48 | .67 | .74 | .80 | .86 | .90 | .93 | .97 | .99 | .99 | .99 | 1.0 | 1.0 | .98 | .96 | .92 | .86 | .64 | .60 | .55 | .45 |
| Side | .61 | .74 | .80 | .87 | .90 | .94 | .97 | .99 | 1.0 | 1.0 | 1.0 | .99 | .99 | .96 | .94 | .90 | .61 | .60 | .56 | .50 | .38 |
| Rear | .45 | .57 | .62 | .67 | .80 | .87 | .92 | .95 | .97 | .99 | 1.0 | .99 | .99 | .98 | .96 | .93 | .89 | .85 | .79 | .73 | .55 |
| r34 | .36 | .49 | .55 | .59 | .80 | .88 | .92 | .95 | .97 | 1.0 | 1.0 | 1.0 | 1.0 | .98 | .96 | .94 | .89 | .85 | .79 | .71 | .53 |
| Top (mirrored) | .37 | .72 | .78 | .88 | .93 | .94 | .96 | .99 | 1.0 | .99 | .96 | .95 | .94 | .91 | .88 | .88 | .87 | .84 | .75 | .66 | .52 |

- **The step.** In the front, f34 and side the big dome runs from f 0 to about .80, then the profile drops 0.20–0.30 h
  to the small cap's top (front .86 → .64 between f .80 and .85). In the rear and r34 the step is at f .15–.20 (screen
  left = +X), smaller (.67 → .80) because the small cap is nearer the camera there.

**Width per height** (silhouette width / W at h = 0.0, 0.1 … 1.0; start f after the @):

```
f34    .12@.60 .86@.10 .87@.06 .87@.12 .93@.06 .96@.01 .88@.03 .69@.06 .68@.12 .51@.23 .13@.45
front  .13@.58 .86@.11 .83@.09 .86@.14 .94@.06 .97@.01 .87@.03 .71@.07 .68@.15 .52@.24 .18@.43
side   .30@.30 .86@.07 .79@.10 .75@.23 .69@.30 .94@.01 .86@.01 .68@.03 .68@.09 .56@.19 .22@.35
rear   .23@.39 .90@.06 .87@.08 .74@.16 .71@.00 .98@.02 .92@.07 .74@.21 .70@.20 .52@.27 .14@.45
r34    .18@.40 .93@.03 .89@.06 .90@.01 .69@.01 .94@.06 .82@.16 .75@.20 .69@.20 .52@.28 .16@.45
```

So: the rock band 0.83–0.90 W at h .1–.2; the stems and rocks (and in the front the small cap's rim) at h .3; the
silhouette widest at h .4–.5 (0.94–0.98 W: both caps' rims); the big cap alone above h .65 (0.68–0.74 W at h .7, 0.52
at h .9, a flat crown 0.13–0.22 wide at the very top).

**Height bands** (share of P / C / T / G / R per 0.1 h, front; f34 and rear follow within ±10):

```
h  .0-.1  R99            .1-.2  T20 R80           .2-.3  P4 T63 G10 R22     .3-.4  P29 T55 G9 R6    .4-.5  P64 C3 T32
h  .5-.6  P78 C9 T11     .6-.7  P90 C10           .7-.8  P87 C13            .8-.9  P78 C22          .9-1.0 P76 C24
rear h .2-.3  T30 G39 R31   .3-.4  P10 T55 G33     (the leaves show most from behind)
```

**Bottom profiles** (lowest pixel per column above the bbox bottom, fraction of H): front .08 at f .10, .02 at .40–.55,
0 at .65, .08 at .95; the ring's front curve gives an elevation of about 6–10° for the front, side and rear. The f34 is
the front composition seen about 6° higher (§3.1).

**Stems** (`stems.py`; width in studs at height z, centre f):

```
front big    z0.8 1.76  z1.2 2.25  z1.6 2.40  z2.0 2.34  z2.4 2.10  z2.8 1.52(shade)   centre f .47-.48  (rocks hide z < 0.8)
f34   big    z1.2 2.31  z1.6 2.46  z2.0 2.37  z2.4 2.10
rear  big    z2.0 2.18  z2.4 2.09  z2.8 1.85  z3.2 1.26                               centre f .55-.57
side  big    z1.6 2.16  z2.0 2.10  z2.4 1.98  z2.8 1.80  z3.2 1.56                     centre f .46-.48
front small  z0.8 1.55  z1.2 1.37  z1.6 1.28  z2.0 0.85(under the cap)                centre f .74-.76
f34   small  z0.8 1.73  z1.2 1.48  z1.6 1.37
```

- **Big stem:** a fat pear, widest (Ø 2.4) at z 1.4–1.8, Ø 2.1 at z 2.4, 1.8 at z 2.8, about 1.5 where it enters the
  cap (z 3.1–3.4). Its foot is hidden by boulders below z 0.8.
- **Small stem:** widest (Ø 1.45–1.5) low, at z 0.8–1.2, 1.3 at z 1.6, about 0.95 under its cap (z 2.0–2.1).
- **Positions:** big stem X −0.21 (front) / −0.41 (rear), Y +0.11 (side); small stem X +1.81 (front) / +1.9 (rear),
  Y −1.35 (side). Centre to centre about 2.5 studs, the small one front-right of the big.

### 1.3 Silhouette and composition per view

**Front (`front.png`; governs the X layout and the heights).** Camera on the front axis, about 8° up.
- **Big cap:** f .00–.82. A wide faceted dome: rim tip at the far left (f 0, h .45), the left flank rising in 3
  facets to the flat crown (f .38–.60, h .99–1.0), the right flank falling in 2 facets to the right rim (f .82, h
  .80). The thick rim band shows as a darker strip along the lower-left edge; the underside shows as a dark violet band
  under the front rim (h .45–.57) above the stem. Gems: S1 big near the crown right (f .60, h .90, 46 × 23 px),
  S2 upper left (f .18, h .77, 35 × 31), S3 below it (f .25, h .68, 22 × 22), S4 on the far left flank (f .05, h
  .55, 6 × 12).
- **Small cap:** f .60–1.00, h .27–.64; its left edge tucks under the big cap's right rim and **its rim passes in front
  of the big stem's right side** (it is nearer the camera, §3.2). Gems: s1 near its top left (f .71, h .59, 19 × 9),
  s2 upper right (f .90, h .52, 20 × 20), s3 front (f .77, h .49, 11 × 9), s4 right flank (f .98, h .39).
- **Stems:** big f .32–.64 visible from the rocks (h .14) to the cap (h .58); small f .65–.84, h .14–.38. A narrow
  green leaf tip shows between the stems (f .65–.68, h .29–.37) and a leaf clump to the left of the big stem
  (f .13–.31, h .21–.38).
- **Rocks:** a continuous band f .08–.95 at h .0–.2, 6–7 boulders across the front, tops at h .18–.26 (z 1.0–1.4).

**Front three-quarter (`f34.png`; the hero).** The front composition seen about 6° higher and drawn 6 % wider (W : H
1.37). Every gem, cap edge and stem sits at the front cell's fractions within ±0.03 (spots f34 (.59,.87), (.18,.76),
(.26,.64), (.05,.54) against the front's (.60,.90), (.18,.77), (.25,.68), (.05,.55)). About 9 boulders and 2 pebbles
show; the left leaf clump (two bits, f .11–.31) sits behind the front-left boulders.

**Side (`side.png`; the camera is at −X: screen right = −Y, the front).** D : H 1.005.
- **Big cap** f .00–.77 (4.27 studs across, 0.73 of its front width, §3.4), the screen-left (back) rim low (h .47–.51)
  and the screen-right edge higher (h .66–.78). Two gems on its upper surface (f .18 h .87; f .61 h .95), one on the
  left flank.
- **Small cap** f .61–.99, h .27–.61, **behind the big stem** (the big stem's right edge cuts across the small cap's
  left edge, `z_side_small.png`), so the small mushroom is on the far side from this camera. Its right (front) rim is
  the lowest.
- **Big stem** f .28–.66 (Y +1.2 … −0.9), visible up to h .66; the small stem shows only between the big stem and the
  small cap (f .66–.83, h .20–.40). One leaf clump at the far left (f .14–.29, h .18–.34: L2 at the back-left,
  nearest this camera). Rocks f .07–.93 at h .1.

**Rear (`rear.png`; screen right = −X).** The big mushroom at screen right (f .40–.72 stem), the small one at screen
left (stem f .15–.30). **The big stem hides the small cap's right edge** (`z_rear_small.png`), so from behind the small
mushroom is the farther one: it stands in front (−Y). L1, a big bright clump of 4–5 leaves, stands in front of the
small stem (f .18–.40, h .18–.48); L2 at screen right of the big stem (f .71–.90, h .17–.39). Gems: the big crown gem
seen from behind (f .34, h .91), a big one on the back-left flank (f .79, h .81, 38 × 32), three small on the small
cap's back (f .08–.25, h .53–.64). Rocks f .06–.95, the centre-back boulder the biggest.

**Rear three-quarter (`r34.png`).** The rear composition from a little higher (the same gems at the same fractions
within ±0.05). The small cap reads big at screen left (f .00–.41) because its far side is open; leaves L1 (f .14–.36)
and L2 (f .70–.91).

**Top (`top.png`; mirrored, §3.3).** One violet mass: the big cap upper right (image), the small cap lower left,
overlapping (the big cap on top). Boulders show at the upper left and lower right outside the caps, one leaf clump at
the big cap's upper-left rim. Gems: big cap 3–4 (the big crown gem Ø 49 × 52 px, one upper left 33 × 32, one on the
right edge 18 × 25), small cap 3 (its top gem 36 × 40, two small on its edges). The caps are seen nearly end-on as
faceted 14- and 12-gons.

### 1.4 Parts (Exploded Construction (16,760,655,1300), close-ups (662,718,1012,1300))

Facet language for every part: broad flat-shaded facets, chunky, crisp edges, no noise, no bevels; facet rings offset
by half a step so the cap and gem faces read as **triangles and kites**, not vertical strips.

#### Cap Shell — exploded (172,760,467,928) 296 × 169 px; close-up "Cap Underside" (676,760,1000,920)

- **Shape:** a thick, broad, flat-crowned dome (the big cap). Upper outline (exploded, rim to rim) widens fast from the
  rim (width / H per 0.1 of the height from the top: `.53 .99 1.23 1.43 1.54 1.53 1.47 1.29 1.06 .76 .20`): a flat top
  polygon about 0.3 of the diameter, two shoulder rings, a **vertical rim band** about 0.15 of the cap's height, and
  an underside.
- **Underside (close-up):** a shallow faceted cone, 14–16 radial facets plus one inner ring, rising from the rim band's
  lower edge to the stem (about 0.2 of the cap height), dark violet (`#4D3B72`); the rim band reads as a lighter
  violet strip all round. "Consistent low-poly thickness": the cap is a solid with real thickness, never an open bowl.
- **Pockets:** each gem sits in an **8-sided pocket** with a vertical wall about 0.07 of the gem's width and a floor
  about 0.10 × the gem width below the cap surface (`z_cu_spot.png`).
- **Construction:** `_cap(rx, ry, hc, n, seed)`, a lathe of rings (radius fraction ρ, height fraction of hc), each ring
  rotated half a step from the one below, ±4 % radius / ±3 % height jitter per vertex:
  - underside: (0.30, 0.20) stem ring, (0.68, 0.07);
  - rim band: (1.00, 0.00) rim bottom, (1.00, 0.15) rim top;
  - dome: (0.92, 0.42) shoulder, (0.70, 0.74) upper shoulder, (0.34, 0.96) crown ring, apex (0, 1.0) offset 0.05 ρ;
  - big cap: n 14, rx 2.9, ry 2.33, hc 2.35; small cap: n 12, rx 1.4, ry 1.12, hc 1.45, the dome rings raised
    (0.92, 0.48), (0.70, 0.80) so it reads more domed (the small caps' visible W : H is 1.37–1.54 against the big
    cap's 1.73–1.78);
  - **droop and eccentricity** (the hero caps, §1.2): after the lathe, move every dome vertex by its ring's height
    fraction u (rim 0 → apex 1): x += e × u (the crown shifts toward the stem) and z += s × (x₀ − x_c) × (1 − u)
    (the rim slopes, the crown stays level), where x₀ is the vertex's lathe x and x_c the rim centre. Big cap e +0.65,
    s +0.33 (the −X rim 0.95 lower, the +X rim 0.95 higher than the centre); small cap e −0.30, s −0.35. The underside
    rings follow the rim (weight 1) except the stem ring, which is centred on the stem top. The exported
    `MooncapShell` stays undrooped (e 0, s 0);
  - the underside's stem ring is the join face (the stem overlaps it by 0.15); **about 180 tris** (big) / 150 (small)
    before pockets.

#### Spot Insert — exploded (501,818,566,878) 66 × 61 px; close-up "Spot Junction" (850,960,1000,1135)

- **Shape:** a faceted gem: an **8-sided girdle**, a flat 8-sided **table** (Ø 0.62 of the girdle) raised 0.22 × the
  girdle Ø above it with an 8-facet crown bevel between, and an 8-facet pavilion cone below (depth 0.45 × Ø) that is
  hidden in the cap. The loose insert reads as a rounded nugget (W : H 1.08) because its pavilion shows.
- **Placement:** the girdle sits at the pocket floor; the table stands 0.08–0.12 × Ø proud of the cap surface; a ring
  of pocket floor 0.08 × Ø wide shows round it (the dark wall in the close-up).
- **Sizes in the hero** (§2.3): Ø 1.40 (crown gem), 1.15, 1.10, 0.85, 0.75, 0.70, 0.62, 0.50, 0.45, 0.40, 0.30.
- **Construction:** `_gem(d, seed)`: table 8 + crown 16 + pavilion 8 = **32 tris**; ±3 % jitter; the table faces get
  `spot_light`, the crown bevels `spot`, the lowest crown row and the pavilion `spot_deep` (§5.4).

#### Stem (Large) — exploded (269,947,393,1122) 125 × 176 px; Stem (Small) — exploded (408,995,489,1114) 82 × 120 px

- **Shape:** a fat faceted **pear**: narrow flat top, widening downward to a bulb, rounded to a smaller flat foot.
  Width / max width, top → bottom per 0.1 of the length (Large): `.59 .66 .73 .81 .94 1.00 .94 .84 .59 (.11 foot)`;
  (Small): `.58 .64 .69 .79 .88 .97 1.00 .97 .81 (.33)`. W : H 0.71 (Large), 0.68 (Small). 8–10 sides, 5–6 rings,
  no smoothing. A small dark dot on the Large stem's top is the peg notation (§3.6).
- **Hero profiles** (the hero governs; z from the ground, Ø):
  - big: (0.0, 1.85), (0.5, 2.20), (1.1, 2.38), (1.6, 2.42), (2.2, 2.25), (2.7, 1.90), (3.1, 1.60), (3.6, 1.48)
    inside the cap; 10 sides;
  - small: (0.0, 1.20), (0.45, 1.45), (0.9, 1.47), (1.4, 1.30), (1.8, 1.08), (2.15, 0.95), (2.45, 0.92) inside the
    cap; 8 sides.
- **Construction:** `_stem(rings, n, seed)`, rings rotated half a step, ±4 % jitter, flat caps both ends. **About 140
  tris** (big), 96 (small).

#### Leaf Clump — exploded (94,1121,184,1201) 91 × 81 px

- **Shape:** 4–5 thick faceted **lance leaves** from one root point: one upright centre leaf, two splayed 35–50° to the
  sides, one or two behind. Each leaf is an elongated kite: widest at 0.55–0.60 of its length, **W : L 0.36–0.40**,
  a sharp tip (plan angle 40–50°), a narrow base (0.15 L), a raised midrib ridge on top (the two halves are two flat
  planes meeting at about 150°), thickness about 0.10 L. No serration.
- **Size:** clump 1.4–1.6 W × 1.9–2.3 H in the hero (L1 the bigger, §2.4); leaves L 1.3–2.2.
- **Construction:** `_leaf(L, W, T, seed)`: outline 6 points (base, two per side at 0.30 / 0.58 L with half-widths
  0.30 / 0.50 × W, tip), a midrib ridge raised T × 0.6 at 0.45 L, a keel lowered T × 0.4; **about 16 tris**; ±5 %
  jitter; no two leaves identical. Not `K.leaf` (shallow card) and not `NS["leaf"]` (serrated).

#### Base — exploded (158,1151,549,1288) 392 × 138 px; close-up "Base Junction" (850,1150,1000,1295)

- **Shape:** a low **dirt slab** (oval, about 5.0 × 3.8 × 0.3, irregular faceted outline, a slightly raised faceted
  top, dark brown) carrying **about ten domed boulders** round its rim — big ones at the front-centre, front-left, back
  and right, smaller ones between — plus 1–3 pebbles. Boulders are peaky domes: height 0.70–0.75 of width, 6–8-sided
  footprints, 2 rings plus an off-centre top vertex, 10–14 visible facets, flat bottoms (WorldModeling §12.1).
- **Base Junction close-up:** the stem's foot stands in a ring of boulders that touch it ("stems slot into base
  rocks"); the stem holes in the exploded slab are notation (§3.6).
- **Construction:** `_slab(rx, ry, h, n=14, seed)` + `_boulder(d, h, seed)` × 10 + `_pebble(d)` × 3 (or
  `K.hull_rock(..., keep_bottom=True)` with 3 rings of 6–7). Part size about **6.1 × 4.8 × 1.25**.

#### The exploded's left mushroom

- An unlabelled second small mushroom (cap 157 × 102 px, stem 85 × 107 px, the same shape as the right one). The
  assembled views show only two mushrooms and the base has two stem holes. **Not built** (decision §8.2).

## 2. Layout (starting values; tune on the renders)

Studs, build frame (front −Y, +X right, ground z 0, origin = the base ring's centre). Azimuths φ are measured from +X
counter-clockwise (front = 270°, back = 90°). Cap-local spot positions use ρ (0 at the apex, 1 at the rim) and φ in the
cap's own lathe frame, before the droop.

### 2.1 Mushrooms

| Piece | Position | Size | Droop (§1.4) | Sheet evidence |
| --- | --- | --- | --- | --- |
| Big stem | vertical, foot (−0.20, +0.35, 0) → top 0.15 inside the cap's underside stem ring (z ≈ 3.85) | §1.4 big profile, 10 sides | – | front centre f .47–.48 at every z, Ø 2.40 at z 1.6; side Y +0.1; rear X −0.4 |
| Big cap | rim centre (−0.65, +0.50), rim-bottom z 3.10 at the centre | rx 2.9 (X) × ry 2.33 (Y), hc 2.4, 14 sides | **e +0.65 (crown at X 0.0, over the stem), s +0.33 (−X rim 2.15, +X rim 4.05)** | front f .00–.82, crown f .38–.60 h 1.0, left rim h .39–.45, right rim h .79–.81 |
| Small stem | vertical, foot (+1.85, −1.35, 0) → top 0.15 inside its cap (z ≈ 2.45) | §1.4 small profile, 8 sides | – | front f .74–.76, Ø 1.45 low; side Y −1.35 |
| Small cap | rim centre (+2.13, −1.55), rim-bottom z 2.05 at the centre | rx 1.4 × ry 1.12, hc 1.45, 12 sides | **e −0.30 (crown at X +1.83, over the stem), s −0.35 (+X rim 1.56, −X rim 2.54)** | front f .60–1.00, crown f .65–.85 h .61–.64, right rim h .27–.29 |

- **Expected heights:** big apex 5.5; big rim from 2.15 (−X) to 4.05 + the band 0.36 = 4.41 (+X); the front rim at the
  stem's column about 3.25 (sheet: the cap's bottom at f .50 is h .56–.58, z 3.1–3.2); small top 3.5; small rim from
  1.56 (+X) to 2.54 + 0.22 band (−X, under the big rim; let the two caps touch with a clean overlap ≥ 0.05, never a
  sliver gap).
- **Expected X:** big cap −3.55 … +2.25; small cap +0.73 … +3.53; hero **−3.55 … +3.53 (7.08)**. Front stems at f .47
  and .76; the big crown's flat top across f .40–.60.
- **Expected Y:** big cap −1.83 … +2.83; small cap −2.67 … −0.43; hero **−2.67 … +2.83 (5.50)**.
- **Stem joins:** each stem's top ring sits 0.15 inside its cap's underside stem ring; the underside's stem ring is
  Ø 1.74 (big, 0.30 × 5.8) against the stem's Ø 1.5–1.6 there, so a narrow underside ledge shows round the stem as
  in the close-up.

### 2.2 Leaves and base

| Piece | Root / centre (x, y) | Size | Sheet evidence |
| --- | --- | --- | --- |
| L1 leaf clump (back right) | (+1.60, +1.45), root z 0.25 | 5 leaves, L 1.5–2.2, tips to z 2.5–2.6, splay ±45°, clump 1.6 W | rear f .18–.40 h .18–.48 (X +0.7 … +2.2, z 1.0–2.64); front sliver f .65–.68; top: peeks out at the big cap's rim |
| L2 leaf clump (back left) | (−2.10, +1.35), root z 0.25 | 4–5 leaves, L 1.3–1.8, tips to z 2.0–2.1, clump 1.4 W | rear f .71–.90 h .17–.39; front f .13–.31 h .21–.38; side f .14–.29 |
| Dirt slab | (+0.15, 0) | oval 14-gon 5.0 × 3.8, z 0 → 0.30, top ring raised 0.05 | exploded base; hidden in the hero except between boulders |

**Boulders** (centre (x, y), footprint Ø × height; flat bottoms at z 0):

| # | Centre | Ø × h | Note |
| --- | --- | --- | --- |
| B1 | (−2.05, −1.00) | 1.6 × 1.15 | front left, big |
| B2 | (−0.95, −1.65) | 1.35 × 1.00 | front centre-left |
| B3 | (+0.35, −1.75) | 1.6 × 1.15 | front centre, against the big stem's front right |
| B4 | (+1.55, −1.95) | 1.25 × 0.90 | in front of the small stem |
| B5 | (+2.50, −1.35) | 1.3 × 0.95 | front right |
| B6 | (+2.45, +0.25) | 1.4 × 1.05 | right |
| B7 | (+2.35, +1.15) | 1.2 × 0.90 | back right, beside L1 |
| B8 | (+0.20, +1.55) | 1.75 × 1.25 | back centre (the rear's biggest) |
| B9 | (−1.40, +1.50) | 1.3 × 0.95 | back left, beside L2 |
| B10 | (−2.25, +0.50) | 1.45 × 1.10 | left (the f34's dark back-left rock) |

- **Pebbles:** Pa Ø 0.6 × 0.4 at (−1.0, −2.35), Pb Ø 0.5 × 0.35 at (+0.95, −2.4), Pc Ø 0.55 × 0.4 at (+2.85, −0.55).
- Boulders overlap the slab by 0.2–0.4, each other by 0.1–0.2 and **touch both stem feet** (Base Junction). Expected
  ring: X −2.95 … +3.15, Y −2.6 … +2.4; boulder tops z 0.9–1.25 (front band h .0–.2, tops to h .26).

### 2.3 Spots (gem Ø; cap-local ρ, φ)

| Gem | Cap | Ø | ρ | φ | Sheet evidence |
| --- | --- | --- | --- | --- | --- |
| S1 | big | 1.40 | 0.42 | 10° | the crown gem: front (.60,.90) 46 × 23 px; f34 (.59,.87); rear (.34,.91); top's biggest |
| S2 | big | 1.10 | 0.65 | 215° | front (.18,.77) 35 × 31 |
| S3 | big | 0.70 | 0.78 | 240° | front (.25,.68) 22 × 22 |
| S4 | big | 0.45 | 0.88 | 180° | front (.05,.55), seen edge-on on the left flank |
| S5 | big | 1.15 | 0.62 | 140° | rear (.79,.81) 38 × 32 |
| S6 | big | 0.85 | 0.70 | 60° | top: upper-left gem of the big cap (mirrored → +X back flank) |
| s1 | small | 0.75 | 0.30 | 160° | front (.71,.59) 19 × 9; top's small-cap gem 36 × 40 |
| s2 | small | 0.62 | 0.62 | 320° | front (.90,.52) 20 × 20 |
| s3 | small | 0.40 | 0.70 | 240° | front (.77,.49) 11 × 9 |
| s4 | small | 0.30 | 0.86 | 0° | front (.98,.39), right flank |
| s5 | small | 0.50 | 0.65 | 80° | rear (.08,.59) 17 × 14 |

- Each gem's axis follows the cap's local surface normal at its position (after the droop). Gem tables must stay
  inside one cap face ring band where possible so the pocket floor is flat.
- **Expected front glow:** about 7 % of the silhouette (C / (P + C) about 12 %), mostly S1 and S2.

### 2.4 Checks on the renders

- **front_sheet (0, 8):** W : H 1.22–1.36 (sheet 1.291); shares ±4 of 49.1 / 6.8 / 20.5 / 2.2 / 21.5 (C ±2); top
  profile ±0.06 (the step from .86 to .64 at f .80–.85); width per height ±0.07; big cap visible h .39–1.0 with its
  left rim lowest; small cap f .60–1.00, h .27–.64, in front of the big stem's right side.
- **f34_sheet (0, 14):** shares ±4 of 49.3 / 8.2 / 18.7 / 2.4 / 21.3; the same gem fractions as the front ±0.04.
- **rear_sheet (180, 8):** shares ±4 of 46.4 / 3.7 / 16.9 / 8.3 / 24.8; the big stem hides the small cap's right edge;
  L1 in front of the small stem.
- **side_sheet (270, 8)** (camera at −X): D : H 0.95–1.10; the small cap at screen right, behind the big stem; L2 at
  screen left.
- **r34_sheet (180, 14)** and **top (0, 89, mirrored) + top_tilt (0, 70, mirrored):** shares and counts (§3).

## 3. View conflicts and resolutions

### 3.1 The three-quarter cells are elevated front and rear views

- **Evidence.** Every gem, cap edge and stem in the f34 sits at the front cell's fractions within ±0.03; the r34 repeats
  the rear's within ±0.05. A real 30° turn would move the small stem 0.5 studs nearer the big one (or 1.0 further) and
  hide or expose the small cap; neither happens. The f34's crown gem is seen a little more open (W : H 1.7 against
  1.5), so its camera is about 6° higher. The f34 is drawn 6 % wider (W : H 1.37 against 1.29).
- **Resolution.** Compare the hero with **`f34_sheet (0, 14)`** and the r34 with **`r34_sheet (180, 14)`**, by shares,
  gem places and profiles, not by W : H. The kit front34 (−28) and rear34 (152) are self-consistency only.

### 3.2 Where the small mushroom stands, and which way the side camera looks

- **Evidence.**
  - Front: the small cap's rim passes **in front of** the big stem (`z_front_small.png`).
  - Rear: the big stem passes **in front of** the small cap (`z_rear_small.png`).
  - So the small mushroom is nearer the front camera: **front-right, about (+1.85, −1.35)**.
  - Side: the small mushroom is at screen right and **behind** the big stem (`z_side_small.png`). From the kit side
    camera (+X) a mushroom at +X would be the nearest thing, so this cell is drawn from **−X**, where screen right is −Y
    (the front): it agrees with front-right.
  - The leaf clump at the side cell's screen left is then at the back-left (L2), which the rear confirms (L2 at
    X −2.1, behind the big stem from the front).
- **Resolution.** Small mushroom front-right of the big one. Compare the side cell with an extra **`side_sheet (270,
  8)`** (camera at −X); **probe the handedness with one render first.** The kit side (90) is self-consistency only.

### 3.3 The top cell is mirrored

- **Evidence.** The top shows the big cap upper right and the small cap lower left. With image top = back (kit
  convention), the front, rear and side put the big cap back-left and the small front-right, so the top's left and
  right are swapped.
- **Resolution.** Flip our kit `top (0, 89)` and `top_tilt (0, 70)` renders left-right before comparing; judge by
  shares (±6), gem counts (big 3–5, small 2–4) and boulders showing outside the caps on two opposite corners.

### 3.4 Cap widths: the side draws both caps 0.73 as wide as the front

- **Evidence.** Big cap: front 5.86, f34 6.03, r34 5.53, exploded 5.86, **side 4.27** studs. Small cap: front 2.81,
  f34 3.23, r34 2.79, exploded 2.87, **side 2.15**. Both caps shrink by the same 0.73–0.77 in the side while the big
  stem keeps its width (front 2.13 against side 1.99 at h .42). A round cap projects to the same width from every
  side, so the sheet draws the caps as ovals (wider across X), or the side is drawn compressed. The top cell, a tilted
  view, gives the big cap 180 × 155 px (0.86), which an oval of 0.8 fits once the tilt and the dome's height are
  counted.
- **Resolution.** **Oval caps at Y/X 0.80** (big 5.8 × 4.65, small 2.8 × 2.25; decision §8.3): the front governs X,
  the side's depth is met halfway. Expect the side_sheet big cap at about 0.82–0.86 of D (sheet 0.77) and record it.

### 3.5 Which way the big cap droops

- **Evidence.** The front, f34, rear and r34 all put the big cap's −X rim lowest (front left rim h .39–.45 against
  the right's .79–.81; r34 screen right (−X) .43–.53 against the screen left's .63–.76), with the crown over the stem.
  The side, from −X, should then show the near (−X) rim low across the middle; it shows the screen-left (back, +Y) rim
  low (h .47–.51) and the middle of the cap's bottom high (h .62–.66), as if the cap drooped to the back instead. The
  rear contradicts a back droop: from behind, the cap's bottom over the big stem is at h .55–.62 (z 3.0–3.4), as high
  as from the front.
- **Resolution.** Four views against one: droop the big cap toward −X only (§1.4, s +0.33), crown over the stem. Our
  side_sheet will show the big cap's bottom lower across the middle (about h .40–.50 against .62–.66) and less of the
  big stem (visible to about h .45 against .66); record it, don't chase it.

### 3.6 Holes, pegs and sockets

- The base's stem holes, the dot on the Large stem's top, and the pockets' role as sockets are joinery notation, except
  the gem pockets, which the Spot Junction close-up and every view show as a visible recess ring. **Model the gem
  pockets (§8.6); no stem holes or pegs anywhere.**

### 3.7 Mushroom count: 3 in the exploded against 2 everywhere else

- Build **2** (decision §8.2): five views, the top and the base's two holes show two; the exploded's left mushroom
  repeats the right one.

### 3.8 "Solid colors" against the user's blended-colour rule and the glow

- The user's rule wins, and the sheet itself shows two cap keys (Cap and Cap (Light)), a three-tone gem, a leaf base →
  tip gradient and a darker stem foot (§5.3). Keep Tint low so the asset still reads "clean".
- "Bioluminescent" and the spots' brightness on their shade side (v ≥ 0.85 for 90–95 % of spot pixels in the rear and
  side too) make the gems emissive. The caps are not: their shade quartile falls to `#392D52`.

## 4. Construction plan (modeller, stages 1–3)

1. **Parts first,** each from its own function and checked against its cell:
   - `shell()` → `MooncapShell`: the big cap (5.8 × 4.65 × 2.4) with its six empty pockets, symmetric (no droop). Compare with the
     exploded cap: flat crown about 0.3 of the diameter, two shoulder rings, a vertical rim band, a faceted underside
     cone (render one shot from below like the close-up), 14 sectors, triangle/kite facets.
   - `glow_spot()` → `MooncapGlowSpot`: the S1 gem (Ø 1.4) whole, table + crown + pavilion. Compare with
     `z_insert.png` and `z_cu_spot.png`: 8 sides, W : H 1.0–1.2.
   - `stalk_large()` → `MooncapStalkLarge`, `stalk_small()` → `MooncapStalkSmall`: the §1.4 hero profiles. Compare
     with the exploded stems: widest at 0.55–0.7 of the length from the top, the top 0.58–0.62 of the max width.
   - `leaf_clump()` → `MooncapLeafClump`: L1. Compare with `z_leaf.png`: 4–5 kite leaves, W : L 0.36–0.40, sharp tips.
   - `rock_base()` → `MooncapRockBase`: slab + 10 boulders + 3 pebbles (§2.2). Compare with `z_expl_base.png`.
   - Render a parts shot (`extra`, about (−20, 20)) laid out like the exploded (cap shell top, gem right of it, stems
     under, base bottom, leaf clump left).
2. **Hero:** `_paste` (m011 pattern) the base, the stems, the caps (drooped, §2.1), the gems and the leaves, then
   unite into one closed shell **one piece at a time**, saving the work file between risky steps:
   1. base: slab + boulders (`union_loose`, then one exact union);
   2. each stem into the base;
   3. each cap: build it drooped and placed, carve its pockets (8-sided prisms, one at a time, axis along the local
      face normal, depth 0.10 × Ø, Ø 1.18 × the gem's girdle), union its gems (girdle 0.04 below the pocket rim), then
      union the cap onto its stem;
   4. leaves last; `m004.floor_cut` at z 0.
   Origin at the bbox bottom centre; transforms applied. Decision §8.7.
3. **Budget** (§4.4): hero about 2600–3300 (limit 4000), parts ≤ 1000 each. Spend spare tris on boulder facets, never on
   smoothing.
4. **Placeholder keys** (stage 1): `m030_cap`, `m030_spot`, `m030_stem`, `m030_leaf`, `m030_rock`. Keep each gem's
   faces separable (Neon keys must land on whole gem faces only). Stage 4 adds the rest (§5.4).

### 4.2 Stage 1 acceptance (measurable; written from the 022–027 verifier failures)

Render the `*_sheet` cameras **with the studio floor hidden**. Use this folder's `m.py` masks on both images.

1. **Overall read:** two thick faceted violet caps, the big one drooping left and the small one drooping right, each
   with its flat crown over its stem, on fat
   cream pear stems, a boulder ring, two leaf clumps at the back, cyan gems; nothing round, nothing smooth, no
   open-bowl caps.
2. **Caps are faceted polygons, not balls** (the "seed read as a flame" lesson): in front_sheet the big cap's upper
   outline has 6–9 Douglas–Peucker segments (eps 2 px) with a flat crown segment over 0.20–0.32 of the cap width; the
   small cap's 6–9. Visible W : H big cap 1.62–1.88 (sheet 1.75), small 1.25–1.50 (1.37) in the front; f34 1.65–1.90 /
   1.40–1.65. **The big cap's lowest point is its left rim** (h .36–.48) and its right rim is at h .72–.86; **its
   flat crown is centred at 0.55–0.72 of the cap's width from the left** (sheet 0.65), not left of centre (a rigid
   tilt fails this); the small cap's crown at 0.35–0.60 of its width (sheet 0.45–0.55).
3. **Stems:** front_sheet big stem widths per z within ±0.2 of §1.2 (2.25 / 2.40 / 2.34 / 2.10 at z 1.2 / 1.6 / 2.0 /
   2.4), visible h .14–.58; small stem 1.25–1.5 at z 0.8–1.6, visible to h .36–.40.
4. **Silhouette per view:** W : H front 1.22–1.36, side (270) 0.95–1.12, rear 1.17–1.31; top profiles ±0.06 at every
   0.05 f including the cap step (front .86 at f .80 → .64 at .85); width per height ±0.07 at h .1, .3, .5, .7, .9.
5. **Shares per view** (P / C / T / G / R ±4, C ±2, top ±6), **rear included**: §1.2 table; C / (P + C) ±3.
6. **Who hides whom** (§3.2): front: the small cap overlaps the big stem; rear: the big stem overlaps the small cap;
   side (270): the small cap behind the big stem.
7. **Gems:** 11 gems; per view visible gem counts big / small: front 4 / 3–4, rear 2–3 / 2–3, top (mirrored) 3–5 /
   2–4; S1's centre in front_sheet at f .56–.64, h .86–.94; every gem 8-sided with a table, in a visible pocket ring.
8. **Rock band:** h .0–.1 at least 95 % rock and h .1–.2 at least 75 % in the front, side and rear; 6–7 boulders across
   the front.
9. **Leaves:** rear_sheet G 8.3 ± 3 with two clumps (L1 f .14–.44, L2 f .68–.94); front G ≤ 4 %.
10. **Kit views** (front34, rear34, side 90, underside): self-consistency; the underside shows the slab and boulder
    bottoms flat.
11. **Parts against their cells** (step 1). **Hero size** 7.1 × 5.5 × 5.5 (±0.35 / ±0.4 / ±0.25).

### 4.3 Stages 2 and 3

1. **Stage 2:**
   - zero non-manifold, boundary, wire and loose elements; zero bowtie vertices (`M.audit()`; pocket rims and the stem
     / underside join are the likely spots, `M.fix_bowties`); no zero-area faces or n-gons; normals outward;
   - no faces under 5° where gems meet pockets, stems meet caps and boulders meet stems (m011 `_tidy` / `_desliver`);
   - don't decimate a cap below its 14 / 12 sectors and 7 rings, a gem below 8 sides with its table, a stem below 8
     sides and 5 rings, a boulder below 5 sides, or a leaf below its 6-point outline with midrib.
2. **Stage 3:** smart UV, margin ≥ 0.008, no overlaps, even texel density.

### 4.4 Budget table

| Piece | Count | Tris each | Total |
| --- | --- | --- | --- |
| Big cap (14 sectors × 7 rings + apex) | 1 | 180 | 180 |
| Small cap (12 sectors) | 1 | 150 | 150 |
| Pockets (added faces after the carve) | 7 | 25–35 | 210 |
| Gems (table, crown, pavilion) | 11 | 32 | 352 |
| Big / small stem | 2 | 140 / 96 | 236 |
| Leaves | 9–10 | 16 | 160 |
| Boulders (6–8-sided, 2 rings, peak) | 10 | 50–65 | 580 |
| Pebbles | 3 | 24 | 72 |
| Slab (14-gon, raised top ring) | 1 | 84 | 84 |
| **Sum before union** | | | **about 2000** |
| **Hero after union** (seams, slivers, floor cut) | | | **about 2600–3300** (limit 4000) |
| Parts: Shell / GlowSpot / StalkLarge / StalkSmall / LeafClump / RockBase | | | about 380 / 32 / 140 / 96 / 80 / 740 (limit 1000) |

## 5. Colour plan (modeller, stage 4)

### 5.1 Swatches (flat; medians of a 40 × 40 box inside each; swatches at y 1349–1409)

| Swatch | Box | Hex | HSV |
| --- | --- | --- | --- |
| Cap | (39,1359,79,1399) | `#5A478F` | 256°, 0.50, 0.56 |
| Cap (Light) | (111,1359,151,1399) | `#9476D5` | 259°, 0.45, 0.84 |
| Spot | (185,1359,225,1399) | `#8CE9EE` | 183°, 0.41, 0.93 |
| Stem | (257,1359,297,1399) | `#E8CCA4` | 35°, 0.29, 0.91 |
| Rock (Dark) | (331,1359,371,1399) | `#796359` | 19°, 0.26, 0.47 |
| Rock (Light) | (404,1359,444,1399) | `#AE876A` | 26°, 0.39, 0.68 |
| Leaf | (482,1359,522,1399) | `#849333` | 69°, 0.65, 0.58 |

- **Cap** is the flank / rim colour (rendered bottom bands `#51417F`–`#58489C`); **Cap (Light)** the crown (top bands
  `#8870DE`–`#9072DB`).
- **Spot** is paler and less saturated than the rendered gems (mid `#69E5F5`–`#79E8FA`, sat 0.50–0.54).
- **Stem** matches the unshadowed exploded stems (`#E0C097`–`#E6C89F`).
- **Rock (Dark)** matches the rendered rock medians (`#755F56`–`#7B675F`); **Rock (Light)** is warmer and more
  saturated than any rendered rock face (lit quartiles `#9D8679`–`#A18B85`, sat 0.20–0.26): use it only as the warm end
  of the light key.
- **Leaf** sits between the rendered leaf middle (`#80922C`) and the swatch.

### 5.2 Rendered regions (`samp.py`, `grad.py`; median / lit quartile / shade quartile)

| Region | Box | Mask | Median | Lit | Shade |
| --- | --- | --- | --- | --- | --- |
| Cap, front / f34 | V | P | `#6356BD` / `#6859C0` | `#8D75DF` / `#9378E0` | `#4A3B77` / `#513F7D` |
| Cap, side / rear / r34 / top | V | P | `#5A489F` / `#604DA3` / `#614FA9` / `#725BC2` | `#896FDD` / `#8B76DE` / `#8D77E1` / `#896DD7` | `#3F3156` / `#392D4D` / `#392D52` / `#564799` |
| Cap shell, exploded all / top half | (170,758,470,930) / (170,758,470,840) | P | `#6D5BC5` / `#7868D1` | `#9375DF` / `#9274DD` | `#54458F` / `#6658C2` |
| Small caps, exploded R / L | (398,918,545,1020) / (99,955,260,1062) | P | `#6653B5` / `#6657BA` | `#987BE3` / `#846BD6` | `#4D3D75` / `#52428B` |
| Cap underside (close-up) | (676,760,1000,920) | P | `#4D3B72` | `#8469D3` (rim band) | `#41325F` |
| Pocket ring (Spot Junction) | (850,960,1000,1135) | P | `#574AAB` | `#5E51B5` | `#5346A1` |
| Spots, front / f34 / rear / side | V | C | `#73E7F8` / `#71E8F7` / `#7AEAFA` / `#7CDFF7` | `#AFFCFE` / `#B3FBFD` / `#B2FCFE` / `#A5F8FC` | `#48AADE` / `#42BFE1` / `#5CB4E6` / `#5DA8E3` |
| Spots, exploded shell / insert / Spot Junction | §1.4 boxes | C | `#70E9F7` / `#7EE8F3` / `#83EEF9` | `#AEFBFD` / `#9DF7FA` / `#88F1FB` | `#45C0E0` / `#57B9BE` / `#43C9E0` |
| Stems, front / f34 / rear / side | V | T | `#C7A881` / `#C8A780` / `#D6B891` / `#E6C79F` | `#EFD3AD` / `#F1D5B0` / `#F7DEBB` / `#FCE4C3` | `#94795A` / `#987C5B` / `#977D5D` / `#A98B69` |
| Stems, exploded Large / Small R / Small L | §1.4 boxes | T | `#E6C89F` / `#E0C097` / `#E3C59E` | `#FCE3C0` / `#FAE0BE` / `#FBE1BD` | `#BFA17C` / `#B49571` / `#B69873` |
| Stem at the Base Junction / under the cap (close-ups) | (850,1150,1000,1295) / (676,760,1000,920) | T | `#C6A379` / `#DEBF98` | `#F2D5AF` / `#FBE5C7` | `#9F7F5B` / `#AE906F` |
| Leaves, rear / r34 / top | V | G | `#818F22` / `#809121` / `#7C8A29` | `#AAB829` / `#ABBA2D` / `#A1AE35` | `#576417` / `#5B6818` / `#565C1F` |
| Leaves, front / f34 (in shade) | V | G | `#4F5918` / `#525D17` | `#636B20` / `#68741E` | `#39400F` / `#39400E` |
| Leaf clump, exploded | (90,1118,188,1205) | G | `#80922C` | `#A3B332` | `#627122` |
| Rock, front / f34 / side / rear / top | V | R | `#755F56` / `#77635B` / `#7B675F` / `#7A655A` / `#695B55` | `#9C857B` / `#9D8679` / `#A18B85` / `#A08C86` / `#988076` | `#53443C` / `#53443D` / `#584840` / `#57473E` / `#423734` |
| Base, exploded / Base Junction | (155,1148,555,1292) / (850,1150,1000,1295) | R | `#7D685F` / `#7C6862` | `#9E8B86` / `#A28E86` | `#5C4D46` / `#5E504A` |
| Dirt slab, exploded (probes) | (270–380, 1195–1225) | all | `#685951`–`#7C665F` (h 14–21°, sat 0.22–0.31, v 0.40–0.49) | | |

**Gradients along a part** (medians in five equal steps):

```
cap bottom -> top (whole visible cap: underside and rim band first, crown last)
  front       #4B3D79 #58489C #6254B9 #8469D8 #8870DE
  f34         #503F7B #5E4DA7 #6959C1 #8B6ED9 #8C73E0
  rear / r34  #4B3C5C #4A3960 #4B3A6D #6C5BC1 #8873DF  /  #4B3B5D #49385E #6953B8 #856AD9 #8C77E3
  exploded    #51417F #604EAA #715BC6 #9072DB #8D71DD      (shell; small caps R #53427F ... #977BE3)
stem top -> bottom
  front       #9E8261 #C2A37E #DCC096 #D3B58E #BFA07A      (top fifth in the cap's shade)
  rear        #9D8264 #C6AA89 #F4DBB9 #EBCEA7 #D5B388
  exploded L  #E0C099 #EACDA8 #F0D5B2 #E4C49A #BF9E75      (S: #A58868 #D0B28D #F5D9B4 #F9DDB5 #DAB98E)
leaf base -> tip
  exploded    #677724 #76892A #83972E #94A532 #9EAC36
  rear L1     #5C6919 #7F8A1E #818F22 #A0A92A #99AA30
```

**Spot colour split** (share of C pixels; deep = hue ≥ 192° or v < 0.88, light = sat < 0.38, mid = the rest):

| View | Deep | Mid | Light |
| --- | --- | --- | --- |
| f34 | 17 % `#44AAD9` | 50 % `#69E5F5` | 32 % `#ADFBFD` |
| front | 26 % `#56ACDF` | 48 % `#6CE7F8` | 25 % `#AFFBFE` |
| rear / r34 | 26 / 20 % `#64B8E8` / `#5EB4E7` | 41 / 45 % `#6FE9F9` / `#6FECFA` | 33 / 35 % `#B0FBFD` / `#B2FBFD` |
| side / top | 41 / 28 % `#6FB9EC` / `#44A7CB` | 43 / 45 % `#79E8FA` / `#6EEAF7` | 16 / 27 % `#AAF8FC` / `#AEFBFD` |
| exploded shell / insert | 16 / 33 % `#42B0D6` / `#59CCD7` | 57 / 49 % `#6EE8F6` / `#94F5F9` | 27 / 18 % `#ADFBFD` / `#A3F7F9` |

### 5.3 How the colour works

**Caps.**
- One blue-violet family: hue 248–253°, **sat 0.50–0.54** in every view median (keep it there; 025's leaves came out
  dull because the saturation dropped). Unshadowed exploded median `#6D5BC5`.
- **Painted crown → rim gradient** on every drawing, including the exploded shell and the rear: crown `#8870DE`–
  `#9072DB` (Cap (Light)) → flank `#6254B9`–`#715BC6` → rim band and underside `#4B3D79`–`#51417F` (Cap). Part of it
  is light, but the two swatches say it is also paint. Paint it by position along the cap's own axis (never by facing).
- The underside is the darkest violet (`#4D3B72`, close-up); the pocket floor ring a little darker than the flank
  around it (`#574AAB`).
- No cyan wash on the caps round the gems: the pocket ring is darker, not bluer.

**Gems.**
- Self-lit: 90–95 % of gem pixels at v ≥ 0.85 in every elevation view (the rear and side too). Three tones by facet:
  **light** table faces `#ADFBFD`–`#B2FBFD` (sat 0.30), **mid** crown bevels `#69E5F5`–`#79E8FA` (hue 186–188°, sat
  0.50–0.54), **deep** lower bevels `#44AAD9`–`#64B8E8` (hue 195–200°, sat 0.62–0.70). Split about 25 / 48 / 27.

**Stems.**
- Cream, hue 33–35°, sat 0.30–0.36. Unshadowed `#E6C89F`. The top fifth darkens under the cap (`#9E8261`, shade, not
  paint); the foot is darker than the middle in every drawing including the exploded (`#BF9E75` at the bottom fifth,
  `#C6A379` at the Base Junction): paint a mild darker foot band.

**Leaves.**
- Yellow-green, hue 68–71°, **sat 0.70–0.77**. **Painted base → tip gradient**: base `#677724` → middle `#83972E` → tip
  `#9EAC36`. The front and f34 leaves look dark (`#4F5918`) only because they stand in the stems' and caps' shade.

**Rocks and dirt.**
- Warm brown-grey, hue 14–21°, sat 0.20–0.26 (never purple, never orange). Unshadowed `#7D685F`; lit faces `#9E8880`
  (a few reach `#B2998B`); shade `#53443D`–`#5C4D46`. The dirt slab is a little darker and redder (`#685951`–`#735B54`).

### 5.4 Keys (start from these; `K.calibrate`; write the calibrated hexes into `palette()`)

Calibration targets are rendered medians of **unshadowed** regions (exploded parts and close-ups), not swatches.
`K.sample` kinds: `"vivid"` for the caps and gems, `"green"` for the leaves, `"brown"` for rock and dirt, `"all"` on
tight boxes for the stems.

| Key | Calibration target | Where | Finish |
| --- | --- | --- | --- |
| `m030_cap` | `#6A58C2` (exploded flank bands `#604EAA`–`#715BC6`; view medians `#6356BD`–`#6859C0`); sat ≥ 0.50 | cap flanks (axis height 0.25–0.65 of hc) | rough 0.7, metal 0 |
| `m030_cap_light` | `#8C70DC` (crown bands `#8870DE`–`#9072DB`; Cap (Light) `#9476D5`) | crown ring, apex fan and the upper shoulder above 0.7 hc | rough 0.7 |
| `m030_cap_dark` | `#4F3F7C` (rim and underside bands `#4B3D79`–`#51417F`; underside `#4D3B72`; Cap `#5A478F`) | underside rings, the lower half of the rim band, the pocket walls and floor rings | rough 0.75 |
| `m030_spot` | `#6FE8F8` (mid medians `#69E5F5`–`#79E8FA`) | crown bevels | **emission ≥ 1.0 → Neon** |
| `m030_spot_light` | `#AEFBFD` (light medians `#ADFBFD`–`#B2FBFD`) | the table faces | **emission ≥ 1.0 → Neon** |
| `m030_spot_deep` | `#52B0E2` (deep medians `#44AAD9`–`#64B8E8`) | the lowest crown row and the pavilion | **emission ≥ 1.0 → Neon** |
| `m030_stem` | `#E6C89F` (exploded Large `#E6C89F`, Small `#E0C097`; swatch `#E8CCA4`) | stem bodies | rough 0.85 |
| `m030_stem_base` | `#C8A67B` (bottom fifths `#BF9E75`–`#DAB98E`; Base Junction `#C6A379`) | the lowest 25 % of each stem | rough 0.85 |
| `m030_leaf` | `#82952E` (exploded `#80922C`, mid fifth `#83972E`; swatch `#849333`) | leaf middles (t 0.3–0.7) | rough 0.75, `low_spec` |
| `m030_leaf_base` | `#697925` (base fifths `#677724`, rear `#5C6919`) | inner 30 % | rough 0.75, `low_spec` |
| `m030_leaf_tip` | `#9DAC35` (tip fifths `#9EAC36`, `#99AA30`) | outer 30 % | rough 0.75, `low_spec` |
| `m030_rock` | `#7B665D` (exploded base `#7D685F`; views `#755F56`–`#7B675F`; Rock (Dark) `#796359`) | boulder bodies | rough 0.92 |
| `m030_rock_light` | `#9E8880` (lit quartiles `#9D8679`–`#A18B85`; Rock (Light) `#AE876A` as the warm end) | broad patches, about 25 % of each boulder, crowns | rough 0.92 |
| `m030_rock_dark` | `#5C4B43` (shade quartiles `#53443D`–`#5C4D46`) | the lowest 20 % of each boulder; faces within 0.2 of a stem or neighbour; pebbles | rough 0.92 |
| `m030_dirt` | `#6C5850` (exploded floor `#685951`–`#735B54`) | slab top and sides | rough 0.95 |

**Calibration warnings:**
- **Neon keys** render flat at their colour (emission ≥ 1.0) and export as Neon pieces, one flat colour each. Check
  the front_sheet gem median within 12 of `#73E7F8`, hue 184–190°, **sat 0.48–0.56** (not white, not teal); the light
  key must stay at least 40 levels above the mid in R (`#AE…` against `#6F…`) and the deep at least 25 below the mid in
  G, so the three tones survive Roblox's bloom. If the light key washes to white, lower its value; never raise emission.
- **Caps:** calibrate on the parts-shot shell against `#6D5BC5`; then front_sheet median within 12 of `#6356BD`, hue
  246–254°, sat ≥ 0.50; crown band (top fifth) within 15 of `#8870DE`; underside within 15 of `#4D3B72`.
- **Stems:** parts-shot within 10 of `#E6C89F`; front_sheet within 15 of `#C7A881`; sat 0.28–0.38 (not white, not
  orange).
- **Leaves:** greens calibrate darker than the painted sheet (kit memory): parts-shot within 12 of `#80922C`, sat ≥
  0.68; rear_sheet within 15 of `#818F22`.
- **Rock:** parts-shot base within 10 of `#7D685F`; front_sheet within 10 of `#755F56`; sat 0.18–0.28.

### 5.5 Blending (`K.blend(mode="blend", steps=3)` over explicit face lists; fields are positions, never facing)

- **Caps** (field u = height along the cap's own axis / hc, + 0.08 × per-face noise): underside rings → `cap_dark`;
  rim band → 50 % `cap_dark` / 50 % `cap`; u 0.15–0.65 → `cap`; u > 0.70 → `cap_light`, with a 3-step mixed band
  across 0.6–0.75 (alternate faces of the shoulder ring between the two keys so the change reads as scattered facets,
  not a stripe). Pocket walls and floor rings → `cap_dark` (hard edge at the pocket rim). The facing correlation must
  stay below 0.5 (`K.check`): the noise term and the droop matter.
- **Gems** (all Neon, whole facets): table → `spot_light`; crown upper row → `spot`; crown lower row + pavilion →
  `spot_deep`. Shares to land per view: deep 15–35 %, mid 40–56 %, light 18–36 % (§5.2).
- **Stems** (field = height on the stem / its height): bottom 25 % → `stem_base`, blending into `stem` over 0.15; the
  rest `stem`.
- **Leaves** (field = along-leaf t): t < 0.3 `leaf_base`, 0.3–0.7 `leaf`, > 0.7 `leaf_tip`; ±0.08 noise.
- **Rock:** body `rock`; broad noise patches (`K.patches` scale about 0.5) → `rock_light` at level 0.3 on the upper
  60 %; ground band (< 0.2 × the boulder's height) → 50 % `rock_dark`; contact faces within 0.2 of a stem or a
  neighbour → 35 % `rock_dark`. Pebbles `rock_dark` with 30 % `rock`. Dirt: `dirt`, 20 % `rock_dark` patches near the
  boulders.
- **Hard edges only** where materials meet: gem | pocket, cap underside | stem, stem | rock, leaf | rock or dirt.

### 5.6 Texture (Tint) and finish

- **Tint** (`tint_var` per piece about 0.04, so each boulder, leaf and cap differs slightly):
  - caps: `K.texture` amp 0.03, scale 0.5 (broad, per facet group); stems amp 0.03; leaves amp 0.03;
  - rock and dirt: amp 0.06, scale 0.45;
  - gems: none (Neon keys ignore Tint);
  - never per-triangle confetti ("solid colors").
- **Finish:**

| Material | Roughness | Specular | Metal | Notes |
| --- | --- | --- | --- | --- |
| Gem keys | 0.4 | low | 0 | Neon (emission ≥ 1.0) |
| Cap keys | 0.7–0.75 | low (`low_spec`, so the lit crown keeps its saturation) | 0 | matte violet with crisp lit facets |
| Stem keys | 0.85 | normal | 0 | matte; check the lit faces don't clip to white |
| Leaf keys | 0.75 | `low_spec` | 0 | |
| Rock, dirt keys | 0.92–0.95 | normal | 0 | matte |

### 5.7 Re-measure (final renders against the sheet, same boxes and masks)

- **Gems:** front_sheet median within 12 of `#73E7F8`; deep/mid/light split per §5.5; **bright share ≥ 85 %** of gem
  pixels at v ≥ 0.85 in the front, side, rear and f34, with VFX on and off; C share per §1.2 ±2.
- **Caps:** per §5.4 warnings; crown lighter than the flank and the flank lighter than the rim in every view.
- **Stems, leaves, rock:** per §5.4 warnings; foot band darker than the stem middle; leaf base darker than tip.
- **Shares** per §2.4 and §4.2.

## 6. Joins and contact

- **Stems into caps:** each stem's top ring sits 0.15 inside the cap's underside stem ring, coaxial; a 0.1–0.15 ledge
  of underside shows round it. No gap, no visible peg.
- **Stems into the base:** each stem foot stands on the slab (sunk 0.1) with 2–3 boulders touching it all round
  (Base Junction); no stem hole.
- **Gems in pockets:** pocket floor flat, gem girdle 0.04 below the pocket rim, table 0.08–0.12 × Ø proud of the cap
  surface; the pocket ring (0.08 × Ø) shows all round. The pocket wall stays ≥ 0.06 thick to the cap's underside
  ("no thin geometry"): at S4 / s4 near the rim, keep the pocket depth ≤ 0.04 or skip the pocket (§8.6).
- **Caps:** the small cap's −X rim tucks under the big cap's +X rim; they may touch, but with a clean overlap ≥ 0.05,
  never a sliver gap under 0.05.
- **Leaves:** each clump's root sinks 0.25 into the slab between two boulders; leaves overlap at their bases (never
  coplanar).
- **Ground:** floor-cut at z 0.
- Overlap everything; exact booleans one piece at a time (pitfall 9).

## 7. Lighting and VFX plan (modeller, stages 5 and 6)

**What the sheet shows:**
- The gems glow: self-lit, bright cyan on every side (§5.3), and the header says "bioluminescent".
- No halo round the gems, no cyan light on the caps, stems or rocks, no spores, mist or sparkle; there is no VFX panel.

### 7.1 Stage 5 (lighting)

- **Emissive (Neon) keys: `m030_spot`, `m030_spot_light`, `m030_spot_deep`** at emission ≥ 1.0 (start at 1.2), one flat
  colour each. Each exports as a Neon glow piece with no collision; the export STATS line should report 3 glow pieces.
  Emission between 0 and 1 does nothing in Roblox except drop the Tint; don't use it. Caps, stems, leaves, rock and
  dirt: emission 0.
- **Light (decision §8.8):** one soft cyan PointLight carried by a `crystal_glow` socket (light only): colour
  `#7FE9F8`, brightness about 0.5, range 8, shadows true, no flicker. Place it in the open in front of and between the
  caps, about (+0.6, −2.7, 3.6), at least 0.6 from every surface (check by BVH). It must not tint the stems or rocks:
  the front_sheet stem and rock medians with VFX on stay within 10 of the VFX-off values. (WorldModeling §11: cave
  mushrooms read by "shape and placed lighting".)
- **Studio note (Requires Manual Validation):** check the three gem tones stay distinct under Neon bloom, and that the
  light reads in a dark cave without washing the cream stems cyan.

### 7.2 Stage 6 (VFX), kinds in `art/blender/lib/vfx.py`

- **Kinds that exist:** `torch_fire`, `campfire`, `brazier_fire`, `forge_fire`, `chimney_smoke`, `embers`,
  `heat_glow`, `glyph_glow`, `rune_glow`, `waterfall_mist`, `water_foam`, `waterfall_curtain`, `water_flow`, `vapour`,
  `harvest_hit`, `harvest_deplete`, `ore_glint`, `crystal_glow`, `crystal_halo`, `dust`. No new kind is needed.
- **Recommended:** only the `crystal_glow` light above (one socket). The sheet shows no particles or halo.
- **Not added:** `crystal_halo` (no halo drawn; it would veil the caps), `glyph_glow` (R08's choice: pulsing light and
  puffs), `dust` spores (R08 had them; not on this sheet), `ore_glint` (the gems glow, they don't twinkle).
- **Option** (decision §8.8): R08-style faint cyan spores, `dust` with `dust_mote`, colour `["#AFFBFD", "#6FE8F8"]`,
  rate 0.8, shape about [5, 3, 4], light_emission 0.8, socket at (0, 0, 4.5).
- **Harvest sockets:** none (as M025; gameplay sockets later in one pass).
- All sockets on the hero only. Render with `vfx=True`; if the preview stand-ins veil the model, render the compare
  set with them hidden plus one shot with them, and record that.

## 8. Naming and decisions for the main session

**Names owned elsewhere.** Found by `git grep -w` of the repo and a search of every sheet .blend, zstd-decompressed
(`m020_study/blendall.py` run with the uv Python 3.14):
- **R08 kit:** `Mooncap` (61 hits in `FlintbornWorldKit.blend`), `MooncapCapShell`, `MooncapSpotInsert`, `MooncapStem`,
  `MooncapBase`, `MooncapDrop`, `MooncapDepleted`, `SporePod`; keys `r08_cap_purple`, `r08_spot_cyan`,
  `r08_stem_cream`, `r08_spore`, `r08_leaf_green`, `r08_rock` (`art/blender/scripts/kit/R08/mooncap.py`,
  `art/roblox/kit/R08/manifest.json`).
- `MooncapSpot` and `MooncapCap` occur in the kit .blend only as substrings of `MooncapSpotInsert` / `MooncapCapShell`;
  avoid them anyway.
- **R07 kit:** `CaveMushroom*` (56 hits); **V05:** `ChestnutMushroom*`.
- `M.mk` would silently rename a clash to `<name>M030`, so avoid all of these.

**Proposed names.** `MooncapNode`, `MooncapShell`, `MooncapGlowSpot`, `MooncapStalkLarge`, `MooncapStalkSmall`,
`MooncapLeafClump`, `MooncapRockBase` and the `m030_` prefix occur nowhere in the repo or any sheet .blend.

| Object | Part | Why |
| --- | --- | --- |
| `MooncapNode` | hero | `…Node` like `EmberbloomNode`; R08 owns `Mooncap` |
| `MooncapShell` | Cap Shell (big cap, empty pockets) | R08 owns `MooncapCapShell` |
| `MooncapGlowSpot` | Spot Insert (S1 gem whole) | R08 owns `MooncapSpotInsert` |
| `MooncapStalkLarge` / `MooncapStalkSmall` | Stem (Large) / Stem (Small) | R08 owns `MooncapStem` |
| `MooncapLeafClump` | Leaf Clump (L1) | free |
| `MooncapRockBase` | Base (slab, boulders, pebbles) | R08 owns `MooncapBase` |

- Palette keys `m030_*` (§5.4). Collection `Kit/M030 Mooncap`.

**Decisions needed (a recommendation each):**
1. **Size** (§1.1): **7.1 × 5.5 × 5.5** (recommended: 1.0 C, as M025 Emberbloom, its §11 sibling; crown at head
   height, knee-high boulders), or 1.3 C (9.3 × 7.3 × 7.2, near R08's scale), or 0.8 C (5.7 × 4.5 × 4.4).
2. **Mushrooms:** **2** (recommended: every assembled view, the top and the base's two holes), or 3 (the exploded's
   extra left one).
3. **Cap plan shape** (§3.4): **oval, Y/X 0.80** (recommended: front X, side depth met halfway; fits the f34, r34 and
   the top cell), or round (side_sheet then reads about 0.20 D too deep).
4. **Layout and cap shape** (§1.2, §3.2, §3.5): **small mushroom front-right of the big one; each cap eccentric and
   drooping, crown over its stem: the big cap's rim slopes down toward −X (−X rim 2.15, +X rim 4.05), the small cap's
   toward +X; no front/back droop** (recommended: the front, f34, rear and r34 agree; the side cell is drawn from −X
   and its back droop is not chased), or rigidly tilted symmetric caps (simpler, but the crown then moves away from
   the stem, against every view).
5. **Gems:** **11 gems (6 big + 5 small), 8-sided with table, crown and pavilion; carved 8-sided pockets for the 7 gems
   ≥ 0.6 Ø, the 4 small ones sunk flush with a painted `cap_dark` ring** (recommended: the Spot Junction close-up and
   every view show pockets; the small flank gems are too near the rim for a safe pocket), or no carving at all (paint a
   `cap_dark` ring round every gem; no booleans in the caps).
6. **Hero packaging:** **one closed shell**, gems united into their pockets (recommended: STAGES default; the exporter
   still makes the gems separate Neon MeshParts, which satisfies "spots are separate meshes"), or the gems as separate
   closed shells inside the hero (no gem unions, but the pockets then hold intersecting shells).
7. **Union order:** base, stems, each cap (drooped and placed) with its pockets carved and its gems united, then the
   caps onto the stems, leaves last; one piece at a time, saving between (recommended).
8. **Stage 5/6:** **three Neon gem keys + one `crystal_glow` light (cyan `#7FE9F8`, 0.5, range 8)** (recommended: the
   sheet shows self-lit gems and says "bioluminescent"; no halo or particles are drawn), or Neon only (no light), or
   also R08-style `dust` spores (not on the sheet).
9. **Harvest sockets:** **none for now** (recommended, as M025), or R08's `harvest_hit` in violet and cyan.
10. **Exports:** **the hero plus 6 parts** (`…Shell`, `…GlowSpot`, `…StalkLarge`, `…StalkSmall`, `…LeafClump`,
    `…RockBase`) (recommended: the sheet's own part list), or also a `MooncapSmallCap` (the small cap is the same
    builder at 0.48 scale). R08's drop, spore pod and depleted state are not on this sheet; not built unless asked.
11. **Comparison cameras** (§3): `front_sheet (0, 8)`, `f34_sheet (0, 14)`, `rear_sheet (180, 8)`, `r34_sheet (180,
    14)`, `side_sheet (270, 8)` (probe the handedness first), kit top + `top_tilt (0, 70)` flipped left-right; kit
    front34, rear34, side (90) and underside as self-consistency; a parts shot `(−20, 20)`. **All `*_sheet` renders
    with the floor hidden.**
12. **Names** as proposed.

## 9. Pitfalls to avoid

1. **Round caps.** The caps are faceted polygons with a flat crown (0.26 of the width), two shoulder rings and a
   vertical rim band: not icospheres, not hemispheres, not R08's "small flat caps". Count the outline segments
   (§4.2 item 2).
2. **Open-bowl caps or thin rims.** "Keep thickness on caps": a real underside cone and a rim band about 0.35 thick
   (WorldModeling §18: "Mushroom is an open bowl balanced on a pole").
3. **A thin or straight stem.** The big stem is a fat pear (Ø 2.4 low, 1.5 at the top), the small one Ø 1.45 → 0.95;
   R08 was marked "thin stem". Not cylinders.
4. **Wrong droop or wrong side.** The big cap's −X rim is the lowest point of the cap and its flat crown stays over
   the stem (a rigid tilt moves the crown away: wrong); the small cap's +X rim is lowest; the small mushroom stands
   front-right and passes in front of the big stem from the front (§3.2).
5. **Oversized or dull gems.** Eleven gems Ø 0.3–1.4 (R08 was marked "oversized spots" and "no spot glow"). C share
   about 7 % from the front, bright share ≥ 85 %, mid tone sat ≥ 0.48. All three gem keys Neon.
6. **Gems stuck on, not set in.** Each gem sits in a pocket with a visible darker ring, its table only slightly proud.
7. **Colour by facing.** The crown → rim gradient is painted by axis height on each cap's own frame plus noise; lit and
   shade facets are the light's. `K.check` facing correlation < 0.5.
8. **Hidden boulders / buried stems.** The rock band is ≥ 95 % of h .0–.1 and ≥ 75 % of h .1–.2 in the front, side and
   rear, and the stems show from h .14 up.
9. **Exact booleans.** Carve pockets with clean 8-sided prisms (no coplanar faces with the cap's
   facets: offset the prism top 0.05 above the surface), one at a time, saving between; unite gems after the carve;
   remove slivers with m011's `_tidy` / `_desliver`; check bowtie verts at pocket rims.
10. **Comparing the wrong views.** The f34 and r34 are elevated front and rear views; the side cell is drawn from −X;
    the top is mirrored; the side draws the caps 0.73 as wide (§3).
11. **Measuring the ground shadow.** Hide the floor for the `*_sheet` renders.
12. **Naming clashes** with R08's `Mooncap*` / `SporePod` and R07's `CaveMushroom*` (§8). Don't edit shared helpers
    (`kit_models.py`, `kit_mcp.py`, `build_kit.py`, `lib/vfx.py`); put new helpers in `m030.py`. No commits, pushes or
    exports in the modeller's stages.

## Decisions (main session, 2026-10-29)

All recommendations are accepted:
1. Size: 7.1 W × 5.5 D × 5.5 H.
2. Two mushrooms, as every assembled view shows.
3. Oval caps with depth 0.80 of width.
4. Layout:
   - the small mushroom stands front-right;
   - the caps droop along X only, eccentric with the crown over the stem, never rigidly tilted;
   - the sheet's side cell is compared with `side_sheet (270, 8)`.
5. Gems: 11 (6 on the big cap, 5 on the small one). The 7 gems of Ø 0.6 or more sit in 8-sided pockets; the 4 small ones are sunk flush with a painted dark ring.
6. One closed shell with the gems united into it. The exporter still makes them separate Neon pieces.
7. Union order: base, then stems, then each cap with its pockets and gems, then leaves, one piece at a time.
8. Neon keys `m030_spot` `#6FE8F8`, `m030_spot_light` `#AEFBFD` and `m030_spot_deep` `#52B0E2`, each at emission ≥ 1.0, one flat colour. One `crystal_glow` socket, light only (cyan `#7FE9F8`, brightness 0.5, range 8, about (+0.6, −2.7, 3.6)), with its spill on stems and rocks within 10 levels.
9. No harvest sockets.
10. Hero plus the 6 parts.
11. Comparison cameras: front_sheet (0,8), f34_sheet (0,14), rear_sheet (180,8), r34_sheet (180,14), side_sheet (270,8) (probe the handedness first), and the kit top plus top_tilt (0,70) flipped left-right. The floor is hidden in every `*_sheet` render.
12. Names as proposed (`Mooncap*` hero and parts as listed, keys `m030_*`). Check that none collides with the old R08 `Mooncap*` objects in the kit file before building. If one does, use the study's fallback names.

## Stage 1 — Modelling (modeller, 2026-10-29)

Builder `art/blender/kit/mcp/m030.py` (`build()`), run in a background Blender (port 9881, work file
`art/blender/assets/kit/wip/M030.blend`). Names checked first: the work file holds R08's `Mooncap`, `MooncapBase`,
`MooncapCapShell`, `MooncapDepleted`, `MooncapDrop`, `MooncapSpotInsert`, `MooncapStem`, `SporePod` and no `m030_*`
material; none of the decided names collides, so they are used as decided. Collection `Kit/M030 Mooncap`.

**Parts** (each its own function, all in one build frame: front −Y, +X right, ground z 0):
- `MooncapShell` (`shell_part`): `_cap_geom`, a lathe of 7 rings each turned half a step (underside stem ring →
  underside ring ρ .68 → rim bottom → rim top (vertical band 0.15 hc) → shoulder .92/.42 → upper shoulder .70/.74 →
  crown .34/.96) + apex + underside centre; ±4 % radius, ±3 % height jitter; 14 sectors (big) / 12 (small). The Shell
  is the big cap undrooped with its **five** pocket gems' pockets carved (S1 S2 S3 S5 S6; S4 is a bezel gem, decision 5,
  so it has no pocket).
- `MooncapGlowSpot` (`spot_part`): `_gem(whole=True)`, the S1 gem Ø 1.40: 8-sided girdle, a mid crown ring turned half a
  step, a flat 8-sided table (Ø 0.56 of the girdle), a pavilion cone; crown 0.30 d, pavilion 0.62 d → W : H 1.09 (the
  exploded insert's rounded nugget, sheet 1.08). 48 tris.
- `MooncapStalkLarge` / `MooncapStalkSmall`: §1.4 hero pear profiles, 10 / 8 sides, rings turned half a step, flat ends.
- `MooncapLeafClump` (`clump_part`): L1, five thick kite leaves (convex hull of base, tip, two outline points per side
  at 0.30 / 0.58 L, a midrib ridge 0.6 T at 0.45 L and 0.35 T at 0.75 L, a keel −0.4 T), W : L 0.44, T 0.10 L; every
  leaf's hull also takes its own buried hub point (0.16 out along its azimuth, in the slab), so the leaves overlap.
- `MooncapRockBase`: a 14-sided faceted dirt slab (5.0 × 3.8, raised top) + 12 peaky dome boulders (`K.hull_rock`, rings
  7/7/5/2, flat bottoms each at its own depth) + 3 pebbles.

**Hero** (`MooncapNode`): `hero_body` (slab, boulders, pebbles, stems, the two drooped caps, two clumps) → exact unions
one shell at a time (`_union_fine`, merge 0.002, guarded) → the 7 pocket cutters carved one at a time (exact
difference; the cutters are cap_dark, so walls and floors come out dark) → the 11 gems appended and united → floor
cut at z 0 → m016 clean → finish → polish (m023 floor re-fan) → bowties. All booleans run with the object at the world
origin (see the pitfalls below).

**Layout as built** (changed from §2 on the renders; every change measured):
- Size **7.36 W × 5.58 D × 5.35 H** (decision 7.1 ± 0.35 × 5.5 ± 0.4 × 5.5 ± 0.25). Why: at 7.1 × 5.5 × 5.5 the
  front_sheet W : H came out 1.17 (sheet 1.291, accepted 1.22–1.36), because the 8° camera adds the ring's depth to the
  visible height. Widening inside the tolerance (big cap rx 3.0, small cap rx 1.47) and lowering the crown to 5.35 gives
  W : H 1.26.
- Big cap: rim centre (−0.70, 0.50), z0 2.75, rx 3.0, ry 2.4 (0.8), hc 2.6, e +0.70, s +0.33, stem ring r 0.88 on
  the stem top (−0.20, 0.35). Crown X range −0.04 … +0.70 (over the stem), left rim bottom z 1.8, right rim 3.6–3.98.
  The underside ring droops with weight 0.5 (weight 1 folded the small cap's underside into itself). z0 2.75 / hc 2.6
  (was 3.0 / 2.35): the cap's bottom edge per column then matches the sheet (front sheet
  `.45 .41 .39 .41 .43 .44 .46 .50 .52 .54 .57 .59 .57 .60 .64 .69 .75`, ours
  `.46 .40 .41 .43 .44 .46 .48 .50 .52 .54 .56 .59 .61 .64 .66 .69 .73`).
- Small cap: rim centre (2.18, −1.55), z0 2.0, rx 1.47, ry 1.18, hc 1.42, e −0.32, s −0.35.
- Gems: placed by casting a ray from the sheet's own camera at the gem's (f, h) in the sheet's front / rear cell onto
  the drooped cap (front: S1 .60/.90, S2 .18/.77, S3 .25/.68, S4 .05/.55, s1 .71/.59, s2 .90/.52, s3 .77/.49; rear:
  S5 .76/.84, s5 .16/.60; lathe: S6 ρ .70 φ 60°, s4 ρ .82 φ 20°). The axis is the normal of a plane fitted to the
  surface round the pocket rim (two passes); S2 / S3 / S4 lean 0.40 / 0.25 / 0.35 toward the front camera (the sheet
  draws S2 nearly face-on from the front, 35 × 31 px). The lathe guesses of §2.3 put S2 and S3 in one merged pocket.
- Pockets (7 gems ≥ 0.6): 8-sided, circumradius 0.58 d, floor 0.08 d under the mean surface round the rim; gem girdle
  0.02 above the floor, table 0.12 d above the mean surface. Bezel gems (S4, s3, s4, s5): a dark (cap_dark) collar
  ring r 0.64 d sunk under the surface up to the girdle, which sits 0.025 above it (decision 5's dark ring, built as a
  ring of faces instead of paint, since the cap facets are larger than the ring).
- Leaves: L1 root (1.55, 1.20, 0.80), five leaves L 1.3–1.7 at elevations 35–70°; L2 root (−2.0, 1.10, 0.65), four
  leaves L 1.0–1.35. Two back boulders added (B11 (1.35, 1.95) Ø 1.15, B12 (−2.5, 1.45) Ø 1.1) and B6 / B7 / B8 / B9 /
  B10 a little bigger, so from behind the leaves stand on a continuous rock band (rear R was 19.4 against 24.8).

## Stage 2 — Optimisation and cleanup

| Object | Tris | Size (studs) | Shells | NM edges | NM (bowtie) verts | Boundary | Wire / loose | Zero-area | n-gons | Self-int. | Min corner | Normals |
| --- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- |
| MooncapNode | 2880 | 7.36 × 5.58 × 5.35 | 1 | 0 | 0 | 0 | 0 / 0 | 0 | 0 | 0 | 5.01° | outward |
| MooncapShell | 452 | 6.06 × 4.82 × 2.62 | 1 | 0 | 0 | 0 | 0 / 0 | 0 | 0 | 0 | 5.20° | outward |
| MooncapGlowSpot | 48 | 1.40 × 1.40 × 1.29 | 1 | 0 | 0 | 0 | 0 / 0 | 0 | 0 | 0 | 27.8° | outward |
| MooncapStalkLarge | 160 | 2.37 × 2.43 × 3.42 | 1 | 0 | 0 | 0 | 0 / 0 | 0 | 0 | 0 | 34.6° | outward |
| MooncapStalkSmall | 112 | 1.49 × 1.51 × 2.43 | 1 | 0 | 0 | 0 | 0 / 0 | 0 | 0 | 0 | 43.3° | outward |
| MooncapLeafClump | 154 | 2.24 × 1.03 × 1.78 | 1 | 0 | 0 | 0 | 0 / 0 | 0 | 0 | 0 | 5.02° | outward |
| MooncapRockBase | 928 | 6.14 × 5.06 × 1.40 | 1 | 0 | 0 | 0 | 0 / 0 | 0 | 0 | 0 | 5.02° | outward |

- Origins at the bottom centre, transforms applied, no duplicate verts, flat shading, no custom normals. Pieces before
  union: big cap 196, small cap 168, stems 160 / 112, gems 48 each (+16 for a bezel), leaves 16, boulders ~50–60.
- **Pitfalls hit and fixed** (keep them in mind for later models):
  - Booleans at the display slot (x ≈ 540, y −320) made 236–675 self-intersecting pairs: the operands' float32
    matrices are off by ~1e-4 there. `_make` now moves the object to the origin before any boolean; `M.display` puts it
    back.
  - B1 / B2's flat bottoms were coplanar and overlapping at z −0.1: self-intersecting slivers after the first carve.
    Each boulder / pebble bottom now sits at its own depth (−0.1 − 0.013 i).
  - The gem shells were first pasted in the build frame, not the hero's mesh frame (0.1 low): most crowns ended inside
    the cap. `_append` applies `o.matrix_world⁻¹ @ cutter.matrix_world`.
  - Floor-cap needles (1.2°) on the ground: m023's floor re-fan (poke / beautify / split long edges) is in `_polish`.
  - Leaf hubs 0.03 apart left needles and 4 self-intersections at the clump feet: hubs 0.16 apart.
  - The Pc pebble didn't reach a boulder (a second shell): moved to (2.72, −0.55), Ø 0.6.

## Stage 3 — UV

Smart UV 45° re-unwrapped ANGLE_BASED per island, margin 0.008 (gap 0.016), `m012._uv_unfold` for folds.

| Object | Islands | Overlaps | Flipped | Min gap | Border | Density min / med / max | Conformal p95 |
| --- | --- | --- | --- | --- | --- | --- | --- |
| MooncapNode | 574 | 0 | 0 | 0.016 | 0.008 | 1.0 / 1.0 / 1.0 | 1.031 |
| MooncapShell | 53 | 0 | 0 | 0.016 | 0.008 | 1.0 / 1.0 / 1.0 | 1.030 |
| MooncapGlowSpot | 8 | 0 | 0 | 0.016 | 0.008 | 1.0 / 1.0 / 1.0 | 1.053 |
| MooncapStalkLarge | 14 | 0 | 0 | 0.016 | 0.008 | 1.0 / 1.0 / 1.0 | 1.037 |
| MooncapStalkSmall | 17 | 0 | 0 | 0.016 | 0.008 | 1.0 / 1.0 / 1.0 | 1.026 |
| MooncapLeafClump | 33 | 0 | 0 | 0.016 | 0.008 | 1.0 / 1.0 / 1.0 | 1.021 |
| MooncapRockBase | 182 | 0 | 0 | 0.016 | 0.008 | 1.0 / 1.0 / 1.0 | 1.001 |

## Stage 4 — Materials, colour and texture

**Pass 1** (`m030.calibrate()`, the kit's test dome, against §5.4's unshadowed targets; rendered / target sRGB):
cap `#584DA6` (103,86,192 / 106,88,194), cap_light `#725FBE` (138,109,222 / 140,112,220), cap_dark `#44396E`
(78,62,122 / 79,63,124), stem `#B5A388` (230,200,158 / 230,200,159), stem_base `#9C876A` (197,165,123 / 200,166,123),
leaf `#6A7C2D` (127,146,46 / 130,149,46), leaf_base `#576724`, leaf_tip `#7E8D34`, rock `#625450` (123,103,93 /
123,102,93), rock_light `#7C6F6E`, rock_dark `#483D39`, dirt `#564845`.

**Pass 2** (the hero's sheet views against the sheet's medians, linear-light gains): the caps were right (front
`#6658BB` against `#6356BD`) and kept. Stems ×(1.33, 1.22, 1.10) → `#CCB18F` / `#B0956E` (the big cap shades them
more than the sheet does); leaves ×1.5 → `#819630` / `#6A7D28` / `#98AA36` (they stand in the caps' and rocks' shade:
rear `#5C6D21` against `#818F22` before); rock family ×1.2 and warmer → rock `#6E5C55`, rock_light `#8A7973`,
rock_dark `#4F433E`, dirt `#5E4E4B`, and the dark ground band / contact paint halved (ROCK_GROUND (0.15, 0.35),
contact 25 %). Gem keys re-aimed for the rendered Neon preview (emission 1.0): spot `#74D6EC`, spot_light `#A9F0F5`,
spot_deep `#4DA2D0` (light 53 above mid in R, deep 52 below mid in G).

**Final re-measure** (study masks, ours with the floor hidden; median / lit / shade):

| View | Cap P ours vs sheet | Gem C | Stem T | Leaf G | Rock R |
| --- | --- | --- | --- | --- | --- |
| front | `#6657BA` / `#9277ED` / `#423676` vs `#6356BD` / `#8D75DF` / `#4A3B77` | `#74E6FF` vs `#73E7F8` | `#9A8465` / `#FAD3A2` vs `#C7A881` / `#EFD3AD` | `#434F12` vs `#4F5919` | `#7E685C` vs `#755F56` |
| f34 | `#6758BC` vs `#6859C0` | `#74E6FF` vs `#71E8F7` | `#A08768` vs `#C8A780` | `#424E11` vs `#525D17` | `#7C675C` vs `#77635B` |
| rear | `#52469A` vs `#604DA3` | `#74E6FF` vs `#7AEAFA` | `#CFB490` vs `#D6B891` | `#6B7E22` vs `#818F22` | `#6A5951` vs `#7A655A` |
| side | `#5D4DAD` vs `#5A489F` | | `#B59771` vs `#E6C79F` | `#4B5717` vs `#616B1F` | `#735F54` vs `#7B675F` |

- Caps within 3–14 of the sheet in every elevation view (crown light → flank → rim dark in every view); gems within
  7–17 (the Neon preview clips B to 255); rocks within 7–16; leaves 12–22 dark (shade); **the front / f34 / side stems
  read 30–45 darker in the median** (their lit quartile matches, `#FAD3A2` against `#EFD3AD`: the studio's key light
  leaves more of the big stem in the cap's shadow than the sheet does). Raising the stem key further would clip the lit
  faces; left as is and noted.
- **Blending** (positions only, never facing): caps by the lathe ring's height fraction u + broad noise + a ±0.10
  facet scatter on a 9-key ladder dark → cap → light (25 / 50 / 75 % steps): underside 25 % dark, rim band 50 % dark,
  u < 0.38 ramps toward dark, u > 0.62 toward light; stems: stem_base under the lowest 25 % blending over 0.15 (3 mixes);
  leaves base → mid → tip by t along the leaf (5 keys incl. 50 % mixes); rocks: noise patches → rock_light (mix up to
  75 %), a dark ground band, contact faces 25 % dark, pebbles dark; dirt with 25 % rock_dark patches near boulders.
  Hard edges only at gem | pocket (the cutter faces are cap_dark) and between materials.
- **Tint**: per piece tint_var 0.04; broad mottling amp 0.03 (caps, stems, leaves), 0.06 (rocks, dirt), scale ~0.5;
  gem keys Tint 1 (`_gem_tint`). Tint spread hero 1.18 (< 1.25). Baked-shading correlation (K.check): hero 0.39
  (< 0.5) — reached by painting the underside only 25 % dark (50 % gave 0.62).
- **Finish**: caps rough 0.70 / 0.75 dark, low spec; stems 0.85; leaves 0.75 low spec; rock 0.92, dirt 0.95; gems 0.4.
- **Gem tone split** (deep / mid / light, sheet in brackets): front .17 / .53 / .30 (.26 / .48 / .25), f34 .17 / .53 /
  .30 (.17 / .50 / .32), rear .23 / .51 / .26 (.26 / .41 / .33), side .19 / .54 / .27, top .17 / .54 / .29. The lower
  crown row alternates deep / mid by triangle; table r 0.28 d.

## Stage 5 — Lighting

- Neon keys `m030_spot`, `m030_spot_light`, `m030_spot_deep` at emission 1.0 (≥ the exporter's GLOW_EMISSION), one flat
  colour each, Tint 1, previewed unshaded (`_glow_mats`). All other keys emission 0. `build()` checks there are exactly 3.
- Gem bright share (v ≥ 0.85 of C pixels): front 0.953, f34 0.948, side 0.943, rear 0.924, r34 0.928, top 0.941
  (target ≥ 0.85 / top ≥ 0.75).
- Light: one `crystal_glow` socket (light only) at build (0.6, −2.7, 3.6), 0.91 from the nearest surface, outside the
  mesh; colour `#7FE9F8`, brightness 0.5, range 8, shadows true, no flicker. Spill, VFX on against off (sheet-view
  medians): front stem `#9A8465` / `#998061`, rock `#7E685C` / `#7E675B`; f34 stem `#A08768` / `#9F8465`, rock
  `#7C675C` / `#7C665A`; rear and side identical. Spill ≤ 4 levels (limit 10).
- **Studio (Requires Manual Validation):** check the three gem tones stay distinct under Neon bloom, and that the light
  reads in a dark cave without washing the cream stems cyan.

## Stage 6 — VFX

Only the `crystal_glow` light (decision 8): the sheet draws no halo, spores or sparkle. `fx_check`: inside False, spawn
box n/a (no emitters), clear 0.91, Roblox xyz (0.64, 3.6, 2.75). No harvest sockets (decision 9). Renders use vfx=True.

## Measured against the sheet (final)

Shares P / C / T / G / R in % (sheet in brackets), study masks, ground shadow excluded:

| View | P | C | T | G | R | C/(P+C) | W : H |
| --- | --- | --- | --- | --- | --- | --- | --- |
| front_sheet | 46.9 (49.1) | 7.1 (6.8) | 21.2 (20.5) | 3.1 (2.2) | 21.7 (21.5) | 13.2 (12.1) | 1.26 (1.291) |
| f34_sheet | 48.2 (49.3) | 7.6 (8.2) | 19.0 (18.8) | 2.7 (2.4) | 22.5 (21.3) | 13.6 (14.3) | 1.21 (1.37) |
| rear_sheet | 50.6 (46.4) | 3.8 (3.7) | 14.5 (16.9) | 9.0 (8.3) | 22.2 (24.8) | 6.9 (7.4) | 1.26 (1.243) |
| r34_sheet | 50.9 (48.1) | 4.1 (3.8) | 13.8 (16.1) | 8.1 (7.5) | 23.1 (24.4) | 7.5 (7.4) | 1.22 (1.23) |
| side_sheet (270) | 58.6 (46.8) | 7.4 (2.5) | 8.9 (25.4) | 2.4 (1.8) | 22.6 (23.6) | 11.2 (5.0) | 0.92 (1.005) |
| top (flipped) | 80.3 (72.2) | 13.8 (13.8) | 0.2 (0.5) | 0.5 (1.5) | 5.3 (11.9) | 14.6 (16.0) | |
| top_tilt (flipped) | 71.2 (72.2) | 12.8 (13.8) | 0.2 (0.5) | 0.1 (1.5) | 15.7 (11.9) | 15.2 (16.0) | |

- Front top profile mean / max error 0.020 / 0.11 (the 0.11 is the last column, the small cap's +X rim tip), f34
  0.022 / 0.06, rear 0.048 / 0.14, r34 0.064 / 0.17. Front width per height at h .1 / .3 / .5 / .7 / .9: .82 / .87 /
  .94 / .68 / .53 against .86 / .86 / .97 / .71 / .52.
- Big cap visible bottom edge per column matches the front within 0.04 (above); flat crown centred at about 0.67 of the
  cap width from the left (sheet 0.65); left rim the cap's lowest point.

## Modeller's notes for the verifier

1. **Rebuild**: `m030.build()` (about 45 s geometry + 23 s renders in the background session); problems list empty.
   `m030.measure()` re-runs the study's masks on the sheet and on our `*_sheet` renders (our top flipped).
2. **The side cell (side_sheet 270) does not match by shares** (P +11.8, T −16.5, C +4.9): with decision 4's −X-only
   droop the big cap's whole −X rim hangs low toward this camera, so the stem is hidden above h .45 and the −X flank's
   gems face it. §3.5 predicted this ("record it, don't chase it"); the sheet's side cell draws a back droop instead.
   S2 / S3 / S4 already lean toward the front camera to cut this (side C was 8.4).
3. **Size** is 7.36 × 5.58 × 5.35, inside the tolerances but wider and lower than the nominal 7.1 × 5.5 × 5.5, to meet
   the front W : H 1.22–1.36 (at the nominal size it is 1.17). The f34 W : H stays 1.21 (§3.1: compare it by shares).
4. **Top (kit top, flipped)**: P +8.1 and R −6.6 just outside ±6 (the ortho top hides the boulders under the caps);
   the top_tilt view is within ±4 everywhere. The sheet's top cell looks tilted.
5. **Rear**: P +4.2 (just over ±4), R −2.6, T −2.4; the studio leaves the rear rocks darker (`#6A5951` against
   `#7A655A`).
6. **Stems** read darker in the front / f34 / side medians (studio shadow under the big cap; lit quartile matches).
7. **Shell part** has 5 empty pockets, not 6 (S4 is a bezel gem by decision 5). The pockets are shallow recesses
   whose walls are deeper on the uphill side where a gem leans toward the camera (S2's wall reaches 0.24).
8. Bezel gems (S4, s3, s4, s5) sit on a dark collar ring of faces rather than painted cap faces.
9. The study's §2.3 lathe placements are replaced by sheet-camera rays (see stage 1); gem centres hit the sheet's
   front / rear (f, h) by construction.

## Stage 7 — Verification (round 1)

Independent verifier, 2026-10-29. Read-only: background Blender on port 9881 with `wip/M030_verify.blend` (not saved,
`build()` not called), fresh renders into the verifier's scratch folder (`kit_models.MODEL_RENDERS` redirected), the
study's masks (`m030.measure()` and the verifier's own numpy scripts) on both images.

**Result: PASS, 8 / 10.** No blockers. The leftovers below are minors.

### Re-measured geometry

| Object | Tris | Size | Shells | NM edges / verts | Boundary | Wire / loose | Zero-area | n-gons | Self-int. | Min corner | Inverted | Normals |
| --- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- |
| MooncapNode | 2880 / 4000 | 7.36 × 5.58 × 5.35 | 1 | 0 / 0 | 0 | 0 / 0 | 0 | 0 | 0 | 5.01° | 0 | outward |
| MooncapShell | 452 | 6.06 × 4.82 × 2.62 | 1 | 0 / 0 | 0 | 0 / 0 | 0 | 0 | 0 | 5.20° | 0 | outward |
| MooncapGlowSpot | 48 | 1.40 × 1.40 × 1.29 | 1 | 0 / 0 | 0 | 0 / 0 | 0 | 0 | 0 | 27.8° | 0 | outward |
| MooncapStalkLarge | 160 | 2.37 × 2.43 × 3.42 | 1 | 0 / 0 | 0 | 0 / 0 | 0 | 0 | 0 | 34.6° | 0 | outward |
| MooncapStalkSmall | 112 | 1.49 × 1.51 × 2.43 | 1 | 0 / 0 | 0 | 0 / 0 | 0 | 0 | 0 | 43.3° | 0 | outward |
| MooncapLeafClump | 154 | 2.24 × 1.03 × 1.78 | 1 | 0 / 0 | 0 | 0 / 0 | 0 | 0 | 0 | 5.02° | 0 | outward |
| MooncapRockBase | 928 / 1000 | 6.14 × 5.06 × 1.40 | 1 | 0 / 0 | 0 | 0 / 0 | 0 | 0 | 0 | 5.02° | 0 | outward |

- **Size** is inside the decided 7.1 ± 0.35 × 5.5 ± 0.4 × 5.5 ± 0.25 (W margin 0.09, H margin 0.10).
- **Interior faces:** none. A ray-parity test on every face found 3 tiny faces (area 0.003; two on the hero, one on
  the base) whose two sides both test "inside" at 3 mm. At 0.8 mm their front sides are outside, so they line 2.3 mm
  crevices (a boulder against the slab at (−2.0, 1.6, 0.04); a gem pavilion against its pocket at (1.56, −1.63, 3.30)).
  They are not enclosed faces.
- **Origin and transforms:** every object's origin is at its bbox bottom centre (offset 0, 0, 0), with rotation 0 and
  scale 1. There are no modifiers, no custom normals and no duplicate verts, and every face is flat shaded.
- **UVs:** the hero has 574 islands, 0 overlaps, 0 flipped, min gap 0.016, border 0.008, density 1.0 / 1.0 / 1.0 and
  conformal p95 1.031. The parts are the same (p95 1.001–1.053).
- **Materials:** `K.check` is clean (all flintkit keys).
  - The Neon keys `m030_spot #74D6EC`, `m030_spot_light #A9F0F5` and `m030_spot_deep #4DA2D0` are at emission 1.0
    with no Tint node. All 489 gem faces have Tint 1 (0 loops off).
  - Every other key is at emission 0.
  - Baked-shading correlation: hero 0.39 (< 0.5), shell 0.17, clump 0.30, the rest 0. Tint spread 1.18.
- **Socket:** one `crystal_glow`, light only (`#7FE9F8`, 0.5, range 8, shadows, no flicker).
  - It sits at build (0.6, −2.7, 3.6), outside the mesh, 0.91 from the nearest surface.
  - Spill, VFX on against off: front stem `#9A8465` / `#998061`, front rock `#7E685C` / `#7D675B`, f34 stem `#A08768`
    / `#9F8465`; the side and rear are identical. At most 4 levels (limit 10).

### Shape against the sheet

- **Caps:** two thick faceted violet caps with a real underside and rim band.
  - The big cap's crown is level: a plane fitted over its top 0.3 is tilted 1.2°. Its top verts run X −0.97 … +0.98
    around the big stem's axis (−0.20, 0.35). The −X rim goes down to z 1.8 and the +X rim sits at 3.1–3.3. That is an
    eccentric droop, not a rigid tilt.
  - Top profile mean / max error: front 0.020 / 0.11 (only the small cap's +X rim tip, .34 against .45), f34
    0.022 / 0.06.
- **Gems:** 11 separate gem islands.
  - Pocketed, each surrounded only by `cap_dark` wall faces: Ø 1.38, 1.17, 1.13, 0.85, 0.75, 0.70, 0.62.
  - Bezel, a dark collar plus cap faces: Ø 0.53, 0.46, 0.43, 0.30.
  - Glow share and bright share:

| View | C ours (sheet) | C/(P+C) | Bright v ≥ 0.85 | Deep / mid / light ours (sheet) |
| --- | --- | --- | --- | --- |
| front | 7.1 (6.8) | 13.2 (12.1) | 0.953 (0.896) | .17 / .53 / .30 (.26 / .48 / .25) |
| f34 | 7.6 (8.2) | 13.6 (14.3) | 0.948 | .17 / .53 / .30 (.17 / .50 / .32) |
| rear | 3.8 (3.7) | 6.9 (7.4) | 0.924 | .23 / .51 / .26 (.26 / .41 / .33) |
| r34 | 4.1 (3.8) | 7.5 (7.4) | 0.929 | .24 / .50 / .26 (.20 / .45 / .35) |
| side | 7.4 (2.5) | 11.2 (5.0) | 0.943 | (side: decided, see minor 1) |
| top (flipped) / top_tilt | 13.8 / 12.8 (13.8) | 14.7 / 15.2 (16.0) | 0.94 | |

- **Stems:** fat faceted pears with the big axis at (−0.20, 0.35) and the small at (1.85, −1.35), as decided. Front
  width per height at h .1 / .3 / .5 / .7 / .9: .82 / .87 / .94 / .68 / .53, against the sheet's .86 / .86 / .97 / .71
  / .52.
- **Shares** (error in points, P / C / T / G / R):
  - front −2.2 / +0.3 / +0.7 / +0.9 / +0.2;
  - f34 −1.1 / −0.6 / +0.2 / +0.3 / +1.2;
  - rear +4.1 / +0.1 / −2.4 / +0.7 / −2.6;
  - r34 +2.8 / +0.3 / −2.3 / +0.6 / −1.3;
  - top_tilt −1.0 / −1.0 / −0.3 / −1.4 / +3.8.
- **Boulder ring and leaves:**
  - In the front, side and rear, the rock band is 95–98 % rock at h .0–.1 and 77–82 % at h .1–.2.
  - Two leaf clumps stand at the back (rear G 9.0 against 8.3). Their lance leaves with midribs match the exploded
    clump.

### Colours (study masks; sheet → ours, difference in sRGB levels)

| Region | front | f34 | rear | side |
| --- | --- | --- | --- | --- |
| Cap light (top 30 % of cap rows) | `#866DDB` → `#836FDF` (−3,+2,+4) | `#8C70DD` → `#9275E8` (+6,+5,+11) | `#846ADA` → `#7F67D0` (−5,−3,−10) | `#7C63CD` → `#8E72E6` (+18,+15,+25) |
| Cap mid (30–70 %) | `#5E4FAC` → `#6D5EBF` (+15,+15,+19) | `#6554BB` → `#6C5EC1` (+7,+10,+6) | `#584A9E` → `#5448A6` (−4,−2,+8) | `#463665` → `#6555AE` (geometry, see minor 1) |
| Cap dark (bottom 30 %) | `#58468F` → `#53458F` (−5,−1,0) | `#59489B` → `#53458F` (−6,−3,−12) | `#4A3B5C` → `#483D84` (−2,+2,+40) | `#4B3B6A` → `#50448F` (+5,+9,+37) |
| Gem deep | `#56ACDF` → `#5AAADF` (+4,−2,0) | `#44AAD9` → `#59AADF` (+21,0,+6) | `#64B8E8` → `#50A9DF` (−20,−15,−9) | `#6FB9EC` → `#53AADF` (−28,−15,−13) |
| Gem mid | `#6CE7F8` → `#74E6FF` (+8,−1,+7) | `#69E5F5` → `#74E6FF` (+11,+1,+10) | `#6FE9F9` → `#74E6FF` (+5,−3,+6) | `#79E8FA` → `#74E6FF` (−5,−2,+5) |
| Gem light | `#AFFBFE` → `#B1FFFF` (+2,+4,+1) | `#ADFBFD` → `#B1FFFF` (+4,+4,+2) | `#B0FBFD` → `#B1FFFF` (+1,+4,+2) | `#AAF8FC` → `#B1FFFF` (+7,+7,+3) |
| Stem (all) | `#C7A881` → `#9A8465` (−45,−36,−28) | `#C8A780` → `#A08768` (−40,−32,−24) | `#D6B891` → `#CFB490` (−7,−4,−1) | `#E6C79F` → `#B59771` (−49,−48,−46) |
| Stem upper / lower half | `#C2A47F` → `#7A6E56` (−72) / `#CBAB83` → `#D0B085` (+5) | `#C0A27D` → `#7D7057` (−67) / `#CFAE85` → `#CFAC83` (−2) | `#C7AC8B` → `#DABB94` (+19) / `#E0C097` → `#A28868` (−62) | |
| Rock | `#755F56` → `#7E685C` (+9,+9,+6) | `#77635B` → `#7C675C` (+5,+4,+1) | `#7A655A` → `#6A5951` (−16,−12,−9) | `#7B675F` → `#735F54` (−8,−8,−11) |
| Leaf | `#4F5918` → `#434F12` (−12,−10,−6) | `#525D17` → `#424E12` (−16,−15,−5) | `#818F22` → `#6B7E22` (−22,−17,0) | `#616B1F` → `#4B5717` (−22,−20,−8) |

- In the front, f34 and rear, the caps, gems and rocks match within 4–21 levels, and the caps blend crown → flank → rim
  in every view.
- The gem tones stay distinct: light is at least 60 above mid in R, and deep at least 60 below mid in G.

### Items

No blockers.

Minors (record them; chase them only if the main session wants a round 2):
1. **The side cell (side_sheet 270) does not match:** P +11.8, C +4.9, T −16.5, top profile max 0.21, and the cap mid
   reads `#6555AE` against the sheet's shaded underside `#463665`. This follows from decision 4 (droop along X only),
   as §3.5 predicted, and is accepted by that decision.
2. **The big stem's upper half reads dark khaki in the front and f34:** `#7A6E56` against `#C2A47F` (−67…−72), so the
   stem medians are 40–49 levels dark in the front, f34 and side.
   - The lower half matches within 5 and the rear stem within 7, so the key is right. The darkening is the drooping
     cap's shadow in the studio, and Roblox's sun will also shade the stem.
   - Requires Manual Validation in Studio. If the main session wants it lighter, the only rule-safe lever is a small
     lift of `m030_stem`: the lit quartile is already `#FAD3A2` against `#EFD3AD`, so about +5 % at most.
3. **The rear and r34 top profiles exceed ±0.06 at the ends** (rear max 0.14, r34 max 0.17), though the shares stay
   within ±4.1.
   - From behind, the small cap stands about 0.13 h higher at screen left (r34 f .05–.15: .62 / .69 / .76 against
     .49 / .55 / .59).
   - The big cap's −X rim falls lower at screen right (.59 / .44 against .71 / .53), so from behind the big cap reads
     more wedge-like than the sheet's rounder dome.
4. **The rear views are darker.** The keys themselves match; this is the studio's back lighting.
   - Rear lit quartiles: rock `#746159` against `#A08C86`, leaves `#798F26` against `#AAB829`.
   - The cap's shaded rim in the rear and side is bluer (B +37…+40) than the sheet's greyer `#4A3B5C`.
   - The leaves read 12–22 levels dark in every view.
5. **Top (ortho, flipped):** P +8.1 and R −6.6, outside ±6. Every gem shows (about 6 on the big cap and 5 on the
   small), against the sheet's 3–5 / 2–4. The sheet's top cell is tilted, and the tilted top_tilt is within ±4 on
   every share.
6. **Front ground line:** the bottom row of the front silhouette is 0.40 W wide against the sheet's 0.13, because our
   front boulders sit in a straighter line on the ground than the sheet's curved ring. From h .1 up, the width per
   height is within 0.04.
7. **S1's pocket** shows a wide dark crescent on its uphill side (a wall of up to about 0.24, modeller note 7), where
   the sheet shows a thinner dark ring. The tables stand roughly 0.1–0.3 proud of the mean cap surface around them
   (the study asked for 0.08–0.12 × Ø). This is a rough measure on the curved dome.
8. **The `MooncapGlowSpot` part** reads as a pointed brilliant-cut diamond (a pavilion cone of 0.62 d), where the
   sheet's loose Spot Insert is a blunter, rounder nugget. In the hero it is hidden inside the cap.
9. **The front's deep gem tone is a little under-represented** (.17 against .26), and its shaded deep quartile is
   lighter (`#68C4EC` against `#48AADE`). The f34 split matches.
