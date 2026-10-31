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
`<temp>\3f83a1be-3b3d-4e4b-ae5a-7b04dbb75bdc\scratchpad\m039_study\`.
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

## Stage 1 — Modelling (modeller, 2026-10-29)

Builder `art/blender/kit/mcp/m039.py` (`build()`), background Blender on port 9880, work file
`art/blender/assets/kit/wip/M039.blend`. It imports only the committed `m033` / `m012` helpers; the m036 / m038 helpers
it needs are copied in, so an uncommitted builder can't change it.

- **Spire (`_spire`, decision 4):** an explicit 7-sided obelisk.
  - One shared base polygon (angles ±6°, radii ±6 %), rings at h 0 / .12 / .60 / .89 with scales .90 / 1.0 / .76 / .46.
    Every band quad is a planar trapezoid, so long flat faces run up the shaft.
  - Apex 0.5 to −X and 0.2 to −Y of the base centre.
  - The front vertex of the .60 ring is pushed in 13 % (the diamond facet: the four triangles round it pivot on it); one
    back vertex of the foot ring is tucked in 6 %.
  - Cap: 4 faces (three cap-base verts lowered onto the planes through the apex and their major neighbours). Flat floor
    fan. 54 tris.
  - The ring heights were tuned from .15 / .52 / .88 to .12 / .60 / .89 to bring triangle-area CV to ≥ 0.6.
- **Pillar P and Side Rock Rr (`_side_rock`):** 6 verts a ring, rings h 0 / .12 / .55 / .92 / 1.0 at .90 / 1.0 / .82 /
  .60 / .55 of a shared polygon, a flat top ring (P slopes 7° to the front, Rr 4°), the upper rings leaned (P +0.3 X
  toward S; Rr −0.9 X, 10° toward S), a little in-plane jitter on the middle rings (more on Rr, for its medium-sized
  faces). 56 tris each.
- **Hull rocks (`_hull_rock`):** F, BL, FL, FR, s1–s3, the back dome BD, back-right BR, back-left small BS.
  - Unit point clouds of rings (angle jitter 0.45), flattened by cut planes into big flat facets (m038 method).
  - 2–4 "chip" points just inside an upper point give small chip facets beside the broad ones (irregular triangle
    sizes).
  - A flat top ring tilted toward the front (FR / BR 16° toward the front-right); then yawed and scaled to exact size.
  - F gets its nose vertex after the cuts (pushed 0.32 of the half-width forward), so five big faces meet at it; its
    floor ring is at 0.74 so it is widest at h .55.
- **Layout (spec 2.1):** as the table, except P moved to (−1.82, 0.35) so it overlaps S by 0.59 (≤ 0.6). Every rock is
  its own closed shell; no booleans.
- **Rosettes (`_rosette`):** 3–7 broad oval leaves from one root plus a bud.
  - Leaf (`_leaf`, 12 tris): outline 2 points a side and a blunt tip, a raised two-point midrib, a flat underside fan;
    width 0.74 of the length; length 0.48 of the rosette width.
  - Roles: one upright back leaf (60°), two side leaves (42°), low front leaves (22–28°).
  - Bud: a 6-sided double cone (12 tris) sunk in the hub.
  - Flank rosettes tilt their axis 0.45 toward the flank's outward normal and face out of the flank.
- **Clusters (`CLUSTERS`):** 14 groups, 40 rosettes, every table width × `ROS_SCALE` 1.4.
  - Seats: ground; rock top (ray down); rock flank (horizontal ray); or "l", on the rosettes already built under it
    (stacked mounds).
  - The study's 21 rosettes at 1.2–2.2 across gave f34 green 7 % (sheet 22.7 %). The sheet's groups are stacked mounds
    of 2–5 rosettes, so C1, C2, C6, C7, C9 and C10 are stacks, and C3 and C5 got second rosettes on F's top.
- **Hero size:** 14.43 W × 10.50 D × 11.00 H (target 14.0 ± 0.6 × 10.5 ± 0.8 × 11.0 ± 0.3).

## Stage 2 — Optimisation and cleanup

- **Tris:** hero 3844 (rocks 544, 235 leaves 2820, 40 buds 480; limit 4000). Parts: Main 54, SideRock 152, FootRock 180,
  SmallRock 30, Foliage 96 (limit 1000).
- **Every object:**
  - 0 non-manifold edges, 0 non-manifold (bowtie) verts, 0 boundary or wire edges, 0 loose verts;
  - 0 zero-area faces, 0 n-gons, 0 duplicate verts;
  - normals outward; no corner under 5° (hero min 5.2°; 8 slivers forced open by `m012._force_slivers`);
  - transforms applied, no custom normals, origin at the bbox bottom centre (offset 0, 0, 0).
- **Per shell** (`shells_report`): all 288 hero shells closed and manifold, with 0 self-intersections, 0 inverted faces
  and positive volume.
- **Shells:** hero 288 = 13 rocks + 235 leaves + 40 buds (decision 6).
- **Rock overlaps** (convex-hull depth): S–P 0.59, S–Rr 0.55, P–F 0.11, FL–s1 0.03.
- **Rock gaps:** S–BD 0.04, Rr–FR 0.06, F–FL 0.12, BL–FL 0.30, P–BL 0.35. S–F 1.07 and Rr–F 1.19 are the C5 / C6 crevices,
  filled by rosettes.
- **No floating dressing** (`contact_report`):
  - Hero: 0 floating shells (gap > 0.03), max dressing gap 0.000, 0 unchained at 0.03 and at 0.05; `settle` moved 0
    groups.
  - SideRock, FootRock and Foliage: also 0 floating and 0 unchained.
  - The guard pushed leaves out of rocks 127 times; 21 leaves were dropped (more than 0.4 inside a rock).

### Rock-shape targets (spec 2.2), hero rocks

| Rock | Tris | Area CV | Edge CV | < 25° share | Regions 5° / 7° (largest) | Widest h | Floor span | Top faces (span) | Walls |
| --- | --- | --- | --- | --- | --- | --- | --- | --- | --- |
| S | 54 | 0.68 | 0.59 | 0.47 | 19 / 16 (0.36) | .15 | .90 / .90 | apex | 0.95 |
| P | 56 | 0.73 | 0.51 | 0.33 | 18 / 13 (0.36) | .15 | .94 / .95 | 4 (0.58) | 0.96 |
| Rr | 56 | 0.71 | 0.47 | 0.29 | 18 / 16 (0.35) | .15 | .81 / .87 | 4 (0.49) | 0.88 |
| F | 48 | 0.62 | 0.39 | 0.26 | 23 / 19 (0.20) | .55 | .88 / .72 | 2 (0.57) | 0.60 |
| BL / FL / FR | 40 / 42 / 42 | .65 / .67 / .62 | .44 / .43 / .41 | .41 / .31 / .41 | 17/16, 13/12, 16/15 | .35 / .35 / .45 | | 2 / 2 / sloped | |
| BD / BR | 46 / 42 | .53 / .66 | .33 / .41 | .21 / .46 | 19/16, 14/14 | .45 | | 2 / 2 | |
| s1 / s2 / s3 / BS | 30–34 | .44–.61 | .30–.39 | | 10–16 | .35–.45 | | 1–2 | |

- Spire: 14 faces taller than 0.35 H; 14 faces ≥ 2.5 sq studs; smallest face 0.68 sq studs; widths per height .96 1.0
  .95 .90 .85 .80 .71 .59 .47 .19.
- Our region counts run above the facets.py targets: those are colour regions on the sheet, ours count every 5° / 7°
  normal break.

## Stage 3 — UV

Smart UV (angle 45, margin 0.008) per object; `m012._uv_unfold` found nothing to cut.
- Hero: 1753 islands, 0 overlaps, 0 flipped, min gap 0.016, border 0.008, even density (1.0 / 1.0 / 1.0), conformal
  stretch p95 1.0.
- Every part the same (p95 ≤ 1.06). The exporter writes its own palette UVs.

## Stage 4 — Materials, colour and texture

- **Calibration** (`m039.calibrate()`: K.calibrate on the test dome against spec 5.4's targets):
  - Kept: leaf `#698201` → (126,154,6), leaf_light `#9FA906` → (198,205,10), leaf_deep `#446401` → (78,115,6), bud
    `#96A201` → (186,196,7), stain `#706D3A`, rock_deep `#917E73` → (183,153,133).
  - **Rejected:** rock `#9C8981` and rock_light `#AB9C94`. They render right but have R − B 27 / 23 < 30, so they fail
    the warm-stone guard.
  - The rock keys were then set by hand inside the guard (R > G > B, hue 20–21°, R − B 32–33) and tuned on the
    f34_sheet render. The leaf keys were lifted about 7 % (sRGB) toward the sheet's f34 leaves.
