# 039 Rock Spire — spec

Reference: `art/blender/assets/references/039.png` (1024 × 1536 px). The sheet's title is "ROCK SPIRE" with the
subtitle "Angular stone spire with broad foot.", "PAGE 38/132" at the bottom right and "FLINTBORN — INDIVIDUAL MODEL
STUDY" in the footer. INDEX.md row 39 calls it "Flintborn rock spire model study".
Builder: `art/blender/kit/mcp/m039.py` → `build()` (not written yet). Procedure: `art/blender/kit/mcp/STAGES.md`. One
modeller does stages 1–6 in a background Blender, then a fresh verifier does stage 7; the main session then puts the
model into the kit file, exports and commits.

User direction for every model: shapes must match the sheet; colours "need to match the master reference and blend
into the colors nearby. please ensure all color and textures are being made and applied." Effects ship wherever the
sheet shows them. **This sheet shows no effect** (§7).

Sheet text:
- **Header (top right):** "A stylized, low-poly rock formation with a tall, angular spire and surrounding base rocks
  and foliage. Chunky, readable shapes with broad flat-shaded faces."
- **View labels:** "FRONT THREE-QUARTER", "REAR THREE-QUARTER", "ORTHOGRAPHIC VIEWS (Assembled)": "FRONT", "SIDE
  (RIGHT)", "REAR", "TOP".
- **Exploded:** "EXPLODED CONSTRUCTION (Reusabled Parts)" [sic]: "Rock Spire (main mesh)", "Foliage Cluster
  (reusable)", "Side Rock (reusable)", "Foot Rock (base, front)", "Small Rock (reusable)". Dashed drop lines put each
  foliage cluster onto a rock top and the spire onto the foot of the group.
- **Close-ups:**
  - "PART CLOSE-UP: ROCK SPIRE": "Broad, angular faces with clean flat shading."
  - "UNDERSIDE VIEW (Base Rock)": "Flat underside for ground placement (simple geometry)."
  - "JUNCTION DETAIL": "Rocks meet with simple interlocking planes. Foliage placed in crevices (separate mesh)."
- **Material palette:** "Main Rock / Pale warm gray (faceted)", "Rock Shadow / Cool gray", "Rock Highlight / Warm
  beige", "Foliage Dark / Olive green", "Foliage Mid / Leaf green", "Foliage Light / Yellow green".
- **Modeling notes:**
  - "Keep forms chunky and readable."
  - "Use broad, flat-shaded faces (low-poly, no noise)."
  - "Build from reusable rock and foliage parts."
  - "Maintain clean silhouettes and consistent geometry across all views."
  - "Foliage is a separate mesh (not baked into rock geometry)."
  - "Simple, solid colors; no photo textures." (but see §3.9)
- **Game context:** a landmark rock formation. The old kit sheet **W01 already has a Rock Spire row** (passed round 5 at
  7.5/10, exported to `art/roblox/kit/W01/`) and owns `RockSpire` (15.2 W × 11.6 D × 13.0 H, 3448 tris), `RockSpireMain`
  (6.4 × 5.6 × 11.6), `RockSpireFootCollar`, `RockSpireShort`, `RockSpireTall`, `RockSpireLeaning` (§8). Its goals file
  `art/blender/renders/kit/W01/rock_spire_goals.md` records five verifier rounds: greens too dark, "shoulders as round
  boulders, slim spire", a collar that didn't read as a ring, clover clumps chunkier than the master's rosettes, and a
  spire moss streak. W01's builder (`art/blender/kit/mcp/w01.py`, `spire_main`, `SPIRE` rings, `spire_pillars`) is a
  useful reference, but this sheet is a different composition: one spire, two leaning side rocks, one big foot rock in
  front, a ring of medium and small rocks and star-rosette clusters, **no collar**.

**Pixel boxes and masks.** All boxes are sheet pixels `(x0, y0, x1, y1)`, origin top left. Paper `#FBF7EF` (251, 247,
239), tolerance 12. Masks are `cls()` in `m.py` (HSV):
- **R, rock:** hue ≤ 45° or ≥ 190°, sat 0.03–0.42, v ≥ 0.30, and not G/B/T. Lit faces warm peach (hue 18–28°), shaded
  faces cool lavender-grey (hue 260–345°, B ≥ R > G); both are R (f34: 78 % warm, 21 % lavender).
- **G, green:** hue 45–150°, sat ≥ 0.28, v ≥ 0.12 (leaves, buds and the faint moss stains).
- **B, ground shadow:** neutral (sat < 0.05, v 0.55–0.955) or blue-grey with B > R + 4 and G ≥ R (`#999FAC`, hue 221°).
  **Background** in every silhouette and share. (It also swallows a little of the r34's far-left rock, whose shaded
  face is bluish; < 1 % of that cell.)
- **T, text and dark crevices:** v < 0.32, sat < 0.25. In silhouettes, not in shares.
- **O, other:** outlines and anti-aliasing (3.8–6.3 % of the silhouettes).
- Cells: f34 (100,30,565,438) with the title, subtitle and the header rule at y 71–74 blanked; r34 (565,75,955,438);
  front (12,515,272,720); side (276,515,511,720); rear (516,515,762,720); top (766,515,1012,720); exploded
  (12,790,616,1318); close-ups spire (626,790,1013,946), underside (626,987,1013,1136), junction (626,1180,1013,1318).
  Swatches 46 × 48 px at x 36 / 130 / 226 / 329 / 418 / 508, y 1366–1414.