- **Final palette:** rock `#B6A095`, rock_light `#CAB4A9`, rock_deep `#9F8A7F`, moss_stain `#706D3A`, leaf `#718A01`,
  leaf_light `#ACB306`, leaf_deep `#496A01`, bud `#96A201`. Never `#9B949E`.
- **Blend (by position, per flat facet):**
  - rock_light up to 30 % on noise patches above 0.55 of each rock's height; on the spire 35 % above .62 H and at least
    23 % on the cap;
  - rock_deep up to 20 % on patches whose centre is below 1.5;
  - moss_stain 10 / 20 % on whole facets below 2.5 within 1.6 of a rosette root (stained facets: P 6, Rr 7, F 10, BL 12,
    FL 19, s1 25, s2 18, s3 17, …). With the stains off, the f34 rock median doesn't move;
  - leaves by role: low front leaves leaf/leaf_deep 40 %, side leaves leaf, the upright back leaf leaf/leaf_light 67 %;
    C4 and C10 one step lighter; a hard edge to the bud;
  - nothing coloured by facing.
- **Texture:** Tint ±0.04 per flat facet (scale 0.3) and ±0.04 per rock; leaves 0.04 per cluster; buds none.
- **Finish:** rock rough 0.9, metal 0; leaves rough 0.85, low specular; bud rough 0.75, low specular.
- **Re-measured** (final renders, spec masks; ours / sheet):

| Cell | W : H | Rock / green % | Green fifths, bottom → top | Rock median | Lit quartile | Green median | Top profile mean / max | Width per height mean |
| --- | --- | --- | --- | --- | --- | --- | --- | --- |
| f34_sheet (0, 20) | 1.136 / 1.138 | 76.5 / 23.5 (77.3 / 22.7) | .369 .408 .105 .103 .015 (.33 .45 .126 .092 .002) | `#C8AA96` / `#C9AD9C` | `#F0CDB6` / `#E5C9B5` | `#829B09` / `#8FA304` | 0.045 / 0.14 | 0.020 |
| front_sheet (0, 18) | 1.145 / 1.112 | 77.2 / 22.8 (76.9 / 23.1) | .378 .400 .105 .103 .014 | `#C8A996` / `#CAAE9D` | | `#829B09` / `#93A406` | 0.059 / 0.16 | 0.029 |
| r34_sheet (−30, 20) | 0.977 / 0.997 | 76.0 / 24.0 (80.6 / 19.4) | .25 .52 .10 .12 .01 | `#E0BFA9` / `#B89E91` | | `#8BA109` / `#8CA404` | 0.059 | 0.063 |
| side_sheet (90, 10) | 0.835 / 0.867 | 82.8 / 17.2 (81.0 / 19.0) | | `#B19A89` / `#C2A99D` | | | 0.125 | 0.095 |
| rear_sheet (180, 15) | 1.156 / 0.969 | 90.7 / 9.3 (76.9 / 23.1) | | `#BDA497` / `#CAAC99` | | | 0.070 | 0.075 |
| top_sheet (0, 89) | 1.356 / 1.046 | 56.9 / 43.1 (68.0 / 32.0) | | `#D3B8A6` / `#BFA495` | | `#7A9706` / `#799209` | 0.110 | 0.168 |

- f34 rock median: hue 24°, sat 0.25, R > G > B; off the sheet by 1 / 3 / 6. f34 leaves: hue 70°, sat 0.94.
- Parts shot (az 0, e 25; floor shadow excluded with sat ≥ 0.10), ours (target):
  - rock `#CDAF9B` (`#C5A896`);
  - Main `#CEAF9B` (`#C5A997`); SideRock `#C8A996` (`#C7A997`);
  - FootRock `#DFBFAA` (`#C7A997`); SmallRock `#D6B6A1` (`#C4A999`);
  - Foliage `#899F09` (`#769705`).

## Stage 5 — Lighting: skipped

The sheet shows no glow, light or emissive part (spec 7.1, decision 8), so there is no emission anywhere.

Studio check (Requires Manual Validation):
- the rock stays warm grey-pink under the game's sun (not lilac, not orange);
- the spire's flat faces read as separate planes (flat shading kept);
- the leaves stay lime, not olive.

## Stage 6 — VFX: skipped

Stage 6 skipped: the sheet shows no effect (spec 7.2, decision 8). No object has a socket (`build()` checks this).

## Renders

In `art/blender/renders/models/M039/`:
- `M039_views.png`: the kit front34, rear34, front, side, rear, top and underside; then the `*_sheet` shots, the five
  part shots, `parts`, `foot_under`, `exploded` and `scale`.
- `spire_cu.png`: the cap, with no floor.
- `junc_cu.png`: C6 in the F / S / Rr crevice.

`m039.compare()` re-measures every cell against the sheet.

## Modeller's notes for the verifier

- **Governing views:** f34_sheet (0, 20) and front_sheet (0, 18). I didn't re-run the elevation probe: e 20 / 18 gave
  W : H 1.136 / 1.145 against 1.138 / 1.112 and profile means 0.045 / 0.059, so I kept them.
  - r34_sheet is the sheet's "rear three-quarter" taken as a front-left view (az −30).
  - side, rear and top are judged loosely (front redraws and a re-composition).
- **Known misses:**
  - Rear (180, 15): green 9 % against the sheet's 23 %. The sheet's "rear" is a front redraw; our true back shows the
    B1–B3 rosettes and the bare back of the spire.
  - Top: W : D 1.36 against 1.05, and green 43 % against 32 % (a re-composition, spec 3.4).
  - f34 top profile: max error 0.14, at f .50 (our spire's left flank is a little lower than the sheet's in that column)
    and at f .80 (C10's upper rosette).
  - Parts shot:
    - the FootRock and SmallRock part medians run 18–24 levels light, because their big flat tops face the key light at
      e 25;
    - the Foliage part is `#899F09` against the exploded clusters' `#769705`. The hero's f34 leaves govern and are still
      13 levels under the sheet, so the leaf keys can't go darker.
  - Rr measures 3.11 wide (target 2.8 ± 0.2) because its 0.9 lean adds to the width. P is 3.72 × 7.80 (target 3.9 × 7.7).
  - The rock's shade quartile is a warm brown-grey (`#917D70`) where the sheet's is lavender (`#756C70`). That is the
    sheet's cool sky fill, not paint (spec 3.7); nothing is coloured by facing.
- **Budget:** 3844 / 4000, so there is little room left; each extra rosette costs about 90 tris.
- **Rosettes:** there are more and bigger rosettes than in the study's table (40 against 21). The share targets are
  binding, and the table's sizes gave 7 % green.

## Verification round 1 (verifier, 2026-10-29)

Fresh verifier, read-only, background Blender on port 9880 (`wip/M039_verify.blend`). Every number below was re-measured
with my own bmesh / BVH code (`mesh_check.py`, `check2.py`) and my own renders of the six `*_sheet` cameras (into the
scratchpad, `M.MODEL_RENDERS` redirected), with side-by-side crops against the sheet cells. The part shots and close-ups
are the modeller's renders.

### Measured

| Check | Result | Target | |
| --- | --- | --- | --- |
| Tris hero / Main / SideRock / FootRock / SmallRock / Foliage | 3844 / 54 / 152 / 180 / 30 / 96 | < 4000 / < 1000 | ok |
| Hero size | 14.43 × 10.50 × 11.00 | 14.0 ± 0.6 × 10.5 ± 0.8 × 11.0 ± 0.3 | ok |
| Part sizes | Main 4.40 × 3.80 × 11.00; SideRock 3.11 × 2.68 × 5.85 (rock 5.15 H); FootRock 5.00 × 3.80 × 4.30 (rock 3.70 H); SmallRock 1.40 × 1.20 × 1.00; Foliage 1.84 × 1.74 × 0.99 | §1.4 | Rr W +0.11 over 2.8 ± 0.2 |
| Shells | hero 288 (13 rock, 235 leaf, 40 bud); SideRock 9; FootRock 12; Foliage 8; Main and SmallRock 1 | decision 6 | ok |
| Every shell closed and manifold (all six objects) | 0 open shells, 0 non-manifold edges, 0 bowtie verts, 0 boundary, 0 wire, 0 loose, 0 zero-area, 0 n-gons, 0 duplicate verts | 0 | ok |
| Self-intersections inside a shell | 0 pairs in 0 shells (all six objects) | 0 | ok |
| Normals | every shell positive volume (outward); flat shaded; no custom normals; min corner 5.2° (hero) | | ok |
| Origin / transforms | bbox bottom centre offset (0, 0, 0) on all six; rot 0, scale 1; no modifiers; UVMap present | | ok |
| Rocks grounded | all 13 rock shells reach z 0 (floor-cut) | | ok |
| Floating dressing (own code: shell-to-shell BVH overlap or vertex–surface distance, ground at z ≤ 0.03) | **0 floating at 0.03, 0 unchained** (hero, SideRock, FootRock, Foliage) | 0 | ok |
| Rock overlaps (convex-hull SAT, face + edge-cross axes) | **S–P 0.625**, S–Rr 0.545, P–F 0.19, S–BD 0.04, FL–s1 0.03; deepest vertex S–P 0.571 | ≤ 0.6 | S–P 0.025 over |
| Dressing cut into rocks (ray-parity inside test) | 24 of 275 leaf/bud shells > 0.05, 16 > 0.10, 10 > 0.20, max 0.38; 0 fully buried | ≤ 0.05 (§2.3, §6) | minor |
| Spire | 7 verts on each of rings z 0 / 1.3 / 6.6, 3 lowered cap-base verts at 9.0–9.2, 4 at 9.8, apex 11.0; 15 band pairs exactly coplanar; 14 faces taller than 0.35 H; 16 faces ≥ 2.5 sq studs; smallest 0.68 | 6–7 sides, long flat faces, 3–4-face cap | ok |
| Colour by facing | rock face key luminance vs normal z r = 0.13 (x −0.01, y 0.05); vs relative height r = 0.35; `K.check` problems [], `kit_baked_shading` 0.0 on all six | < 0.5 | ok |
| Tint | corner Tint 0.93–1.07, sd 0.024, 131 levels | visible, not confetti | ok |
| Rock area by mix | rock 62.6 %, light mixes 14.5 %, deep mixes 7.8 %, moss 10 % 13.9 %, moss 20 % 1.2 % | stains ≤ 20 % mix | ok |
| Leaf tiers (faces) | deep-40 1272, leaf 948, light-67 540, leaf_light 60, bud 480 | three tiers + bud | ok |
| Lighting / VFX | no children, no sockets, emission 0 on every material | none (decision 8) | ok |
| Collision tags | hero none; Main / SideRock / FootRock / SmallRock hull; Foliage none | decision 7 | ok |

**Views (my renders, spec masks; ours / sheet):**

| Cell | W : H | Rock / green % | Green fifths, bottom → top | Rock median | Green median | Profile mean / max | Width/height mean |
| --- | --- | --- | --- | --- | --- | --- | --- |
| f34_sheet (0, 20) | 1.136 / 1.138 | 76.5 / 23.5 (77.3 / 22.7) | .37 .41 .11 .10 .015 (.33 .45 .13 .09 .002) | `#C8AA96` / `#C9AD9C` | `#829D12` / `#8FA304` | 0.045 / 0.14 | 0.020 |
| front_sheet (0, 18) | 1.145 / 1.112 | 77.2 / 22.8 (76.9 / 23.1) | .38 .40 .11 .10 .014 | `#C8A996` / `#CAAE9D` | `#829D12` / `#93A406` | 0.059 / 0.16 | 0.029 |
| r34_sheet (−30, 20) | 0.977 / 0.997 | 76.0 / 24.0 (80.6 / 19.4) | | `#E0BFA9` / `#B89E91` | `#8BA214` / `#8CA404` | 0.059 / 0.16 | 0.063 |
| side_sheet (90, 10) | 0.835 / 0.867 | 82.8 / 17.2 (81.0 / 19.0) | .45 .19 .18 .17 .00 | `#B19A89` / `#C2A99D` | | 0.125 / 0.22 | 0.095 |
| rear_sheet (180, 15) | 1.156 / 0.969 | 90.7 / 9.3 (76.9 / 23.1) | | `#BDA497` / `#CAAC99` | | 0.070 / 0.15 | 0.075 |
| top_sheet (0, 89) | 1.356 / 1.046 | 56.9 / 43.1 (68.0 / 32.0) | | `#D3B8A6` / `#BFA495` | | 0.110 / 0.28 | 0.168 |

- My renders reproduce the modeller's table within 0.01 on shares and profiles.
- **Colour, own Pillow sampling:**
  - Swatches: Main `#BBA8A0` (18°), Rock Shadow `#9B949E` (282°, lavender), Highlight `#D3BAAC`, Foliage `#819A1E` /
    `#96AB22` / `#CCCA24`.
  - Rock medians in all four front-family renders are hue 20.5–25.5°, sat 0.20–0.25, R > G > B. **0.0 % of our rock
    pixels have B ≥ R** (sheet 8.9 %, its sky fill).
  - Our shade quartile is `#917D6E` (warm, 26°) against the sheet's `#736B6E` (lavender). That is light, not paint
    (§3.7), as noted.
  - f34 leaves: median `#809C11` (72°, sat 0.89) against `#739103` (73°, 0.98); lit `#BAC416` against `#B6C703`; shade
    `#545E07` against `#335602`. Our shade halves are olive rather than deep green.
  - Bud key `#96A201` (64.5°).

### Findings

1. **Blocker: the Foliage Cluster rosette doesn't read as the sheet's rosette.** This affects the `StoneSpireFoliage`
   part and all 40 hero rosettes.
   - **The sheet:** both the exploded cluster and the hero clumps are soft rounded star-flowers. Each has 6–7 broad oval
     leaves with rounded ends and a small round lime bud in the middle. The silhouette is scalloped and round
     (`z_clusterA.png`; spec §1.4: "broad ovals with a soft rounded point, width 0.60–0.70 of the length").
   - **Ours (`part_foliage.png`, and the f34 and junction crops):** the rosettes are spiky crystal shapes.
     - Each leaf is a kite or diamond: a stem wedge with outline points at 0.24 and 0.68 of the length and a
       single-vertex tip.
     - A high raised midrib (`LEAF_CAMBER` 0.16 L) gives each leaf a pyramid ridge.
     - The upright back leaf stands like a tall pointed shard.
     - The bud is a 6-sided double cone whose apex sits at 1.45 r, so it reads as a spike, not a round bud.
   - **Scale:** the rosettes are scaled ×1.4 and stacked, 2.2–2.8 across. They reach the share, but in the f34 and front
     views the groups read as piles of pointed green shards rather than distinct round star rosettes. STAGES says
     "Leaves are rounded clumps, not pointed ladders."
   - **Fix target (keep about 12 tris a leaf; the budget is 3844 / 4000):**
     - Reshape the outline into a broad oval: widest at about 0.55–0.65 of the length, and the base wider (≥ 0.6 at
       0.2 L, not a wedge).
     - Make the tip blunt. Either use two tip verts about 0.3 W apart, or move the last outline pair to about 0.8 L at
       0.85 W so the tip angle is ≥ 110°.
     - Drop the midrib camber to ≤ 0.07 L so the leaf reads as a cupped oval, not a pyramid.
     - Make the bud a squat round dome: ring at about 0.5 r, top at ≤ 0.9 r, or a 2-ring dome.
     - The back leaf stays upright but broad and oval.
     - If the broader leaves overshoot the share, bring `ROS_SCALE` back toward 1.2, or drop hidden stacked leaves.
       Keep f34 green within 22.7 ± 4.
   - **Re-check** `part_foliage` against the exploded cluster. Its silhouette should be round and scalloped, with
     screen w/h 0.86–1.05.

2. **Minor: rock overlap S–P is 0.625 by full convex-hull SAT** (deepest vertex 0.571); decision 6 caps it at 0.6. The
   spire's diamond dent makes the hull estimate a little high.
   - **Fix:** move P 0.03–0.05 toward −X, from (−1.82, 0.35) to about (−1.86, 0.35).

3. **Minor: dressing cuts into rocks.** 24 leaf/bud shells sit more than 0.05 inside a rock and 10 more than 0.20 (max
   0.38). The spec allows ≤ 0.05 (§2.3, §6), so these hidden faces waste tris.
   - **Fix:** `DROP_DEPTH` from 0.40 to about 0.15, and push to ≤ 0.05; or re-seat those leaves.
   - Any tris freed help pay for finding 1.

4. **Minor: the foot rock reads boxier than the sheet's dome.**
   - In the f34, front and part shots, its front and left faces stand near vertical under a large flat top. The
     underside shot reads as a box, while the sheet's is a wide low slab (w/h 1.54).
   - The sheet's Foot Rock is a faceted dome: the upper faces slope steadily to a smaller flat top, with a nose vertex.
   - **Fix:** pull the upper ring in, with the top facet at about 0.45–0.50 W and the 0.80 H ring at 0.80–0.85, so the
     upper faces slope about 35–45°. Keep the nose vertex and the flat floor.

5. **Minor (known): rear_sheet green is 9.3 % against 23.1 %, and W : H is 1.16 against 0.97.**
   - The sheet's rear is a front redraw (decision 2: loosely). Our true back shows B1–B3 and the bare spire back.
   - Decision 3's back dressing is present: the dome BD, BR, BS and the three-rosette mound B1.
   - Accepted as a known miss. If finding 1 frees tris, one more back rosette at the P / BD junction would help.

6. **Minor (known): top view.** W : D is 1.36 against 1.05 and green 43 % against 32 %. B1 is not the largest green
   group; the front crevice band is. The sheet's top is a re-composition (§3.4), so this is accepted.

7. **Minor: Rr is 3.11 wide against 2.8 ± 0.2.**
   - The 0.9 lean adds the extra width; the rock itself reads right (flat top, leans toward the spire) and its f34 box
     matches.
   - Accepted. A lean of about 0.7 would bring it inside the tolerance.

8. **Minor: the part shots read light.** FootRock `#DFBFAA` and SmallRock `#D6B6A1` against `#C7A997` / `#C4A999`.
   - Their big flat tops face the key light at e 25. The hero medians are on target within 1 / 3 / 6, so this is
     lighting and accepted.

9. **Minor: the leaf shade halves are olive (`#545E07`, 66°) where the sheet's are deep green (`#335602`, 87°), and the
   f34 green saturation is 0.89 against ≥ 0.93.**
   - **Fix:** take `leaf_deep` a step greener and more saturated, toward `#3F6A01`, while keeping `leaf` value ≥ 0.58.

**Checked and passing:**
- **Spire:** an explicit 7-sided obelisk with long planar band faces, a 4-face cap with a sharp ridge (matches
  `spire_cu`), and a diamond dent at the 0.60 ring. No hull_rock zigzag.
- **Pillar:** flat-topped, steep, tapered.
- **Rr:** flat-topped, leans toward the spire, with C10 climbing the spire's right flank. The r34 shows the lime patch
  on that flank.
- **Rock ring:** BL, FL, FR, the small rocks and the back pieces are chunky faceted rocks. None is a soccer ball or an
  egg, and there are no round shoulders.
- **Foot rock:** the front nose fan is present.
- **Silhouette:** the f34 / front composition, top profile and width per height match the sheet (mean 0.045 / 0.020).
- **Shares:** the f34 share is inside ±4, and the top fifth is green-free (1.5 %).
- **Colour:** one warm stone, never lavender, blended by position with visible Tint mottling, and moss stains at
  ≤ 20 % mix.
- **Lighting and VFX:** none.
- **Decisions:** 1–12 are all followed, apart from the 0.025 overlap excess in finding 2.

**Score: 6.5 / 10.**

**Verdict: FAIL** on finding 1 alone: the rosette part's leaf and bud shapes are clearly unlike the sheet's. Everything
else is minor, and a fix modeller should do 2–4 and 9 in the same pass. Round 2 should re-check:
- `part_foliage` against the exploded cluster;
- the f34 and front shares (±4) and the top fifth (≤ 3 %);
- floating 0;
- tris < 4000.

## Fix round 1 (fix modeller, 2026-10-29)

Fresh fix modeller, background Blender on port 9880 (`wip/M039.blend`). Every change is in `m039.py`. The final numbers
below come from a freshly restarted session: `build()`, then my own checks (ray-parity cut depth per dressing shell,
full convex-hull SAT per rock pair, leaf/bud probe geometry, green colour quartiles). Work file saved.

### Blocker: the rosettes (finding 1)

- **Leaf (`_leaf`, still 12 tris, a closed solid):** a broad oval instead of the kite.
  - 8-point outline: stem; a wide base pair at 0.20 L (0.70 of the max half-width); the widest pair at 0.58 L; blunt
    shoulders at 0.92 L (0.45); a rounded tip point at 0.98 L. Tip corner 137°, shoulder corners 141°; no
    single-vertex spike. Width 0.74 of the length.
  - Midrib: a low crease-ridge from stem to tip, 0.06 L above the rim, falling linearly to the rim, so each half is one
    near-flat plane (a lit half and a shaded half, like the sheet's folded leaves). Round 1: two midrib points at
    0.16 L, a pyramid. The underside is a strip across the midrib (thickness under the midrib, none at the rim).
  - Curl 0.08 (was 0.10).
- **Bud (`_bud`, 14 tris):** a squat two-ring dome: a 6-vert equator at 0.05 r in the hub, a 3-vert top ring
  0.62 r wide forming a flat top at 0.85 r, and a flat floor. Height 0.80 r. Round 1: a double cone with its apex
  at 1.45 r.
- **Back leaf:** pitch 50° (was 60–64°), length 1.0 (was 1.05–1.10). It is the same broad oval, so it stands up as a
  rounded paddle, not a shard.
- **Side and front leaves:** side leaves 34° (was 42–44°); low front leaves 12–16° (was 22–28°). At 22–28° they rose
  straight at the e 18–25 sheet cameras and showed edge-on, as slivers. Now they show as ovals.
- **`ROS_SCALE`:** kept at 1.4. The flatter, broader leaves give f34 green 21.8 %, inside 22.7 ± 4, so there was no
  overshoot to pull back.
- **Foliage part:** `part_foliage.png` (e 25) shows a star of oval leaves round a dome bud. Its silhouette w/h is 1.52,
  shadow included, against the sheet cluster's 0.85: the sheet draws its clusters from well above. So `render_views`
  adds **`part_foliage_top.png` (az 0, e 55)**. There the rosette reads like `z_clusterA`: an upright oval back leaf,
  two side ovals, the lower ring and the bud in the middle, w/h 1.07. The top views of the hero show every rosette as a
  round scalloped star.

### Minors

- **S–P overlap (finding 2):** moving P 0.04 to −X (to −1.86) only brought the full SAT overlap to 0.610. P is now at
  (−1.94, 0.35), 0.12 from round 1, and S–P is **0.581**. P–F is 0.19 and P–BL a 0.23 gap. Nothing else moved.
- **Dressing cut into rocks (finding 3):**
  - `DROP_DEPTH` is 0.15 (was 0.40). A leaf that still cuts deeper than `MAX_CUT` 0.05 after the push is re-tried
    turned and raised (`VARIANTS`: up to ±45° yaw, +45° pitch, 0.8 length) before it is left out. That keeps the share
    (only 14 leaves left out, 7 of them in C2's triple crevice; 55 kept on a re-try).
  - The guard now tests per rock with ray parity. One BVH over overlapping rocks plus a nearest-normal sign test
    misread points by rock edges, and a C2 bud sat 0.23 inside FL.
  - Ground roots that start inside a rock's foot slide out horizontally.
  - Buds are pushed out, and raised along the rosette axis if a crevice holds them.
- **Foot rock (finding 4):** rings are now (0, .74) (.55, 1.0) (.80, .84) (1.0, .47); they were (0, .74) (.50, 1.0)
  (.76, .86) (1.0, .55).
  - The top facet (normal z > 0.97) is now **0.49 W** across (was 0.57), and the top band slopes **39°** (was 61°).
  - Area CV is 0.65 (spec ≥ 0.6). Widest at h .55. The nose vertex is kept.
  - It reads as a faceted dome in `part_footrock` and the f34.
- **Leaf colour (finding 9):** `leaf_deep` is `#386E03` (92°), was `#496A01`. The requested `#3F6A01` rendered a
  median per-pixel leaf saturation of 0.922; `#386E03` gives 0.943.

### Before → after

| Check | Round 1 | Fix round 1 | Target |
| --- | --- | --- | --- |
| Leaf outline | kite, single-vertex tip | oval, tip 137° / shoulders 141°, base 0.70 of max width at 0.2 L, widest at 0.58 L | tip ≥ 110°, base ≥ 0.6 |
| Midrib camber | 0.16 L (two points) | 0.06 L (crease-ridge) | ≤ 0.07 L |
| Bud | double cone, apex 1.45 r, 12 tris | two-ring dome, top 0.85 r, 14 tris | top ≤ 0.9 r |
| Back leaf | 60–64°, 1.10 L, pointed | 50°, 1.0 L, oval | no tall pointed leaf |
| Hero tris | 3844 (235 leaves, 40 buds) | **3984** (544 rock, 240 leaves × 12, 40 buds × 14) | < 4000 |
| Part tris Main / SideRock / FootRock / SmallRock / Foliage | 54 / 152 / 180 / 30 / 96 | 54 / 154 / 184 / 30 / 98 | < 1000 |
| f34 rock / green | 76.5 / 23.5 | **78.2 / 21.8** | 77.3 / 22.7 ± 4 |
| f34 green fifths | .37 .41 .11 .10 .015 | .39 .39 .11 .11 **.004** | top fifth ≤ 3 % |
| front rock / green | 77.2 / 22.8 | 79.0 / 21.0 | 76.9 / 23.1 ± 4 |
| f34 W : H, profile mean / max, width/height mean | 1.136, .045 / .14, .020 | 1.134, .041 / .12, .022 | 1.138 |
| front W : H, profile mean / max | 1.145, .059 / .16 | 1.142, .070 / .18 | 1.112 |
| r34 green, W : H | 24.0, 0.977 | 22.1, 0.977 | 19.4 (loose) |
| Floating shells / unchained (0.03, 0.05) | 0 / 0 / 0 | **0 / 0 / 0** (all six objects; max dressing gap 0.011) | 0 |
| Dressing shells > 0.05 in a rock (> 0.10, > 0.20), max | 24 (16, 10), 0.38 | **0 (0, 0), 0.029** (hero, 280 shells); parts max 0.024 | ≤ 0.05 |
| S–P overlap (full SAT) | 0.625 | **0.581** | ≤ 0.6 |
| Other overlaps (SAT) | S–Rr 0.545, P–F 0.19 | S–Rr 0.545, P–F 0.192, S–BD 0.041, FL–s1 0.03 | ≤ 0.6 |
| Foot rock top facet / top-band slope / upper (> .55 H) slope | 0.57 W / — / 61° | **0.49 W / 39° / 58°** | 0.45–0.50 W, 35–45° |
| Foot rock area CV / edge CV / regions 5° | 0.62 / 0.39 / 23 | 0.65 / 0.39 / 19 | ≥ 0.6 / ≥ 0.35 |
| f34 leaves: median, lit, shade | `#829B09` (sat 0.89 per the verifier) | `#829C0A` h71 s0.94; lit `#C1CA0A`; shade `#515D04` h68 | sheet `#8FA304` / `#D0D205` / `#3B5D03` h83 |
| Median per-pixel leaf saturation (f34) | 0.89 | **0.943** | ≥ 0.93 |
| f34 rock median | `#C8AA96` | `#C8AA96` | `#C9AD9C` |

- **Mesh checks:**
  - Every object and every shell has 0 non-manifold edges, 0 bowtie verts, 0 boundary, wire or loose elements, 0
    zero-area faces, 0 n-gons and 0 duplicate verts. Normals are outward, with 0 self-intersections and 0 inverted
    faces per shell, and no corner is under 5°.
  - Hero shells: 293 (13 rocks, 240 leaves, 40 buds).
  - Origin at the bbox bottom centre, transforms applied.
  - `K.check` reports none; `build()` problems `[]`.
- **UV:** 0 overlaps, 0 flipped, min gap 0.016, border 0.008, even density, conformal stretch p95 ≤ 1.06 on all six.
- **Size:** hero 14.46 × 10.50 × 11.00 (tolerance 14.0 ± 0.6 × 10.5 ± 0.8 × 11.0 ± 0.3).

### Left over

- **Leaf shade hue:** 68° against the sheet's 83°. Our shaded halves are lit by the warm studio fill, the sheet's by a
  cool sky. The lit and median hues match (63° / 71° against 61° / 68°). Nothing is coloured by facing.
- **Budget:** 3984 / 4000 leaves 16 tris spare. Any new rosette needs leaves removed elsewhere.
- **Known misses, unchanged:** rear green 8.3 % (a front redraw on the sheet), top W : D 1.36 with green 45 %, Rr
  3.11 wide, light part-shot rock medians.
- **Junction close-up:** `junc_cu` framing is unchanged. The crevice shows the new oval leaves.

## Verification round 2 (verifier, 2026-10-29)

A fresh verifier, read-only, using a background Blender on port 9880 (`wip/M039_verify.blend`, not saved). I re-measured every number below with my own bmesh, BVH, ray-parity and SAT code (`mesh.py`, `shells.py`, `colgeo.py`). I made my own renders of the six `*_sheet` cameras, the foliage, foot-rock and side-rock parts, `part_foliage_top`, `foot_under`, `junc_cu` and two extra close-ups (`c2_cu` and `c10_cu`), plus 1440 × 1200 renders of f34 and r34. Colour was sampled with Pillow on both images (`col.py`). Everything is in `scratchpad\m039_verify2\`.

### Measured

| Check | Result | Target | |
| --- | --- | --- | --- |
| Tris: hero / Main / SideRock / FootRock / SmallRock / Foliage | 3984 / 54 / 154 / 184 / 30 / 98 | < 4000 / < 1000 | ok (16 spare) |
| Hero size | 14.46 × 10.50 × 11.00 | 14.0 ± 0.6 × 10.5 ± 0.8 × 11.0 ± 0.3 | ok |
| Part sizes | Main 4.40 × 3.80 × 11.00; SideRock 3.11 × 2.68 × 5.72; FootRock 5.00 × 3.80 × 4.20 (rock 3.70 H); SmallRock 1.40 × 1.20 × 1.00; Foliage 1.92 × 1.77 × 0.82 | §1.4 | Rr 3.11 wide (known) |
| Shells | hero 293 (13 rock, 240 leaf × 12 tris, 40 bud × 14 tris); SideRock 9; FootRock 12; Foliage 8; Main 1; SmallRock 1 | decision 6 | ok |
| Mesh, all six objects | 0 open shells, 0 non-manifold edges, 0 bowtie verts, 0 boundary, 0 wire, 0 loose verts, 0 zero-area faces, 0 n-gons, 0 duplicate verts | 0 | ok |
| Self-intersections within a shell (BVH self-overlap, shared-vertex pairs excluded) | 0 in every shell of all six objects | 0 | ok |
| Normals, shading, transforms | every shell has positive volume; 0 smooth faces; no custom normals; min corner 5.2° (hero); origin at bbox bottom centre (0, 0, 0) on all six; rotation 0, scale 1; no modifiers; UVMap present | | ok |
| Rocks grounded | all 13 rock shells have min z 0.000 | | ok |
| Rock overlaps (convex-hull SAT, face and edge-cross axes; deepest vertex) | S–P **0.581** (0.527); S–Rr 0.545 (0.527); P–F 0.192; S–BD 0.041; FL–s1 0.030 | ≤ 0.6 | ok (round 1: 0.625) |
| Floating dressing (own code: BVH overlap or vertex-to-surface ≤ 0.03; ground z ≤ 0.03; chained to a rock or the ground) | hero, SideRock, FootRock and Foliage: **0 floating, 0 unchained**; max dressing gap 0.011 | 0 | ok |
| Leaf and bud cut into rock (ray parity with 3 rays, vertex depth) | hero: 0 shells > 0.03, **max 0.029**; SideRock 0.010; FootRock 0.024 | ≤ 0.05 | ok (round 1: 24 shells, max 0.38) |
| Leaf shape (all 240 hero leaves and the 7 part leaves) | tip corner **138.8°**; stem corner 103°; midrib camber **0.041 L**; width ÷ length 0.74, widest at 0.58 L; L 0.54–1.43 (median 1.05) | tip ≥ 110°; camber ≤ 0.07 L | ok |
| Bud | height ÷ radius **0.80**; top ring 0.62 r (flat 3-vert top); r 0.14–0.31 | squat dome, top ≤ 0.9 r | ok |
| Leaves seen edge-on at the f34 camera (top-face normal within 12° of the view plane) | 67 / 240 (28 % of leaf area); 23 show their undersides; front 33 %, r34 31 % | — | minor 1 |
| f34_sheet (0, 20) | W : H 1.134 (1.138); rock / green **78.2 / 21.8** (77.3 / 22.7); green fifths .387 .394 .105 .110 **.004**; top profile mean 0.041, max 0.12; width per height mean 0.022 | shares ± 4; top fifth ≤ 3 % | ok |
| front_sheet (0, 18) | W : H 1.142 (1.112); 79.0 / 21.0 (76.9 / 23.1); profile mean **0.070**, max 0.18 (spire tip about 0.05 f right; FR end high); width per height 0.029 | ± 4; profile mean ≤ 0.04 | minor 4 |
| r34_sheet (−30, 20) | W : H 0.977 (0.997); 77.9 / 22.1 (80.6 / 19.4); profile 0.059 | loose | ok |
| side / rear / top | side 0.841 (0.867), 84 / 16; rear 1.159 (0.969), 92 / 8; top 1.359 (1.046), 55 / 45 | loose | known misses |
| Foot rock (part, rock shell) | top facet (n z > 0.97, 2 tris) **0.49 W** × 0.29 D; width per height (h .05 → .95) .89 .92 .96 .97 .95 .87 .64, widest at h .55; upper faces (above 0.6 H) slope 17–89°, 9 of 25 between 28° and 47°; 48 tris | top 0.45–0.50 W, sloping upper faces | ok |
| Colour by facing | rock key × Tint against normal z / x / y: r = 0.135 / 0.007 / 0.006; against height r = 0.46 (by position); leaf key against normal z 0.004; `K.check` []; `kit_baked_shading` 0.0 on all six | < 0.5 | ok |
| Tint | corner Tint 0.922–1.072, sd 0.024, 138 levels; one tone per face (5 faces of 3984 non-uniform); 1 of 90 coplanar rock pairs breaks tone; rock-neighbour median difference 0.004 | visible, not confetti | ok |
| Rock area by material | plain rock 63.3 %, light mixes 14.3 %, deep mixes 7.8 %, moss stain at 10 % 13.6 %, moss stain at 20 % 0.9 % | stains ≤ 20 % mix | ok |
| Keys (sRGB) | rock `#B6A095`, moss-stain mixes `#AF9B8C` / `#A89683` (warm), leaf `#718A01`, leaf mixes `#99A504` / `#5A7F02`, leaf_light `#ACB306`, bud `#96A201`; no lavender key | R > G > B rock; never `#9B949E` | ok |
| Lighting / VFX | emission 0.0 on every material; no children, empties or sockets | none (decision 8) | ok |
| Collision tags | hero none; Main / SideRock / FootRock / SmallRock hull; Foliage none | decision 7 | ok |

**Colour (Pillow, the spec's masks; ours / sheet):**

| Cell | Rock median | Rock lit / shade | B ≥ R rock px | Green median | Green lit / shade | Per-pixel green sat |
| --- | --- | --- | --- | --- | --- | --- |
| f34 | `#C8AA96` 24° 0.25 / `#C9AD9C` 23° 0.22 | `#EFCDB6` / `#917E71` (24°) vs `#E5C9B5` / `#756C70` (333°) | 0.000 / 0.057 | `#829C10` 71° / `#8FA304` 68° | `#C2CA16` 63° / `#515D06` **68°** vs `#D0D205` 61° / `#3B5D03` **83°** | 0.90 / 0.98 |
| front | `#C8A996` 23° / `#CAAE9D` 23° | | 0.000 / 0.125 | `#829C10` / `#93A406` | shade `#515C06` 68° vs `#3C5606` 80° | 0.90 / 0.96 |
| r34 / side / rear / top | `#E1C0A9` 25° / `#B29B8A` 25° / `#BDA497` 21° / `#D3B8A6` 24° | | 0.000 each | `#8CA511` / `#72860C` / `#788E0F` / `#739807` | | 0.90–0.96 |
| part_foliage / part_foliage_top | — | | — | `#84A010` / `#829F08` vs exploded `#769605` | | 0.91 / 0.95 |

- Swatches re-sampled: Main `#BBA8A0` 18°, Rock Shadow `#9B949E` 282°, Highlight `#D3BAAC`, Foliage `#819A1E` / `#96AB22` / `#CCCA24`.
- The rock is one warm stone, R > G > B, hue 21–25°, sat 0.20–0.25, never mauve.
- Our shade is warm grey-brown where the sheet's is lavender. That is the sheet's cool sky fill (spec §3.7), not paint.

### The round-1 blocker: the rosettes

- **The Foliage part does now read as the sheet's rosette** (`sbs_fol_top.png` against the exploded cluster at (180,925,250,995)):
  - an upright oval back leaf, two oval side leaves and a lower ring of ovals round a lime bud;
  - a scalloped, round silhouette;
  - no kite outlines, no single-vertex spikes and no double-cone bud.
- **The hero's rosettes are better than in round 1.** The top view shows every rosette as a round scalloped star, close to the sheet's top cell. In the f34, the upright back and side leaves of each rosette read as ovals.
- **The fix modeller's claims were checked and hold:**
  - tip 138.8° (they gave 137°);
  - camber 0.041 L where it counts. They gave 0.06 L nominal; curl lowers it.
  - bud 0.80 r high with a flat top 0.62 r wide;
  - back leaf at 50°;
  - S–P 0.581;
  - maximum cut 0.029;
  - foot-rock top 0.49 W;
  - f34 21.8 % green with 0.4 % in the top fifth;
  - 3984 tris.
- **Not quite right:** the median per-pixel leaf saturation. They reported 0.943; I measure 0.90, using a mask that includes edge pixels. Their figure may come from a tighter mask.

### Findings

1. **Minor: at the governing cameras, the flat low leaf ring still shows edge-on as thin blades.**
   - The low front leaves are pitched 12–16° and the side leaves 34°. The f34 camera is at e 20, so a leaf pointing at the camera is seen about 8° off edge-on.
   - 28 % of leaf area is within 12° of edge-on at the f34 camera (33 % at the front camera), and 23 leaves show their undersides.
   - In the 1440-px f34 (`big/`) and the close-ups `c10_cu` and `c2_cu`, the rosettes of C10 (Rr top and the spire flank), C3 and C5 (F top) and C1 have a skirt of thin pointed green slivers under their oval upper leaves.
   - The sheet's clusters are chunkier and more upright: many small cupped ovals stacked into puffy lime columns, all facing the viewer.
   - It no longer reads as "green shards" overall: the upper leaves are ovals and the top view is right. It is the main difference left against the sheet.
   - **Fix target (if a round 3 or a later polish pass is wanted):**
     - Turn the low ring away from the camera axis, so it is mostly side-facing (az ±60–100°) rather than 18–24° off the face direction.
     - Either droop the front leaves to pitch −5 to 0°, or drop them and give the tris to a second upright tier (pitch 35–55°, facing out).
     - Target: ≤ 12 % of leaf area within 12° of edge-on at f34 (0, 20), 0 undersides showing.
     - Optionally shorten the leaves toward the study's 0.55–0.85 (median L is now 1.05), so the clumps read as many smaller leaves.

2. **Minor: the leaf shade halves still lean olive.**
   - f34 shade quartile `#515D06` (68°) against the sheet's `#3B5D03` (83°).
   - Median per-pixel saturation 0.90 against 0.98 (spec ≥ 0.93 by my mask).
   - The warm studio fill accounts for part of this. The `leaf_deep` mix `#5A7F02` (78°) could go a step greener and darker, toward `#4A7A02`, keeping `leaf` value ≥ 0.58.

3. **Minor: the foot rock is a faceted dome-block rather than the sheet's rounder dome.**
   - The top facet (0.49 W) and the sloped top band are now right.
   - Its sides stay steep: 64 % of the area is wall within 20° of vertical, and 16 of the 25 upper faces slope ≥ 51°.
   - The underside shot still reads boxy.
   - Accepted: it reads as the sheet's foot rock in f34, front and `part_footrock`.

4. **Minor: the front_sheet top-profile mean is 0.070** (round 1: 0.059; target ≤ 0.04). The spire tip sits about 0.05 f right of the sheet's, and the FR end stands higher. f34 is in tolerance (0.041), so this is accepted as the front redraw's offset.

5. **Minor (known, accepted in round 1):**
   - rear_sheet green is 8 % against 23 %, and its W : H is 1.16;
   - the top view's W : D is 1.36, with 45 % green;
   - Rr is 3.11 wide;
   - the part-shot rock medians are light (lighting);
   - the r34's lime patch on the spire flank reads as two separate rosettes, not a patch.

6. **Minor: the loose views' rock hue is 24.6–25.5°** (r34, side), against the spec's 19–24°. It is still clearly warm, R > G > B, with 0 % B ≥ R. No action needed.

**Decisions 1–12:** all followed.
- Size: 14.46 × 10.50 × 11.00.
- Cameras as listed.
- Back dressing: BD, BR, BS and the B1 mound.
- Explicit 7-sided spire: 54 tris, 4-face cap, diamond dent.
- Hero proportions.
- One hero of closed shells: overlaps ≤ 0.6, no booleans, 0 bowties, 0 self-intersections.
- Six exports, named `StoneSpire*`, with the collision tags as decided.
- No light or VFX.
- One warm stone, blended by position, never lavender.
- Moss stains at ≤ 20 % mix.
- Keys named `m039_*`.

**Score: 7.5 / 10.**

**Verdict: PASS.**
- The mesh is clean, under budget and correctly packaged.
- There is no floating dressing, and no leaf or bud cuts more than 0.05 into a rock.
- The silhouette and shares match the governing cells, the colour family is right and set by position, and every decision is followed.
- The round-1 blocker is fixed: the rosettes are oval-leaf stars with a round bud, not shards.
- Finding 1 is the main leftover for the commit notes: the flat low leaf ring shows edge-on at the sheet cameras, so the hero clumps are flatter and thinner-edged than the sheet's puffy upright clusters.

## Main session ruling (2026-10-29)
- **Result:** passed in round 2 (7.5/10) and committed. Round 1 failed (6.5/10) because the rosettes were spiky.
- **Left for a later polish pass:**
  - Low front leaves read as thin edge-on blades at the 20° cameras. Target: turn the low ring to the sides, add an upright 35–55° tier, keep ≤ 12 % of leaf area edge-on, and show no undersides.
  - Leaf shade halves lean olive. Move `leaf_deep` toward `#4A7A02`.
  - The foot rock sides are steep.
  - The front-cell profile mean is 0.070.
  - Budget is tight: 3984 of 4000.
- **Export:** 6 assets, 6 solid pieces, 4504 tris, 0 VFX sockets, palette 17 colours, 0 problems.