**Scratch study material** (no Blender), in
`C:\Users\Orang\AppData\Local\Temp\claude\D--Projects-Roblox-RBLX-Flintborn\3f83a1be-3b3d-4e4b-ae5a-7b04dbb75bdc\scratchpad\m039_study\`.
Run with the scratch venv `..\venv22\Scripts\python.exe` (Python 3.14, Pillow, numpy; `m.py` has its own `label()`).
- **Helpers:** `m.py` (masks `cls()`/`cellcls()`, boxes `V`/`X`, swatches `SW`, `label()`, `preview()`), `zoom.py`,
  `lines.py`, `prev.py` (mask previews `cls_*.png`).
- **Measurements:** `measure.py` → `measure_out.txt`, `bb.json` (silhouettes, shares, top/bottom profiles, width per
  height, green per fifth); `comps.py` (rock and green components); `parts.py` → `parts.json` (per-part outlines);
  `facets.py` → `facets_out.txt`, `facets.json`, `facets_*.png` (flat-facet segmentation, M035/M038 method).
- **Colour:** `samp.py` → `samp_out.txt` (swatches; median / lit / shade quartiles per cell, per rock, per third;
  green and rock deciles).
- **Zooms:** `z_f34.png`, `z_r34.png`, `z_row2.png`, `z_front.png`, `z_top.png`, `z_expl.png`, `z_expl_spire.png`,
  `z_expl_sides.png`, `z_expl_base.png`, `z_cu.png`, `z_clusterA.png`, `z_f34_left.png`, `z_f34_right.png`, `z_pal.png`.
- **To run the scripts on our renders:** point `R` in `m.py` at the render, set `P` to its background, set the `V`/`X`
  boxes to the render cells (and the part boxes in `parts.py` / `facets.py`), and re-run.

## 1. Study (2a)

### 1.1 Classification, what it is, size

- **Classification:** full asset (a landmark rock formation with foliage). Hero budget 4000 tris, each part under
  1000. The plan in §4.3 lands at about 2600–3100.
- **Overall read (check this first).** A **tall angular warm-grey obelisk** standing at the back centre-right, its
  lower flanks wrapped by a **broad foot** of rocks:
  - **the Spire** (S): a long tapering 6–7-sided obelisk, about 2.5× taller than anything else, with a short
    pyramid cap; huge flat faces, a lavender left flank and a peach right flank;
  - **a tall Pillar** (P, a "Side Rock") leaning against the spire's lower-left flank, flat-topped, reaching 0.7 of the
    spire's height;
  - **a shorter Side Rock** (Rr) against the spire's lower-right flank, a tapered flat-topped block reaching about
    half the spire's height;
  - **the Foot Rock** (F): a big chunky faceted dome in front, flat top, a pointed front "nose" vertex where five big
    faces meet; the largest rock by screen area;
  - **a ring of medium rocks** (BL back-left, FL front-left, FR far right) and **small rocks** (s1, s2, s3) along the
    front;
  - **lime-green star rosettes** (Foliage Cluster: 6–7 broad oval leaves round a round lime bud) tucked in every
    crevice, on rock tops against the spire, and climbing the spire's right flank above Rr.
  - Hero shares (f34): rock 77.3 %, green 22.7 %; green by height fifths (bottom → top) 24.5 / 34.9 / 13.9 / 15.2 /
    0.7 %. The top fifth (the spire's upper shaft and cap) is bare stone.
- **Focal silhouettes, in order:**
  1. The spire's tall narrow peak: the only thing above h .72; the top profile rises from .30 at f .15 to 1.0 at f
     .55 and falls to .32 at f .85 (§1.2).
  2. The stepped shoulders: the pillar's flat top at h .72 left of the spire, Rr's flat top at h .52 right of it.
  3. The broad foot: the silhouette's width per height is 0.97 at h .15 and halves by h .45 (a wide pyramid of rock).
  4. The foot rock's big faceted front with its nose vertex, and the lime rosettes in the crevices.
- **Target size: 14.0 W × 10.5 D × 11.0 H studs** (spire tip 11.0 = 2.0 × the 5.5-stud character). Tolerances W ±0.6,
  D ±0.8, H ±0.3. Decision §8.1.
  - **How it was derived.** The sheet has no character. The f34 and the front cell are one drawing (§3.1). With the
    camera at e ≈ 20° and the layout of §2.1, the f34's tops and bottoms are reproduced within 0.02 H: **f34 31.5
    px/stud, front cell 15.6 px/stud**.
  - **Why this size.** A landmark you see from across a clearing: the spire two characters tall, the pillar 1.4, Rr
    0.9 (shoulder height), the foot rock 0.67 (chest height), medium rocks 2.1–2.9 (waist), small rocks 0.75–1.2
    (knee). At this size the leaves are 0.6–0.85 long and the rosettes 1.2–2.2 across, readable next to a character. It
    stays a size class under W01's 13.0-tall spire, so the two read as different kit pieces.
- **Build frame:** front −Y, +X right, ground z 0. Stage 2 re-centres the hero on its bbox bottom centre.

### 1.2 Measured views (`measure.py`)

| View (box) | Silhouette bbox (px) | W : H | Rock R | Green G | O+T of silhouette | Rocks visible | Green groups |
| --- | --- | --- | --- | --- | --- | --- | --- |
| Front three-quarter (100,30,565,438) | 107–552 × 41–432 (446 × 392) | **1.138** | 77.3 % | 22.7 % | 4.8 % | 10 | 6 (≈ 14 rosettes) |
| Rear three-quarter (565,75,955,438) | 604–934 × 81–425 (331 × 345) | 0.959 | 80.4 % | 19.6 % | 4.0 % | 8 | 6 |
| Front (12,515,272,720) | 36–253 × 520–716 (218 × 197) | **1.107** | 76.8 % | 23.2 % | 4.5 % | 10 | 6 |
| Side (276,515,511,720) | 308–477 × 521–716 (170 × 196) | 0.867 | 80.9 % | 19.1 % | 3.8 % | 7 | 5 |
| Rear (516,515,762,720) | 544–732 × 521–715 (189 × 195) | 0.969 | 76.8 % | 23.2 % | 3.9 % | 8 | 6 |
| Top (766,515,1012,720) | 802–978 × 534–706 (177 × 173) | 1.023 (W : D) | 67.9 % | 32.1 % | 6.3 % | 6 | 5 |

- Shares are of R + G; the ground shadow is background. **Verifier tolerance:** shares ±4 points; W : H ±0.06;
  positions ±0.04 of W/H unless stated.

**Top profiles** (highest silhouette pixel per column as a fraction of H, every 0.05 f):

| f | .00 | .05 | .10 | .15 | .20 | .25 | .30 | .35 | .40 | .45 | .50 | .55 | .60 | .65 | .70 | .75 | .80 | .85 | .90 | .95 | 1.0 |
| --- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- |
| f34 | .17 | .21 | .29 | .30 | .33 | .42 | .51 | .68 | .76 | .81 | .93 | .99 | .96 | .91 | .70 | .66 | .58 | .32 | .31 | .28 | .16 |
| Front | .13 | .20 | .27 | .27 | .35 | .43 | .62 | .72 | .78 | .90 | .97 | .98 | .92 | .78 | .66 | .58 | .41 | .26 | .25 | .22 | .12 |
| r34 | .16 | .27 | .24 | .32 | .43 | .59 | .61 | .72 | .88 | .97 | 1.0 | .95 | .84 | .75 | .65 | .42 | .34 | .33 | .31 | .26 | .12 |
| Side | .15 | .18 | .22 | .31 | .40 | .55 | .58 | .65 | .85 | .97 | 1.0 | .96 | .92 | .74 | .70 | .45 | .31 | .27 | .25 | .21 | .09 |
| Rear | .11 | .17 | .19 | .31 | .44 | .58 | .65 | .75 | .92 | .96 | 1.0 | .95 | .85 | .67 | .63 | .56 | .34 | .26 | .24 | .18 | .09 |
| Top (h = back) | .58 | .72 | .74 | .74 | .76 | .91 | .93 | .98 | .99 | .94 | .95 | .93 | .83 | .77 | .71 | .77 | .80 | .80 | .80 | .76 | .66 |

- f34 reading: f .00–.25 the left foot (C1, BL, C2, .17–.42); f .30–.45 the pillar's shoulder and flat top (.51–.81,
  the pillar top itself .72 with C4 above it to .81); f .45–.65 the spire (.93–.99, tip at f .55); f .70–.80 Rr's top
  and the C10 rosettes (.58–.70); f .85–1.0 FR (.28–.32).

**Bottom profiles** (lowest silhouette pixel; ground contacts):

```
f34    .16 .09 .09 .05 .03 .02 .02 .04 .02 .01 .00 .00 .02 .01 .01 .02 .04 .04 .09 .09 .13
front  .11 .07 .05 .04 .03 .02 .02 .02 .02 .01 .01 .01 .01 .00 .01 .02 .03 .03 .05 .06 .08
```

- A shallow V: the foot rock (f .33–.68) is the front-most piece; the ends rise to .09–.16 (pieces set further back).

**Width per height** (silhouette width at h .05 → .95 as a fraction of W):

```
f34    .72 .97 .88 .63 .53 .47 .42 .29 .18 .11
front  .83 .97 .81 .60 .53 .49 .39 .29 .18 .10
r34    .78 .98 .91 .61 .53 .47 .36 .28 .20 .12
side   .94 .96 .77 .58 .52 .46 .35 .26 .21 .13
rear   .88 .92 .75 .60 .55 .50 .38 .26 .21 .12
```

- The step from .88 to .63 between h .25 and .35 is the top of the broad foot (foot rock, BL, FR); .53–.42 at h .45–.65 is
  pillar + spire + Rr; above h .75 the spire alone (.29 → .11).

**Green groups (f34, leaves dilated 2 px; f across, h up):** f .00–.15 h .09–.24 (C1, 10.2 % of green); f .19–.35 h
.17–.42 (C2, 15.8 %); f .38–.46 h .33–.44 (C3, 5.2 %); f .39–.49 h .71–.81 (C4 on the pillar top, 5.0 %); f .50–.95 h
.01–.44 (C5–C9 merged, 48.6 %); f .69–.80 h .48–.70 (C10 on Rr and the spire flank, 13.5 %). The front cell gives the
same six groups within 0.04 (7.7 / 14.8 / 5.4 / 4.8 / 52.3 / 13.7 %).

### 1.3 Silhouette and composition per view

**Front three-quarter (the hero, governs; `z_f34.png`, `z_f34_left.png`, `z_f34_right.png`).** An elevated **front**
view (az 0, e ≈ 20°, §3.1), not a rotated three-quarter.
- **Spire (S):** tip at f .56 h 1.0 (sheet x 357, y 41); a 3–4-face pyramid cap from y 41 to about 75 (h .91–1.0);
  then a slowly tapering shaft: visible width 44 px at y 60, 66 at y 75, 84 at y 105, 93 at y 150 (0.21 W, h .72); the
  right flank runs 399 → 417 between y 90 and 165 and is then vertical to y 240, where Rr covers it; the left flank is
  hidden by the pillar below y 150. The left flank is one huge lavender face, the right flank 2–3 long peach faces; a
  long vertical ridge between them.
- **Pillar (P):** f .27–.55, flat top at h .72 (y 150), the top face 2.1 studs across (x 267–335) sloping a little to
  the front; tall, broad, slightly tapering flat front faces; its right edge overlaps the spire's left flank (P stands
  in front); its foot hidden by C2, BL and the foot rock. A faint olive stain on its lower-left face (§5.3).
- **Side Rock (Rr):** f .67–.85, flat top at h .52 (y 228), top face f .69–.80; a tapered block (narrow top, wide base),
  its left side pressed into the spire's right flank; a two-rosette stack (C10) on its top climbs the spire flank to
  h .70.
- **Foot Rock (F):** f .33–.68, top at h .36 (y 292), bottom at h 0 (the front-most rock); a broad flat top facet, a
  pointed front "nose" vertex where 5 big triangular faces meet, steep big front faces; clusters C3 and C5 on its back
  top edge against the pillar and the spire.
- **Medium rocks:** BL f .07–.24, top h .34 (a blocky flat-topped rock); FL f .12–.32, top h .23, bottom h .04 (a
  rounded faceted rock, flat top facet); FR f .85–1.0, top h .31, bottom h .11 (a chunky wedge-topped rock).
- **Small rocks:** s1 f .25–.32, top h .08 (front of FL/F, 1.05 wide); s2 f .66–.76, top h .10 (front right of F); s3 f
  .75–.88, top h .15.
- **Plants:** about 14 rosettes in 6 groups (§1.2), every one in a crevice or on a rock top against a taller rock; no
  rosette stands alone in the open.
- **Ground shadow:** soft blue-grey to the left and behind (light from the front-right); background.

**Front (`z_front.png`).** The f34 drawing again, at a slightly lower elevation (§3.1): every rock's X fraction within
0.04 (spire tip f .52, pillar .23–.50, Rr .65–.83, foot .29–.66, BL .06–.20, FL .09–.29, FR .83–1.0); tops pillar .70, Rr
.49, foot .35, BL .29, FL .20, FR .26. Same six green groups.

**Rear three-quarter (`z_r34.png`).** **Not a rear view**: the pillar is still on the left and the foot rock still in
front, shifted right of the spire (foot centre f .56 vs tip f .49; in the f34 f .50 vs .56). That is a camera moved to
the **front-left, az ≈ −30°**, e ≈ 20 (§3.2). The rosette stack on Rr shows here as a lime patch on the spire's right
flank at f .60–.70, h .56–.75; the spire is relatively wider (92 px = 0.28 W at h .72).

**Side (right) and Rear (`z_row2.png`).** Both show the same arrangement again (pillar left, foot rock front centre,
spire behind, a small rock low at the right). They are **front redraws**, narrower (W : H 0.867 and 0.969) (§3.3).
The side cell's lime patch high on the spire's right flank (f .58–.71, h .55–.73) matches the r34's.

**Top (`z_top.png`; image top = back).** A **re-composition** (§3.4): a big faceted mass in the centre (0.52 W across;
our spire's footprint is about 0.31 W), a big foliage mound behind it (f .00–.65, h .48–.99, 46 % of the green), a
medium rock at the back right (f .71–1.0, h .51–.80), a rock left (f .04–.24), a rock front centre-right (f .43–.68,
h .03–.26), a rock right-middle (f .77–.93) and a small one front-left; rosettes ring everything. W : D 1.02.

**Close-ups (`z_cu.png`).**
- **Part close-up: Rock Spire** (686,791,860,945): the cap and upper shaft. 4 flat regions (threshold 7): the left
  shaded cap face 0.33 and the right lit cap face 0.32 of the visible stone, meeting at a sharp ridge; the apex at f
  .45 (a hair left of centre); 2 thin bevel faces at the cap's base. Width per height (h .05 → .95) .97 .91 .85 .79 .73
  .67 .61 .48 .29 .10: a straight taper, then the cap.
- **Underside view (Base Rock)** (643,987,861,1129): the foot rock from below: one big flat floor face (0.54–0.56 of
  the visible stone, `facets.py`) inside a ring of 8–10 rim faces; screen w/h 1.54.
- **Junction detail** (626,1180,1013,1318): two big rock faces (each a few large planes) meeting at a narrow crevice
  with 3–4 rosettes strung along it; the rosettes sit in the gap and touch both faces without cutting them.

### 1.4 Parts (Exploded Construction (12,790,616,1318), `z_expl*.png`)

Scale: the exploded parts are not drawn to the hero's scale (spire / foot width 0.70 in the exploded and 0.78 in the
f34; spire / foot height 1.57 and about 2.1; pillar w/h 0.79 and about 0.51). **The hero governs every size** (§3.5);
the exploded gives shapes and facet character.

| Part (exploded box, px) | Size px | Screen w/h | Width per height (h .05 → .95) | Widest at | Facet regions thr 5 / 7 (largest share) |
| --- | --- | --- | --- | --- | --- |
| Rock Spire (253,800,381,1027) | 128 × 227 | 0.56 | .38 .92 .97 .88 .80 .72 .62 .52 .42 .20 | h .19 | 12 (.235) / 8 (.285) |
| Pillar, unlabelled Side Rock (162,1009,255,1127) | 93 × 118 | 0.79 | .51 .89 .96 .92 .86 .82 .76 .70 .63 .40 | h .26 | 13 (.218) / 9 (.284) |
| Side Rock (404,971,491,1090) | 87 × 119 | 0.73 | .38 .70 .78 .82 .91 .76 .74 .75 .66 .39 | h .47 | 15 (.074) / 14 (.148) |
| Foot Rock (232,1125,416,1270) | 184 × 145 | 1.27 | .27 .73 .98 1.0 .95 .92 .93 .95 .90 .70 | h .61 | 15 (.112) / 16 (.204) |
| Medium dome, unlabelled (343,1083,466,1192) | 122 × 109 | 1.12 | (merged with the foot rock in the mask; by eye a rounded faceted dome, flat-ish top) | — | — |
| Small L (120,1145,183,1201) | 64 × 57 | 1.12 | .48 .89 .98 1.0 .95 .89 .81 .73 .56 .29 | h .35 | 12 (.096) / 9 (.112) |
| Small behind-left (183,1187,227,1233) | 45 × 47 | 0.96 | .36 .73 .86 .95 1.0 .98 .93 .91 .48 .45 | h .49 | — |
| Small R (471,1170,529,1229) | 59 × 60 | 0.98 | .57 .83 .93 1.0 .98 .95 .84 .74 .59 .31 | h .41 | 13 (.048) / 13 (.057) |
| Small front-right "Small Rock" (398,1236,458,1287) | 61 × 52 | 1.18 | .52 .83 .95 .98 .97 .92 .83 .75 .65 .32 | h .32 | 11 (.111) / 10 (.122) |
| Hero upper spire (318,42,420,225) | — | — | — | — | 14 (.118) / 9 (.249) |
| Hero foot rock (252,292,412,432) | — | — | — | — | 17 (.117) / 13 (.180) |
| Spire close-up / underside close-up | — | 1.13 / 1.54 | — | — | 7 (.313) / 4 (.332); 9 (.536) / 8 (.556) |

- The exploded drops 8 foliage clusters (one onto each rock top: pillar, spire foot, Side Rock, the dome, two small
  rocks, the foot rock's back) plus three sprigs already on the foot rock's top and its left crevice. Ten rocks: spire,
  pillar, side rock, foot rock, the medium dome behind-right of the foot rock, a small rock behind-left of it, and four
  small rocks. That matches the ten rocks of the f34 (§2.1, §3.5).

#### Rock Spire (main mesh) — exploded (253,800,381,1027); close-up; `z_expl_spire.png`, `facets_eSpire.png`

- **Shape:** a long obelisk, **6–7-sided** in plan (irregular; one vertex points to the front so a vertical ridge runs
  from the cap to the floor), tapering steadily from a foot ring at h .15 (widest) to about 0.44 of that width at h .90,
  then a **short pyramid cap** (h .90–1.0) of 3–4 faces with a sharp apex a little left of centre. Below the widest
  ring the faces tuck in 10–15 % to a flat floor (0.85–0.90 of the max width).
- **Facets:** few and very large: one long left face (0.24–0.29 of the visible area in the exploded), two or three
  long right faces, one or two **diamond facets** low on the front (a vertex pushed in at h .3–.5 so one long face
  splits into a diamond and two slivers), the cap's two big faces. 10–14 faces visible from one side; 8–12 regions at
  threshold 5–7. Never a ring of small triangles.
- **Hero size: 4.4 W × 3.8 D × 11.0 H** (base w/h 0.40; the exploded's 0.56 is drawn fat, §3.5). Width ratios (true,
  of the max width): h 0 → 0.88, .15 → 1.0, .45 → 0.84, .75 → 0.64, .80 → 0.60, .90 → 0.44 (cap base), 1.0 → apex.
  Checked against the f34's visible widths (2.62 studs at z ≈ 8.8, 2.06 at z ≈ 9.8, 1.37 at z ≈ 10.3).
- **Construction:** **not** `K.hull_rock` with its random per-ring offsets (that gives a zigzag of small triangles).
  Build an explicit obelisk: 6–7 vertices per ring at shared angles (±6° jitter) for the rings at h 0, .15, .45, .75,
  .90, so each side is a long near-planar face (each band a quad split into 2 tris, the split diagonal chosen so
  neighbouring bands don't line up); push one front vertex at h .45 in by 0.10–0.15 to make the diamond facet; a cap of
  3–4 triangles to an apex at (−0.25 W off centre, 0, 11.0); flat floor (a fan). Lean the shaft so the apex sits 0.3–0.5
  left of the base centre (f34 tip f .56 against the shaft centre f .59). **48–80 tris.**

#### Side Rock (reusable), and the Pillar — exploded (404,971,491,1090) and (162,1009,255,1127); `z_expl_sides.png`

- **Side Rock shape:** a tapered, **flat-topped** faceted block, base wider than the top (top face about 0.55 of the
  base width), sides steep; it **leans 8–15°** toward the spire (in the exploded it is drawn tilted ~20° with its top to
  the left). 14–15 facet regions, largest 0.07–0.15: medium-sized faces, no dominant face. An olive moss stain on its
  shaded (left) face in the exploded (§5.3).
- **Pillar shape:** the same family, taller: a broad tapered block with a flat top that slopes 5–10° to the front, big
  flat front faces (largest region 0.22–0.28), the top 0.55–0.63 of the base width; width per height .51 .89 .96 .92 .86
  .82 .76 .70 .63 .40 (exploded).
- **Hero sizes:** Pillar **3.9 W × 3.0 D × 7.7 H**; Rr **2.8 W × 2.6 D × 5.1 H** (lean 10° to −X).
- **Construction:** one function `side_rock(w, d, h, lean, seed)`: 5–6 vertices per ring, rings at h 0 (0.90),
  .12 (1.0), .55 (0.82), .92 (0.60), 1.0 (0.55, the flat top ring; all its points at the same z ± 0.05 so the top is one
  or two big faces); shared ring angles ±10°; lean the upper rings. **36–60 tris** each.

#### Foot Rock (base, front) — exploded (232,1125,416,1270); underside close-up; `z_expl_base.png`, `facets_eFoot.png`

- **Shape:** a chunky, wide faceted dome (screen w/h 1.27 in the exploded): a **broad flat top facet** (tilted 5–10°
  to the front, about 0.55 of W across), steep big faces round it, and a **front nose vertex** at about 0.45 H where
  5 large triangular faces meet; the flat floor 0.80–0.85 of the max width; widest at h .5–.6 (the sides bulge a
  little). 13–17 facet regions, largest 0.11–0.20; the underside close-up's floor is 0.54–0.56 of the visible stone.
- **Hero size: 5.0 W × 3.8 D × 3.7 H.**
- **Construction:** `K.hull_rock(..., keep_bottom=True)` is acceptable here with few points: rings `(0.0, 0.84, 7),
  (0.45, 1.0, 7), (0.80, 0.86, 6), (1.0, 0.55, 4)` with the top ring's points at one z (± 0.04) for the flat top facet,
  jitter 0.08; then move the front-most point of the 0.45 ring forward by 0.15 W to make the nose vertex. Check it
  doesn't come out as a soccer ball (§2.2). **40–70 tris.**

#### Medium rocks (BL, FL, FR, and the exploded's dome reused at the back)

- **Shape:** chunky faceted rocks, about as tall as wide (BL h/w 1.2, a blocky flat-topped rock; FL 0.75, rounded with
  a flat top facet; FR 1.1, a chunky block with a top sloping to the front-right); 10–14 visible facets, largest
  0.10–0.20. The exploded dome (122 × 109 px) is the same family.
- **Hero sizes:** BL 2.4 × 2.2 × 2.9; FL 2.8 × 2.4 × 2.1; FR 2.1 × 2.0 × 2.3; back dome 3.3 × 2.8 × 2.9.
- **Construction:** `medium_rock(w, d, h, seed, top="flat"|"slope")`, `K.hull_rock` with rings `(0.0, 0.86, 6),
  (0.35, 1.0, 6), (0.75, 0.82, 5), (1.0, 0.50, 3)`, jitter 0.10; the top ring flattened. **28–48 tris** each.

#### Small Rock (reusable) — exploded small rocks (120,1145,183,1201), (471,1170,529,1229), (398,1236,458,1287)

- **Shape:** squat faceted pebbles, screen w/h 0.96–1.18 (true h/w 0.6–0.8), one flat-ish top facet, 10–13 visible
  facets of similar size (largest 0.05–0.12). Widest at h .3–.5.
- **Hero sizes:** s1 1.05 × 0.9 × 0.75; s2 1.4 × 1.2 × 1.0; s3 1.75 × 1.4 × 1.2; one more at the back (1.2 × 1.0 × 0.8).
- **Construction:** `K.pebble`/`K.PEBBLE` rings with `keep_bottom=True`, jitter 0.12. **16–28 tris** each.

#### Foliage Cluster (reusable) — exploded clusters, e.g. (194,937,235,985), `z_clusterA.png`; junction close-up

- **Shape:** a **star rosette** of **6–7 broad oval leaves** from one root: one upright back leaf (the tallest, pitch
  55–70°), two side leaves (pitch 30–45°), three or four low front leaves (pitch 10–25°, shorter), round a **small
  round lime bud** in the centre (Ø 0.20–0.25 of the rosette, a 6-sided dome). Leaves are broad ovals with a soft
  rounded point, width 0.60–0.70 of the length, folded along a midrib (fold 0.2) so each shows a lit yellow-lime half
  and a greener half; thick (0.04–0.05). Screen w/h of a loose cluster 0.86–1.05 (41–45 × 44–49 px).
- **Hero sizes:** rosettes 1.2–2.2 across, 0.8–1.3 tall; leaves 0.55–0.85 long; small sprigs (C3, C8, C11) 3–5 leaves.
- **Construction:** `rosette(loc, size, seed, leaves=7, upright=True)` from `K.leaf(shape="round", fold 0.2, curl 0.2,
  thick 0.045)` (16 tris a leaf) plus a bud (`a.cyl` 6 sides with a cap, ≈ 12–18 tris). Not `K.clover`'s default three
  tiers of 18 leaves (too dense, W01's minor: "clover clumps chunkier than the master's small rosettes"), and **no
  flowers** (the bud is green-yellow, not a white flower). **100–130 tris** a rosette, sprigs 50–80.

## 2. Layout (starting values; tune on the renders)

Studs, build frame (front −Y, +X right, ground z 0). X from the f34 fractions (x = (f − 0.5) × 14.0); Y from each
piece's front ground point (screen h / (31.5 × sin 20°)), measured from the foot rock's front at y −4.6; Z from its top
(s = z cos e + (y + 4.6) sin e). Cross-checked with the front cell (15.6 px/stud) within 0.04 in X.

### 2.1 Rocks

| Piece | Centre (x, y), base z | Size W × D × H | Lean / yaw | Sheet evidence (f34) | Notes |
| --- | --- | --- | --- | --- | --- |
| S Spire | (+1.25, +1.8), −0.05 | 4.4 × 3.8 × 11.0 | apex 0.4 to −X, 0.2 to −Y | tip f .56 h 1.0; shaft right flank x 417 at h .6 | the tallest; front vertex ridge at about x +1.0 |
| P Pillar | (−1.35, +0.5), −0.05 | 3.9 × 3.0 × 7.7 | top 0.3 to +X (toward S) | f .27–.55, top h .72 (y 150) | right-back corner presses ≤ 0.6 into S's left-front flank |
| Rr Side Rock | (+3.65, +0.3), −0.05 | 2.8 × 2.6 × 5.1 | 10° toward −X | f .67–.85, top h .52 (y 228) | left side presses ≤ 0.5 into S's right flank |
| F Foot Rock | (+0.05, −2.7), −0.05 | 5.0 × 3.8 × 3.7 | yaw 0, nose to −Y | f .33–.68, top h .36, bottom h 0 | front at y −4.6; back ≈ −0.8; 0.2 into P's front |
| BL medium | (−4.85, 0.0), −0.05 | 2.4 × 2.2 × 2.9 | yaw 20° | f .07–.24, top h .34 | behind FL and C2 |
| FL medium | (−3.9, −2.1), −0.05 | 2.8 × 2.4 × 2.1 | yaw −15° | f .12–.32, top h .23, bottom h .04 | touches F's left side |
| FR medium | (+5.95, +0.5), −0.05 | 2.1 × 2.0 × 2.3 | yaw 35° | f .85–1.0, top h .31, bottom h .11 | touches Rr's right foot |
| s1 small | (−3.05, −3.5), −0.04 | 1.05 × 0.9 × 0.75 | — | f .25–.32, top h .08 | in front of the FL–F junction |
| s2 small | (+2.95, −3.6), −0.04 | 1.4 × 1.2 × 1.0 | — | f .66–.76, top h .10 | in front of F's right foot |
| s3 small | (+4.4, −2.6), −0.04 | 1.75 × 1.4 × 1.2 | — | f .75–.88, top h .15 | in front of Rr |
| Back dome (medium) | (−0.6, +4.5), −0.05 | 3.3 × 2.8 × 2.9 | yaw 160° | top cell rear mass; exploded dome | behind S and P; ≤ 0.4 into S's back |
| Back-right (FR mesh) | (+4.3, +3.2), −0.05 | 2.1 × 2.0 × 2.3 | yaw 140° | top cell upper-right rock (f .71–1.0, h .51–.80) | |
| Back-left small (s mesh) | (−4.4, +2.4), −0.04 | 1.2 × 1.0 × 0.8 | — | top cell left rock group | |

- **Expected extents:** X −7.0 … +7.0 (C1's leaves at the left, FR at the right) = 14.0; Y −4.6 … +5.9 = 10.5; Z 0 …
  11.0 (spire apex; nothing else above 8.7).
- **Self-consistency at f34_sheet (0, 20):** this layout puts the spire tip at h 1.0 (by construction), the pillar top
  at h .72 (sheet .72), Rr .52 (.52), F .36 (.36), BL .34 (.34), FL top .23 / bottom .04 (.23 / .04), FR top .31 / bottom
  .11 (.31 / .11), s2 bottom .01 (.01). W : H 14.0 / 12.46 = 1.12 (sheet 1.138); at e 18 → 1.15.
- **Checks on the renders** (floor hidden):
  - **f34_sheet (0, 20):** W : H 1.08–1.20; top profile within ±0.07 (mean ≤ 0.04) of §1.2; width per height within ±0.07;
    each rock's f box ±0.04 and top h ±0.04; shares R 77.3 ± 4, G 22.7 ± 4; green fifths 24.5 / 34.9 / 13.9 / 15.2 / 0.7
    ±6 (top fifth ≤ 3).
  - **front_sheet (0, 18):** W : H 1.05–1.17; tops pillar .70, Rr .49, foot .35 ±0.04; shares R 76.8 / G 23.2 ±4.
  - **The spire leads:** in both, the only silhouette above h .82 is the spire (+ C4's top leaf at most to .81), and
    the spire's visible width at h .72 is 0.19–0.25 W.

### 2.2 Rock-shape targets (binding; check with `M.audit`, own bmesh code and `facets.py` on the parts shot and the hero)

M023 lobes failed first as "soccer-ball" facets; M031's rocks were mauve and upright slabs; W01's spire round 2 failed
on "shoulders as round boulders, slim spire". These are measurable:

| Target | Spire | Pillar / Side Rock | Foot Rock | Medium | Small |
| --- | --- | --- | --- | --- | --- |
| Mesh tris (before any refine) | 48–80 | 36–60 | 40–70 | 28–48 | 16–28 |
| Faces visible from one side (eye) | 10–14 | 10–14 | 14–20 | 10–14 | 10–13 |
| `facets.py` regions ≥ 0.4 % (thr 5 / 7), parts shot | 10–14 / 7–10 | 12–15 / 9–14 | 13–17 / 12–16 | 10–14 / 9–13 | 10–13 / 9–13 |
| Largest region, share of the rock's projected area | 0.20–0.30 (one long flank face) | Pillar 0.20–0.30; Side Rock 0.08–0.16 | 0.11–0.20 | 0.10–0.20 | 0.05–0.12 |
| True H / W | 2.5 (11.0 / 4.4) | Pillar 1.97; Side Rock 1.82 | 0.74 | BL 1.2, FL 0.75, FR 1.1, dome 0.88 | 0.6–0.8 |
| Flat floor, share of max width (X and Y) | 0.85–0.90 | 0.85–0.92 | 0.80–0.85 | 0.80–0.88 | 0.65–0.80 |
| Widest section | h .12–.20 | h .10–.30 | h .45–.60 | h .30–.45 | h .30–.50 |
| Flat top | apex (no top face) | one or two faces with normal z > 0.95, ≥ 0.55 of the top ring's width | one face (or 2 coplanar tris) with normal z > 0.97, 0.50–0.60 of W across | BL and FL one top facet | one top facet |

- **Long flat faces on the spire:** at least 4 faces taller than 0.35 of the spire's height; at least 3 faces with area
  ≥ 2.5 sq studs; no face smaller than 0.04 sq studs except at the cap apex.
- **Irregular triangles, not a pattern** (all rocks except the small ones): triangle area CV ≥ 0.6; edge length CV ≥ 0.35;
  vertex valence 3–8 (floor-fan centre excluded), mean 4.5–6.0, no single valence on more than 45 % of the verts; at
  least 15 % of triangles with a smallest angle under 25° (the long sliver faces); no pentagon/hexagon faces; no vertex
  ringed by 5–6 near-equal (±15 %) triangles at more than 2 vertices of a rock (the foot rock's nose vertex is the one
  allowed fan, and its five faces differ in size by ≥ 30 %). Never `primitive_ico_sphere`, never Fibonacci planes,
  never subdivision plus displacement.
- **No round boulders as shoulders:** the pillar and Rr have flat tops and near-planar steep sides (wall-facing area,
  normal within 20° of horizontal, ≥ 0.55 of their non-floor area); the foot rock is the only dome among the big four.

### 2.3 Foliage (rosette instances; `rosette()`)

| Group | Root (x, y), z | Rosettes / size | Sheet evidence (f34) | Seat |
| --- | --- | --- | --- | --- |
| C1 far-left | (−6.2, −0.4) and (−5.6, −1.7), 0 | 2 × 1.6–2.0 | f .00–.15, h .09–.24 | on the ground against BL's and FL's left flanks |
| C2 left column | (−3.4, −0.8), 0; second at z ≈ 2.4 on P's lower-left flank | 2 × 1.6 | f .19–.35, h .17–.42 | in the BL / FL / P crevice, the upper one conformed onto P |
| C3 sprig | (−1.3, −1.4), z ≈ 3.5 on F's back-left top | 1 × 1.1 (4–5 leaves) | f .38–.46, h .33–.44 | in the F–P crevice |
| C4 pillar top | (−0.6, +1.1), z ≈ 7.6 on P's top back-right corner | 1 × 1.4 | f .39–.49, h .71–.81 | against S's left flank |
| C5 foot-top right | (+0.9, −1.0), z ≈ 3.3 on F's back top | 1 × 1.8 (7 leaves) | f .50–.63, h .34–.45 | in the F–S crevice |
| C6 F–Rr crevice | (+2.5, −0.9), 0; second at z ≈ 1.6 on Rr's front-left flank | 2 × 1.5 | f .63–.76, h .26–.40 | in the crevice between F, S and Rr |
| C7 right foot | (+3.5, −1.6) and (+4.3, −1.2), 0 | 2 × 1.5–1.8 | f .67–.83, h .11–.26 | in front of Rr, behind s2/s3 |
| C8 low front | (+2.0, −3.9), 0 | 1 × 1.0 (5 leaves) | f .61–.68, h .01–.12 | between F's right foot and s2 |
| C9 right | (+5.3, −1.3), 0 | 1 × 1.7 | f .83–.94, h .09–.27 | between Rr's right foot, s3 and FR |
| C10 Rr top + spire flank | (+3.3, +0.6), z ≈ 5.1 on Rr's top; second at z ≈ 6.3 on S's right flank | 2 × 1.4 | f .69–.80, h .48–.70; r34/side lime patch on S's right flank | the upper rosette conformed onto S's flank, leaning out 20–30° |
| C11 s1 sprig | (−2.5, −3.8), 0 | 1 × 0.7 (3 leaves) | f34 tiny greens right of s1 | |
| Back B1 | (−3.0, +2.8), 0 (3 rosettes, a mound) | 3 × 1.6–2.0 | top cell's rear mound (46 % of its green) | between BL, P's back and the back dome |
| Back B2, B3 | (+1.8, +4.6), (+5.3, +2.3), 0 | 2 × 1.4 | top cell right and rear rosettes | at the back dome and the back-right rock |

- **Counts:** about 21 rosettes (17 full + 4 sprigs), ≈ 130 leaves, 21 buds. **f34_sheet must show** 10 rocks, the six
  green groups of §1.2 (C5–C9 may merge as on the sheet) and ≈ 14 ± 2 rosettes; nothing green above h .82.
- **Seats:** roots at z 0–0.05 or on a rock surface (`K.top_at` / `K.conform`); leaves may touch rocks but cut no more
  than 0.05 into them; every rosette sits in a crevice or against a taller rock (junction close-up), never alone in the
  open; the upper rosettes of C2, C6 and C10 conform onto the rock flank behind them.

## 3. View conflicts and resolutions

### 3.1 The front three-quarter is an elevated front view; the front cell is the same drawing

- **Evidence.** Every rock's X fraction agrees within 0.04 between the f34 and the front cell (§1.3); the top profiles
  agree within mean 0.05 and the width per height within 0.10 at h .15 and 0.04 elsewhere; W : H 1.138 against 1.107;
  the same six green groups at the same places (shares 22.7 / 23.2 %). Both show the foot rock's top face and the
  pillar's and Rr's flat tops, so both cameras are above.
- **Elevation:** from the stacked tops and bottoms (§2.1 self-consistency) e ≈ 20° for the f34 and slightly lower for
  the front (its tops are 0.01–0.05 H lower). Uncertain by ±5°.
- **Resolution.** Compare the f34 cell with **`f34_sheet (0, 20)`** (probe 15 / 20 / 25 once, keep the smallest
  top-profile error and record it) and the front cell with **`front_sheet (0, 18)`** (probe 14 / 18 / 22). The kit
  `front34` is self-consistency only.

### 3.2 The "rear three-quarter" is a front-LEFT view (az ≈ −30), not a rear view

- **Evidence.** The pillar stays on the left and the foot rock in front (a true rear view would put the foot rock
  behind the spire and the pillar on the right). The foot rock moves right relative to the spire's tip by 0.13 W
  against the f34, which a camera swung about 30° to the front-left gives for the 3.4-stud Y gap between F and S.
- **Resolution.** Render an extra **`r34_sheet (−30, 20)`** and compare it loosely (W : H 0.90–1.05 (sheet 0.959),
  shares ±5, the spire's width at h .72 0.24–0.31 W, the C10 rosettes reading as a lime patch on the spire's right
  flank). The kit `rear34 (152, 12)` is self-consistency only.

### 3.3 Side and rear cells are front redraws

- **Evidence.** Both show the front arrangement again (pillar left, foot rock front centre, spire behind, a small rock
  low at the right); W : H 0.867 and 0.969 (narrower than the front's 1.107); their top profiles peak at f .50 like the
  front's. A true side of our layout puts F at the left (front) and Rr / FR nearest the camera; a true rear puts the
  back dome in front and the pillar on the right.
- **Resolution.** Render kit **`side (90, 10)`** and **`rear_sheet (180, 15)`**, judge loosely: the spire the only peak
  (top profile 1.0 within f .40–.60), a stepped shoulder each side, the broad foot (width per height at h .15 ≥ 0.85),
  green 15–28 % with most of it in the lower 40 %. Record their W : H as known misses (ours: side ≈ 10.5 / 12 ≈ 0.87,
  rear ≈ 1.1).

### 3.4 The top cell is a re-composition

- **Evidence.** Its central mass is 0.52 W across (our spire's footprint 0.31 W, the foot rock 0.36 W); no pillar or
  Rr reads as such; W : D 1.02 against our 1.33.
- **Resolution.** Use it for what it agrees with: rocks ring the centre on every side, a big foliage mound at the back
  left (B1), a medium rock at the back right, rosettes all round. Render the kit top (0, 89) loosely: green 25–38 % (sheet
  32.1 %), rocks visible on all four sides of the spire, B1 the largest green group. Record W : D as a known miss.

### 3.5 Exploded sizes against the hero

- **Evidence.** Spire w/h 0.56 in the exploded against about 0.40 in the hero (§1.4); pillar w/h 0.79 against about 0.51;
  spire / foot height 1.57 against about 2.1.
- **Resolution.** The hero governs: the spire is a 4.4 × 3.8 × 11.0 obelisk and the pillar 3.9 × 3.0 × 7.7. The parts
  export the hero meshes. Record the exploded's squatter spire and pillar as known misses. Do not make the spire
  slimmer than base W/H 0.38 (W01's "slim spire" fail).

### 3.6 Labels against the shapes

- "Side Rock (reusable)" points at the right-hand leaning rock; the left pillar is unlabelled and is the same family
  (flat top, tapered steep sides), built by the same function taller. Export one SideRock part (Rr).
- "Foot Rock (base, front)" and "UNDERSIDE VIEW (Base Rock)" are the same rock.
- The exploded's medium dome and the small rock behind the foot rock are unlabelled: the dome becomes the back dome, the
  small one the back-left small rock (the f34 can't show either; the top cell suggests both).

### 3.7 Palette names against the renders

- **"Rock Shadow / Cool gray" `#9B949E` is lavender (282°, B > R > G)**: it equals the rendered shade faces (`#756C70`–
  `#787076`, hue 290–330°), the cool sky fill, **not paint**. Using it as a key gives mauve rocks (M031 round 1).
- "Main Rock" `#BBA8A0` (18°, 0.14) is paler and greyer than the rendered medians (`#C2A594`–`#C9AD9C`, 0.22–0.24);
  "Rock Highlight" `#D3BAAC` (22°, 0.18) is the lit upper-face tone.
- "Foliage Dark / Mid / Light" `#819A1E` / `#97AB23` / `#CCCA24` (72° / 69° / 59°, sat 0.80–0.82) are the deep, mid and
  sun ends of one lime family; the rendered leaves are more saturated (0.94–0.98).

### 3.8 "Hollow"/thickness

- Not raised on this sheet. Closed solid shells, no inner walls.

### 3.9 "Simple, solid colors; no photo textures" and "no noise" against the user's blended-colour rule

- The user's rule wins, quietly: broad light patches on upper faces (whole facets), deeper warm patches low down, faint
  olive stains near the foliage, leaf halves and tiers, low Tint. No per-triangle confetti, nothing photographic.

### 3.10 Ground shadow

- Soft blue-grey (`#999FAC`, hue 221°) to the left of and behind each piece: lighting, background in every
  measurement, not modelled.

## 4. Construction plan (stages 1–3)

1. **Parts first,** each from its own function and checked against its cell:
   - `spire()` → `StoneSpireMain`: the obelisk (§1.4) bare. Compare with the exploded spire (outline, width per height,
     8–12 regions) and with the spire close-up (`spire_cu`: the cap from the front at e 10, framed like (686,791,860,945)).
   - `side_rock()` → `StoneSpireSideRock`: Rr with one rosette on its top (the exploded drops one there). Compare with
     the exploded Side Rock.
   - `foot_rock()` → `StoneSpireFootRock`: F with its two top sprigs (exploded). Compare with the exploded Foot Rock and
     the underside close-up (an extra from below, e −35).
   - `small_rock()` → `StoneSpireSmallRock`: s2's mesh bare. Compare with the exploded small rocks.
   - `rosette()` → `StoneSpireFoliage`: one 7-leaf rosette with its bud. Compare with `z_clusterA.png` (screen w/h
     0.86–1.05, an upright back leaf, the bud showing).
   - `medium_rock()` builds BL, FL, FR and the back pieces inside the hero only.
   - Render a **parts shot** (az 0, e 25) laid out like the exploded (spire centre, side rock right, foot rock front,
     small rock right-front, rosette left).
2. **Hero:**
   1. Build the 13 rocks at their §2.1 places with their own seeds (P and Rr from `side_rock`, BL/FL/FR/back from
      `medium_rock`, s1–s3 and back-left from `small_rock`); each its own closed shell, floor-cut flat at z 0
      (`m004.floor_cut`). No booleans between rocks: they interlock by overlapping ≤ 0.6 at the noted contacts.
   2. Paint the rocks (stage 4 needs the face lists; keep the original facet ids before any refine).
   3. Place the 21 rosettes (§2.3), conforming the flank ones (C2, C6, C10 upper; C4) with `K.conform`.
   4. `M.fix_bowties`, origin at the bbox bottom centre, transforms applied.
3. **Budget** (§4.3): hero about 2600–3100 (limit 4000); each part under 300 (limit 1000). If over, cut B2/B3 to 5 leaves
   and drop the hidden back leaves of B1 first; never thin a rock below §2.2.
4. **Placeholder keys** (stage 1): `m039_rock`, `m039_leaf`, `m039_bud`. Stage 4 adds the rest (§5.4).
5. **Stage 1 acceptance** (render, compare every view, measure with this folder's scripts):
   1. **Overall read:** a tall angular warm obelisk at the back, a flat-topped pillar on its left at 0.7 of its
      height, a shorter flat-topped side rock on its right, a big faceted foot rock in front, a ring of medium and
      small rocks, lime star rosettes in the crevices, on the shoulders and up the spire's right flank.
   2. **f34_sheet against the f34 cell:** §2.1 checks (W : H, top profile, width per height, rock boxes and tops, shares,
      green fifths); 10 rocks; six green groups.
   3. **front_sheet against the front cell:** §2.1 checks.
   4. **r34_sheet, side, rear, top:** loosely (§3.2–§3.4).
   5. **Rock-shape targets** (§2.2), all of them, on each part and on the hero's rocks.
   6. **Parts against their cells** (step 1), the **spire close-up extra** `spire_cu`, the **underside extra** (FootRock
      from below, e −35) and a **junction extra** `junc_cu (0, 12)` framed on C6 between F, S and Rr.
   7. **Hero size** 14.0 × 10.5 × 11.0 (±0.6 / ±0.8 / ±0.3); rocks at §2.1 sizes ±0.2.
   8. **Scale shot:** the hero beside a 5.5-stud character marker.
6. **Stage 2:** every shell closed and manifold: zero non-manifold edges and verts (`nonmanifold_verts` 0), boundary,
   wire and loose elements; no zero-area faces or n-gons; normals outward; no corners under 5° (the spire's long
   slivers must stay above it: m011 `_tidy` / `_desliver`); no decimation below §2.2.
7. **Stage 3:** smart UV, margin ≥ 0.008, no overlaps, even texel density (leaves and buds included).

### 4.3 Budget table

| Piece | Count | Tris each | Total |
| --- | --- | --- | --- |
| Spire | 1 | 48–80 | 48–80 |
| Pillar, Rr (side_rock) | 2 | 36–60 | 72–120 |
| Foot Rock | 1 | 40–70 | 40–70 |
| Medium (BL, FL, FR, back dome, back-right) | 5 | 28–48 | 140–240 |
| Small (s1–s3, back-left) | 4 | 16–28 | 64–112 |
| Rosettes (7 leaves × 16 + bud 12–18) | 17 | 124–130 | 2110–2210 |
| Sprigs (3–5 leaves + bud) | 4 | 60–96 | 240–380 |
| **Hero** | | | **about 2700–3200** (limit 4000) |
| Parts: Main / SideRock / FootRock / SmallRock / Foliage | | | about 60 / 180 / 300 / 24 / 128 (limit 1000) |

## 5. Colour plan (stage 4)

### 5.1 Swatches (flat; medians of a 46 × 48 box inside each, sd ≤ 1.4)

| Swatch | Box | Hex | HSV | Channel order |
| --- | --- | --- | --- | --- |
| Main Rock (pale warm gray) | (36,1366,82,1414) | `#BBA8A0` | 18°, 0.14, 0.73 | R > G > B |
| Rock Shadow (cool gray) | (130,1366,176,1414) | `#9B949E` | 282°, 0.06, 0.62 | **B > R > G (lavender)** |
| Rock Highlight (warm beige) | (226,1366,272,1414) | `#D3BAAC` | 22°, 0.18, 0.83 | R > G > B |
| Foliage Dark (olive green) | (329,1366,375,1414) | `#819A1E` | 72°, 0.81, 0.60 | G > R > B |
| Foliage Mid (leaf green) | (418,1366,464,1414) | `#97AB23` | 69°, 0.80, 0.67 | G > R > B |
| Foliage Light (yellow green) | (508,1366,554,1414) | `#CCCA24` | 59°, 0.82, 0.80 | R ≈ G > B |

### 5.2 Rendered regions (`samp.py`; median / lit quartile / shade quartile)

| Region | Mask | Median | Lit | Shade |
| --- | --- | --- | --- | --- |
| Rock, whole f34 / front / r34 | R | `#C9AD9C` / `#CBAE9D` / `#B99F91` | `#E5C9B6` / `#E3C8B4` / `#E3C7B5` | `#756C70` / `#736D72` / `#756C6F` |
| Rock, whole side / rear / top | R | `#C3A99D` / `#CAAC9A` / `#BFA495` | `#E6CBB9` / `#E5CAB7` / `#E4C8B4` | `#767074` / `#736C72` / `#736A67` |
| **Rock, exploded all (no cast shadows across parts)** | R | **`#C2A594`** | `#E6CAB5` | `#736C70` |
| Exploded spire / side rock / foot rock | R | `#C5A997` / `#C7A997` / `#C7A997` | `#E3C5B0` / `#E8CCB8` / `#EDD1BD` | `#736D74` / `#756B6C` / `#797176` |
| Exploded small L / R / front-right | R | `#BA9D8E` / `#C2A496` / `#C4A999` | `#E0C0A7` / `#EACEB8` / `#E4C3AE` | `#716A70` / `#756763` / `#6E6568` |
| Exploded pillar (mostly its shaded face) | R | `#9A8781` | `#DEBDA6` | `#777073` |
| Spire close-up / junction close-up | R | `#D8BCA9` / `#D2B4A1` | `#EED5C0` / `#ECD3BF` | `#78737C` / `#A38E89` |
| Underside close-up (floor in shade) | R | `#88736A` | `#E9CFBB` | `#76635C` |
| Rock thirds (top / mid / bottom): exploded spire / foot / side | R | `#DEC2AE` `#C8ADA0` `#998A87` / `#D3BBAF` `#C7A997` `#987F7E` / `#DCC4B0` `#D8BAA5` `#AB9083` | | |
| Rock thirds, exploded small R / front-right; f34 FR | R | `#E0C3AD` `#C8AC9E` `#BEA28D` / `#D9BBA8` `#BEA395` `#C3A793` / `#DAC1B3` `#DBBCA7` `#CCAE9B` | | |
| f34 split by hue | R | warm (78 %) `#D1B5A4`; lavender (21 %) `#787076` | | |
| Leaves, exploded clusters (all) | G | `#769705` | `#C8CF09` | `#456803` |
| Leaves, f34 / front / junction | G | `#8FA304` / `#93A406` / `#AAB703` | `#D0D204` / `#CBD105` / `#C8CF04` | `#3B5C03` / `#3C5606` / `#3A5404` |
| Lime patch on the spire flank (r34 C10) | G | `#BBC409` | `#D9D90C` | `#8A9B06` |
| Bud (cluster A centre) | G | `#B8C302` (64°, 0.99, 0.76) | | |
| Olive moss stains: exploded side rock / f34 pillar foot / f34 Rr low / exploded foot low-left | — | `#767137` / `#6B664D` / `#AC9C42` / `#6E6C49` (hue 50–57°, sat 0.28–0.62) | | |
| Ground shadow f34 / exploded | B | `#999FAC` / `#ACADB1` | | |

Deciles (dark → light):

```
rock  f34   #6D6460 #776E73 #827679 #968483 #C2A796 #CDB1A1 #D8BBA7 #DEC1AD #E3C7B3 #EFD7C3
rock  expl  #6D6464 #746D74 #7B7276 #867A7C #AD9586 #C9AC9A #D2B5A4 #DEBFAA #E4C7B1 #EED4BF
green expl  #274702 #4B7003 #5A7F04 #628904 #6C9105 #7C9E05 #97B106 #AEC006 #C3CC08 #D9DB0D
green f34   #263C04 #416303 #577603 #6B8306 #849A03 #9AAB03 #AEBA03 #C1C704 #CED004 #D9D905
```

### 5.3 How the colour works

**Rocks.**
- **One pale warm grey-pink stone for all rocks.** Medians hue 19–24°, sat 0.19–0.24, **always R > G > B** (R − B 40–
  50 levels). The lit faces are peach (`#E5C9B6`, hue 22–25°), the shaded faces cool lavender (`#756C70`, hue 290–330°,
  B ≥ R > G). That split is the warm key and the cool sky fill: **light, not paint**. Never colour by facing.
- Per-rock medians differ only by how much of each rock is lit (the exploded pillar `#9A8781` is mostly its shaded face;
  the spire close-up `#D8BCA9` mostly lit); their lit quartiles agree within 12. One key.
- **Gentle painted signal:** broad light patches on upper faces (top thirds `#DEC2AE`, `#DCC4B0`, `#E0C3AD`; swatch Rock
  Highlight `#D3BAAC`) and deeper warm patches low on the rocks (bottom thirds' lit tone `#BEA28D`–`#C3A793`, `#AB9083`),
  both by a noise field over whole facets plus a height bias. The spire gets the light patches on its upper third and
  the deep ones on its lowest 15 %; no dark painted foot band.
- **Olive moss stains** (faint): low on the pillar's left face, the side rock's shaded face and the foot rock's left
  side, next to the rosettes: olive `#6E6C49`–`#767137` in shade, `#AC9C42` lit (hue 50–57°). Whole facets at 10–20 %
  mix, chosen by distance to the nearest rosette root and height (< 2.5), never by facing.
- **Mauve guard (M031 round 1):** every rock key R > G > B with hue 14–26° and R − B ≥ 30. `#9B949E` ("Rock Shadow") is
  never a key, not even as a mix.

**Foliage.**
- **Lime-green rosettes:** medians hue 64–74°, sat 0.95–0.98, value 0.59–0.72; lit halves yellow-lime (`#C8CF09`–
  `#D0D204`, hue 60–63°), shade halves deep green (`#3B5C03`–`#456803`, hue 80–84°). The two-tone look of each leaf is
  mostly its midrib fold in the light.
- **Tiered by position:** the low front leaves `leaf_deep` (mixed 40 %), side leaves `leaf`, the upright back leaf and
  the inner bases `leaf_light`; the bud `bud` (yellow-lime). Rosettes high on the formation (C4, C10) one step lighter
  (they read as lime patches, `#BBC409`).

### 5.4 Keys (start from these; `K.calibrate`; write the calibrated hexes into `palette()`)

The calibration targets are medians of **unshadowed** rendered regions (the exploded parts and the close-ups), not
swatches. `K.sample` kinds: `"stone"` for rock keys, `"green"` for leaf keys, `"vivid"` for the bud.

| Key | Calibration target | Hue / sat / order | Where | Finish |
| --- | --- | --- | --- | --- |
| `m039_rock` | `#C5A896` (exploded spire `#C5A997`, side `#C7A997`, foot `#C7A997`, all `#C2A594`; start from swatch Main Rock `#BBA8A0`) | 19–24°, 0.19–0.25, R > G > B | all rocks, default | rough 0.9, metal 0 |
| `m039_rock_light` | `#D9BFAC` (top thirds `#DEC2AE`, `#DCC4B0`, `#E0C3AD`; swatch Rock Highlight `#D3BAAC`) | 20–25°, 0.17–0.22, R > G > B | broad patches on upper faces at 25–30 %, the spire's upper third at 35 % | rough 0.9 |
| `m039_rock_deep` | `#B39886` (bottom thirds `#BEA28D`, `#C3A793`, `#AB9083`) | 18–24°, 0.22–0.28, R > G > B | broad patches below 1.5 studs at 15–20 % | rough 0.9 |
| `m039_moss_stain` | `#8C8548` (stains `#767137`, `#6E6C49` in shade, `#AC9C42` lit) | 50–57°, 0.35–0.50, R ≥ G > B | whole facets near rosette roots, mixed 10–20 % into `m039_rock` | rough 0.9 |
| `m039_leaf` | `#7E9C05` (exploded clusters `#769705`; f34 `#8FA304`; swatch Foliage Mid `#97AB23`) | 68–74°, ≥ 0.94, G > R > B | side leaves, default | rough 0.85, low spec |
| `m039_leaf_light` | `#C8CF0A` (lit quartiles `#C8CF09`, `#C8CF04`; swatch Foliage Light `#CCCA24`) | 59–64°, ≥ 0.93, \|R − G\| ≤ 12 | upright back leaf, inner leaf bases, C4 / C10 at +1 step | rough 0.85, low spec |
| `m039_leaf_deep` | `#4E7404` (shade quartiles `#3B5C03`–`#456803` lifted one step; swatch Foliage Dark `#819A1E` darkened) | 78–84°, ≥ 0.94 | low front leaves at 40 % | rough 0.85, low spec |
| `m039_bud` | `#BCC604` (bud `#B8C302`) | 62–66°, ≥ 0.95 | rosette buds | rough 0.75 |

**Calibration warnings:**
- **Rock:** calibrate `m039_rock` on the parts shot (spire, side rock, foot rock, small rock) against `#C5A896`; then
  check the f34_sheet rock median within 10 of `#C9AD9C` with hue 19–24°, sat 0.19–0.25 and R > G > B. Our studio's
  shade faces read neutral or warm grey, not lavender: don't push them by facing, and don't let any key drift to B ≥ G.
- **Leaves:** parts-shot Foliage median within 10 of `#769705`; f34_sheet leaves median within 14 of `#8FA304`. Lit
  quartiles of our studio run 16–22 levels below the sheet's (023's verifiers): that is light, not paint. W01's spire
  round 1 failed on greens too dark: keep `leaf` value ≥ 0.58.
- **Stains** must stay faint: the f34_sheet rock median must not move more than 4 levels when the stains are switched
  on, and no stain facet may read green (hue > 60°).

### 5.5 Blending (`K.blend(mode="blend", steps=3)` over explicit face lists; fields are positions, never facing)

- **Rocks** (on the original facets, before any refine): `rock` base; `K.noise_field(scale≈0.25)` patches →
  `rock_light` on faces with centre z above 0.55 of the rock's height at 25–30 % (the spire's upper third 35 %); low
  patches → `rock_deep` below 1.5 studs at 15–20 %; `moss_stain` by distance to the nearest rosette root (< 1.2) and
  height (< 2.5) at 10–20 %. Per-rock tint ±0.04 so neighbouring rocks separate.
- **Leaves:** by role in the rosette (low front / side / upright back) `leaf_deep` 40 % → `leaf` → `leaf_light`; each
  rosette its own `tint_var` 0.04; the high rosettes (C4, C10) one step lighter.
- **Hard edges only** where materials meet: leaf | bud. The rock | leaf boundary is between separate shells.

### 5.6 Texture (Tint) and finish

- **Tint:** rock amp 0.04, scale 0.3, per original facet (a refined facet keeps one tone); leaves 0.04; buds none.
  Never per-triangle confetti ("no noise").
- **Finish:** rock rough 0.9, metal 0; leaves `low_spec=True` (`K.FOLIAGE_SPEC` 0.06), rough 0.85; bud rough 0.75.
  No emission anywhere.

### 5.7 Re-measure (final renders against the sheet, same boxes and masks)

- **Rock:** f34_sheet median within 10 of `#C9AD9C`; parts-shot median within 8 of `#C5A896`; per-part medians within
  12 of spire `#C5A997`, side rock `#C7A997`, foot rock `#C7A997`, small rock `#C4A999`; all R > G > B, hue 19–24°, sat
  0.19–0.25. Side and rear medians too (mauve guard).
- **Leaves:** f34_sheet G median within 14 of `#8FA304`, hue 64–74°, sat ≥ 0.93; C10's patch lighter than the lower
  rosettes (hue ≤ 66°).
- **Bud:** hue 62–66°, sat ≥ 0.9.
- **Shares** per §2.1.

## 6. Joins and contact

- **Rocks:** each its own closed shell, floor-cut flat at z 0 (base 0.03–0.05 below before the cut). They **interlock**
  where the sheet shows them pressed together: P's right-back corner into S's left-front flank (≤ 0.6), Rr's left side
  into S's right flank (≤ 0.5), F's back into P's front (≤ 0.2), FL against F, FR against Rr, the back dome into S's back
  (≤ 0.4). No booleans; no visible gap at those contacts from the f34, front or r34; no rock floating or standing on a
  point.
- **Crevices** stay readable: a dark seam (the T/O mask) along P–S, S–Rr, F–P and F–Rr in the f34_sheet, as on the
  sheet (§1.3; the junction close-up).
- **Rosettes:** roots on the ground (z 0–0.05) or on a rock (`K.top_at` / `K.conform`, sink 0.02–0.04); leaves press
  against rocks but cut no more than 0.05 into them; C2, C6, C10 upper rosettes conformed onto the flank behind them.

## 7. Lighting and VFX plan (stages 5 and 6)

**What the sheet shows:** sunlit rocks and foliage; no glow, light, sparkle, dust, particles or VFX callout. The
brightest pixels are lit peach rock faces and lit leaf halves, which darken on their shaded sides.

### 7.1 Stage 5 (lighting): skip, and record why

- **No emissive faces, no PointLight.** The buds are paint, not glow.
- **Studio note (Requires Manual Validation):** check in Studio that the rock stays warm grey-pink (not lilac or grey)
  under the game's sun, that the spire's flat faces read as separate planes (flat shading kept), and that the leaves
  stay lime, not olive.

### 7.2 Stage 6 (VFX): skip, and record why

- Kinds in `art/blender/lib/vfx.py` (frozen for modellers) include `dust`, `ore_glint`, `crystal_glow`, etc.; **none is
  shown or implied** here. Record "Stage 6 skipped: the sheet shows no effect".
- **Not recommended:** `dust` or pollen motes, glints, harvest sockets.

## 8. Naming and decisions for the main session

**Names owned elsewhere.** Found by searching the repo text, the exported manifests and every sheet / wip `.blend`
(zstd-decompressed) with the M035 study's `blendall.py`:
- **W01:** `RockSpire`, `RockSpireMain`, `RockSpireFootCollar`, `RockSpireShort`, `RockSpireTall`, `RockSpireLeaning`;
  keys `w01_*`.
- **M033:** `MossBoulderSideRock`. **Elsewhere:** `StarstoneFootRock`, `SulfurFootRock`, the kit's `*FoliageCluster`
  (juniper) and `*SmallRock`/`*RockSmall` names.
- `M.mk` would silently rename a clash to `<name>M039`, so avoid all of these.

**Proposed names.** None of `StoneSpire`, `StoneSpireMain`, `StoneSpireSideRock`, `StoneSpireFootRock`,
`StoneSpireSmallRock`, `StoneSpireFoliage` or `m039_` occurs in the repo text, the kit `.blend` or any sheet / wip
`.blend`. "Stone spire" keeps the sheet's subject and subtitle ("Angular stone spire") without W01's `RockSpire*`.

| Object | Part | Why |
| --- | --- | --- |
| `StoneSpire` | hero | W01 owns `RockSpire` |
| `StoneSpireMain` | the Rock Spire main mesh, bare | the sheet's "(main mesh)"; W01 owns `RockSpireMain` |
| `StoneSpireSideRock` | Rr + its top rosette | "Side Rock (reusable)" |
| `StoneSpireFootRock` | F + its two top sprigs | "Foot Rock (base, front)" |
| `StoneSpireSmallRock` | s2's mesh, bare | "Small Rock (reusable)" |
| `StoneSpireFoliage` | one 7-leaf rosette with its bud | "Foliage Cluster (reusable)"; `*FoliageCluster` is the juniper's |

- Palette keys `m039_*` (§5.4). Collection `Kit/M039 Rock Spire`.
- Collision tags: hero `"hull"` (a landmark players walk round, as W01's RockSpire); Main, SideRock, FootRock `"hull"`;
  SmallRock `"hull"`; Foliage `"none"`.

**Decisions needed (a recommendation each):**
1. **Size** (§1.1): **14.0 W × 10.5 D × 11.0 H, the spire 2.0 characters** (recommended: a landmark one class under W01's
   13.0-tall spire, readable leaves), or W01's class (H 13.0 → about 16.5 × 12.2 × 13.0, the same size as the existing
   `RockSpire`), or a compact 8.5 H (10.8 × 8.0 × 8.5, leaves 0.45–0.65).
2. **Layout** (§3.1–§3.4): **the f34 / front composition governs**; r34 compared as a front-left view (az −30); side and
   rear judged loosely as front redraws; the top as a re-composition (recommended).
3. **Back dressing** (§3.4, §3.6): **dress the back with the exploded's medium dome, a back-right medium rock, a
   back-left small rock and a three-rosette mound** (recommended: "consistent geometry across all views", the top cell's
   rear mound and back-right rock, the exploded's two extra rocks), or leave the back bare (the rear and top renders
   would show a bare spire back).
4. **Spire construction** (§1.4): **an explicit 6–7-sided obelisk with aligned rings, long planar faces, a diamond facet
   and a 3–4-face cap** (recommended), not `K.hull_rock` with random ring offsets.
5. **Spire and pillar proportions** (§3.5): **the hero's (spire base W/H 0.40; pillar 3.9 × 7.7)** (recommended), not the
   exploded's squatter drawings (0.56; 0.79).
6. **Hero packaging:** **one hero object holding separate closed shells: each rock, each leaf and each bud its own closed
   solid; rocks interlock by overlap, no booleans** (recommended: the sheet's "simple interlocking planes" and "Foliage
   is a separate mesh"; same rule as M035/M036/M038). Every shell closed and manifold, 0 bowties, 0 self-intersections
   inside a shell; shells may interpenetrate as listed in §6 but share no faces; `problems` reports any shell that isn't
   closed.
7. **Exports:** **the hero plus 5 parts** (`…Main`, `…SideRock`, `…FootRock`, `…SmallRock`, `…Foliage`) (recommended: the
   exploded's five labelled kinds).
8. **Stage 5/6:** **no emission, light or VFX** (recommended: the sheet shows none).
9. **Comparison cameras** (recommended, §3): `f34_sheet (0, 20)` (probe 15 / 20 / 25) and `front_sheet (0, 18)` (probe 14
   / 18 / 22) governing; `r34_sheet (−30, 20)`, kit `side (90, 10)`, `rear_sheet (180, 15)` and the kit top loosely;
   extras: the parts shot (0, 25), `spire_cu`, a FootRock-from-below shot (e −35), `junc_cu (0, 12)` and a scale shot
   with a 5.5-stud marker. Hide the floor in every `*_sheet` render.
10. **Colour:** **one pale warm stone (R > G > B, hue 19–24°) with broad light patches high and warm-deep patches low,
    faint olive stains by the rosettes, three-role lime leaves and a yellow-lime bud** (recommended); never the lavender
    swatch, nothing by facing.
11. **Olive moss stains** (§5.3): **include, faint (≤ 20 % mix on whole facets)** (recommended: the f34 pillar, the
    exploded side rock and foot rock show them), or leave them out for plain stone.
12. **Names** as proposed.

## 9. Pitfalls to avoid

1. **Mauve rocks.** "Rock Shadow" `#9B949E` is B > R > G: it is the shade light, not the stone. Every rock key R > G > B,
   hue 14–26°, R − B ≥ 30. M031 failed round 1 on exactly this; check the side and rear medians too.
2. **Rock that dominates the share / foliage too sparse.** Rock 77.3 % and green 22.7 % in the f34 (±4): the rosettes fill
   every crevice of the lower 60 % (green 24–35 % in the lower two fifths). Too few rosettes reads as bare rock; rosettes
   above h .82 or on the spire's upper shaft are wrong (top fifth ≤ 3 %).
3. **Soccer-ball or icosphere rocks.** Big irregular flat facets with slivers next to broad faces; meet every §2.2 number
   (facet counts, largest facet, area and edge CV, valence spread, flat floors). No subdivision, no bevel modifier, no
   smooth shading. The spire especially: long planar faces, not a hull of jittered rings.
4. **A slim or a fat spire.** Base W/H 0.38–0.42 (W01's round 2 failed on "slim spire"; the exploded's 0.56 is too fat);
   visible width at h .72 0.19–0.25 W in the f34_sheet.
5. **Round boulders as shoulders.** The pillar and Rr are flat-topped, steep-sided tapered blocks (W01's round 2: "shoulders
   as round boulders"); only the foot rock is a dome.
6. **A collar.** This sheet has no foot collar ring (that was W01's subject); the foot is separate rocks of varied size,
   the foot rock dominant in front.
7. **Colour by facing.** The peach-lit / lavender-shade split is light. Patches by noise fields and height, stains by
   distance to rosettes, leaf roles by position; `K.check` facing correlation < 0.5.
8. **Bowties.** Rosette hubs (seven leaves and a bud meeting at a root) are where 019–021 grew bowtie vertices: keep each
   leaf and bud its own closed shell, `M.fix_bowties` on every object, `nonmanifold_verts` 0.
9. **Dense clover mounds or flowers.** Each rosette is 6–7 broad oval leaves round a lime bud, an upright back leaf; no
   white flowers, no 18-leaf three-tier `K.clover` defaults (W01's minor: "clover clumps chunkier than the master's small
   rosettes").
10. **Floating or lone rosettes.** Every rosette sits in a crevice or on a rock top against a taller rock; roots on a
    surface; flank rosettes conformed.
11. **Copying the r34, side, rear or top as true cameras.** They are a front-left view and front redraws / a
    re-composition (§3.2–§3.4).
12. **Gaps at the interlocks.** Rocks press into each other (§6); a visible slit of background between P and S or S and Rr
    in the f34_sheet is a fail.
13. **Budget.** Foliage is about 80 % of the count; don't spend tris on hidden back leaves; never thin a rock below §2.2.
14. **Name clashes** with W01 `RockSpire*`, M033 `MossBoulderSideRock`, `*FoliageCluster`, `*FootRock` (§8). Only one agent
    drives a Blender session at a time; no commits, pushes or exports in stage agents; don't edit `lib/vfx.py` or the
    shared helpers (frozen).

## Decisions (main session, 2026-10-29)
All the study's recommendations are accepted.
1. **Size:** 14.0 W × 10.5 D × 11.0 H, one size class under W01's `RockSpire`.
2. **Governing views:** the front three-quarter and front cells. Compare the rear three-quarter as a front-left view at about −30°; judge the side, rear and top loosely.
3. **Back dressing:** the spare medium dome, a back-right rock, a back-left small rock and a three-rosette mound.
4. **Spire:** an explicit 6–7-sided obelisk with long flat faces, one diamond facet and a 3–4-face cap. No `K.hull_rock` with random ring offsets.
5. **Proportions:** the hero's (spire base width-to-height 0.40, pillar 3.9 × 7.7), not the exploded drawings.
6. **Packaging** (as for M035, M036 and M038): one hero object made of separate closed shells.
   - Rocks overlap where they meet (at most 0.6) with no booleans; each leaf and bud is its own solid.
   - Every shell is manifold, with 0 bowties and no self-intersections inside a shell.
7. **Exports:** the hero `StoneSpire` plus `StoneSpireMain`, `StoneSpireSideRock`, `StoneSpireFootRock`, `StoneSpireSmallRock` and `StoneSpireFoliage`.
   - Collision: hero `none`, the rock parts `hull`, Foliage `none`.
8. **Lighting and VFX:** none. Stages 5 and 6 are recorded as skipped.
9. **Cameras:** as listed in the study. Probe once, then fix them; hide the floor in comparison renders.
10. **Colour:** one warm stone (red > green > blue, hue 19–24°), lighter high and deeper low, blended by position, never by facing.
    - Rosette leaves come in three tiers with a yellow-lime bud.
    - Never use the lavender `#9B949E` swatch as a colour.
11. **Moss stains:** faint olive moss stains, at no more than 20 % mix on whole faces near rosettes.
12. **Names:** `StoneSpire*`, with keys `m039_*`.

The front three-quarter share targets in §1 are binding, within ±4: 77.3 % rock and 22.7 % green, with almost no green in the top fifth.
