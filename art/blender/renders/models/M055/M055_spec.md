# 055 Fallen Log — spec

Reference: `art/blender/assets/references/055.png` (1024 × 1536 px). INDEX.md row 55: "Fallen Log Model Study". The
sheet's own header reads **"PAGE — 56/132"**, **"56 — FALLEN LOG"**, "FLINTBORN — INDIVIDUAL MODEL STUDY" (our number is
INDEX's 055, §3.1). Builder: `art/blender/kit/mcp/m055.py` → `build()` (not written yet). Procedure:
`art/blender/kit/mcp/STAGES.md`. One modeller does stages 1–6 in a background Blender, then a fresh verifier does
stage 7; the main session puts the model into the kit file, exports and commits.

User direction for every model: shapes must match the sheet; colours "need to match the master reference and blend into
the colors nearby"; every model ships its colour, texture and VFX. **This sheet shows no effect** (§7).

Sheet text (paraphrased where long):
- **Description (top):** a hollow log with a broken end, moss, foliage and surrounding rocks; a deadwood ground asset.
- **Palette (top right, "MATERIAL / COLOR PALETTE"):** six labelled swatches: WOOD A (DARK), WOOD B (LIGHT), MOSS,
  FOLIAGE, ROCK A (LIGHT), ROCK B (DARK).
- **1. "ASSEMBLED VIEW (FRONT 3/4)"**, **2. "ASSEMBLED VIEW (REAR 3/4)"** (the "rear" one actually looks at the hollow
  end from the front-left, §3.2).
- **3. "ORTHOGRAPHIC VIEWS (CONSISTENT GEOMETRY)":** FRONT, SIDE (RIGHT), REAR, TOP. They are not fully consistent
  (§3.3–3.5).
- **4. "EXPLODED CONSTRUCTION (REUSABLE PARTS)":** labels "CUT END (CAP) (Reused Part)", "BRANCH STUB (Reused Part)",
  "MOSS / FOLIAGE (Reused Part)", "ROCK MODULE (Reused Part)", "FOLIAGE CLUMP (Reused Part)". Dashed arrows: cap → the
  log's open end, branch → a socket on the log top, two moss clumps → the log top. A white break line crosses the log
  body at about 0.3 of its length from the open end.
- **5. "CONSTRUCTION CLOSE UPS":** A "HOLLOW INTERIOR (FRONT)", B "BRANCH STUB JUNCTION", C "THICKNESS / CROSS-SECTION"
  ("Shell Thickness (Consistent)").
- **6. "MODELING NOTES":** A style and form (chunky low-poly stylised forms, broad flat-shaded faces, simple clean
  silhouettes, the Flintborn primitive look, no photoreal texture or noise); B colour and materials (warm timber tones,
  simple solid colours, pale faceted rocks, clean moss and foliage shapes, the Flintborn palette); C geometry ("Single
  hollow log shell", "Broken end with cut end cap", "One branch stub (reusable)", "Separate moss/foliage pieces",
  "Separate rock modules (reusable)", "Clean joins and simple topology"); D usage (ground prop / deadwood, reusable
  parts, a recognisable silhouette, consistent style and scale, "No gameplay stats or exact dimensions").
- **Game context and the old kit:**
  - **W05 row 4 `LogAndStump`** (`art/blender/scripts/kit/W05/log_and_stump.py`, goals
    `art/blender/renders/kit/W05/log_and_stump_goals.md`) is the old kit's take on a similar row: hero
    `FallenHollowLog`, a 13.2 × Ø 5.5 hollow log lying along X with a **pale heartwood rim**, a Y branch, moss, rocks.
    `MODEL_PROGRESS.md` row 60: "clean cylinder, flat cap (ref rough bark, cracks); flat moss; stub a block". **W05
    owns `FallenHollowLog` and every `LogAndStump*` name** (`…HollowLog`, `…LogShell`, `…BranchStub`, `…CutEndCap`,
    `…MossFoliage`, `…BrokenLog`, `…LowStump`) (§8).
  - **026 Softwood Log** (`FallenSoftwoodLog*`, committed): a solid 11-sided bark-plate log, Ø 3.2 × 9.3, a pale ringed
    cut end, two stubs, leaf stars. §1.5 keeps 055 apart from it.
  - **Sister sheets:** 053 Dead Tree (`TwistedSnag`, trunk waist Ø 5.0) and 054 Broadleaf (trunk Ø 4.7) are the trees
    this log could have fallen from; 055's Ø 5.0 matches them (§1.1).

**Pixel boxes and masks.** All boxes are sheet pixels `(x0, y0, x1, y1)`, origin top left. Paper `#FAF7F0` (250, 247,
240), tolerance 12. Cell rules (measured grey lines): rows y 20 / 179 / 530–533 / 773–776 / 1348–1351 / 1522; columns
x 12 / 513 / 1012; ortho dividers x 251 / 541 / 747; exploded | close-ups x 731–734; close-up frames y 832 / 1034 /
1068 / 1207.
- **Cells** (`m.V`, `m.X`): f34 (16,209,511,528); r34 (516,210,1010,528); front (16,572,250,745); side
  (254,572,540,745); rear (543,572,746,745); top (749,572,1010,745); exploded (16,800,730,1345); close-up A
  (746,831,1000,1034); B (746,1067,1000,1208); C (790,1250,910,1342). The f34 branch tip touches y 209 (the title ends
  at 208).
- **Swatches** (`m.SW`, all at y 84–129): WOOD A (643–688), WOOD B (705–750), MOSS (767–812), FOLIAGE (829–874), ROCK A
  (890–935), ROCK B (952–997).
- **Masks** are `cls()` in `m.py` (HSV, h in degrees, assigned in this order):
  - **X, cast shadow:** neutral pale grey (s < 0.06, v ≥ 0.78) in components ≥ 120 px that touch the paper. The sheet's
    shadow is `#DEDDDE`–`#D9DADC` (s ≤ 0.05, v 0.85) to the left of every view. Small enclosed pale specks are rock
    highlights and stay R (053's looser X rule ate 5–6 % of the rock here).
  - **G, green:** h 50–180, s ≥ 0.30, v ≥ 0.12 (moss leaves and foliage tufts).
  - **T, wood:** h < 48, s ≥ 0.30, v ≥ 0.12 (log, stave ends, cap, branch, the lit part of the bore wall).
  - **R, rock:** s < 0.30, v 0.22–0.97.
  - **O, other:** the dark bore, deep grooves, outlines.

**Scratch study material** (no Blender) in
`C:\Users\Orang\AppData\Local\Temp\claude\D--Projects-Roblox-RBLX-Flintborn\3f83a1be-3b3d-4e4b-ae5a-7b04dbb75bdc\scratchpad\m055_study\`.
Run with the scratch venv `..\venv22\Scripts\python.exe` (Python 3.14, Pillow, numpy).
- **Helpers:** `m.py` (masks, boxes, swatches, `label()`, `silhouette()`, `preview()`), `zoom.py` (`zoom.py x0 y0 x1 y1
  scale out.png [grid]`).
- **Measurements:** `measure.py` (bbox, W : H, shares, fill, profiles, fifths → `measure_out.txt`), `comps.py` (rock
  and plant blobs in studs at 17.4 px / stud → `comps_out.txt`), `logprof.py` (wood extent per column), `rows.py`
  (wood runs per row: branch angles), `hole.py` (front bore and ring), `ell.py` (bore ellipse in the 3/4 views),
  `samp.py` / `samp2.py` (colour per region, close-ups, exploded parts → `samp_out.txt`, `samp2_out.txt`), `sw.py`
  (swatches), `lines.py` (cell rules).
- **Zooms:** `p_f34.png`, `p_r34.png`, `p_ortho.png` (gridded), `p_expl.png`, `p_cu.png` (gridded); gridded 10 px
  `z_front.png`, `z_side.png`, `z_rear.png`, `z_top.png`, `z_f34end.png` (the open end), `z_f34rocks.png`; mask
  previews `cls_*.png`, `cls_mont.png`.
- **On our renders:** copy 047's `measure_render.py`, point it at this folder's `m.py` (same masks, paper `#FAF7F0`).

## 1. Study (2a)

### 1.1 Classification, what it is, size

- **Classification:** full asset (a ground prop with its own dressing). Hero budget 4000 tris, each part under 1000.
  The plan in §4.3 lands at about 2600–3000.
- **Overall read (check this first).** A **big, chunky, hollow fallen log** lying level on the ground, built like a
  **barrel of about twelve long planked staves** with dark V grooves between them (never a smooth cylinder). Its
  **front end is open and broken**: a ring of twelve **chunky, chamfered stave-end blocks**, staggered in length, round a
  **round, near-black bore** whose planked inner wall shows dark brown for the first stretch. The **back end is closed
  by a cut-end cap**: a disc with radial cracks inside a ring of block ends. **One thick Y-forked branch stub** rises
  from the upper right shoulder just past the middle, its two prongs ending in flat cut faces. **Leafy lime moss**
  (flat lobed leaves in rosettes) mats the top and **drapes down both flanks**; **pale lavender-grey faceted rocks**
  and **spiky lime foliage tufts** line both sides of the base. No ground patch.
  - It reads **wood first, green a strong second**: wood 55–60 % of the 3/4 and side silhouettes, green 25–29 %, rock
    12–14 %.
  - Long and low: W : H 1.50 (f34), 1.76 (side); the branch is the only thing above the log.
- **Focal features, in order:**
  1. The open end: the dark round bore in its ring of chunky staggered blocks (front, f34, r34, close-up A).
  2. The staved barrel body with grooves and the step seam (side, f34, exploded).
  3. The Y branch stub against the sky (every side view).
  4. The moss drapes and the rock and tuft line along the base.
- **Target size (decision §8.1): log Ø 5.0, length 14.2 (open end to cap face), top of the log z 5.0, branch tip z 8.1;
  overall about 11.5 (X) × 14.8 (Y) × 8.1 (Z).** Tolerances: Ø ±0.2, length ±0.4, height ±0.3.
  - **How it was derived.** The orthographic cells share one scale (front, side and rear are 142–144 px tall). The log's
    end is 86–89 px across (front ring 641–727 vertical, rear cap 87–90, side height 637–722 = 85), so **Ø 5.0 gives
    17.4 px / stud**. Then: log length (side, 278–521) 243 px = **14.0** (+ the cap rim and stave stagger, 14.2–14.5);
    L : D **2.8**; branch tip y 591–592 against ground y 731–732 = **z 8.0–8.1**; front W 198 px = 11.4, side W 254 px
    = 14.6, rear W 180 px = 10.3.
  - **Why Ø 5.0.** The log is the fallen trunk of a tree like 053 (waist Ø 5.0) or 054 (Ø 4.7); 026's chop log is Ø 3.2,
    so 055 reads as the bigger, older deadwood. W05's hollow log was Ø 5.5.
  - **Against the character (5.5):** the log top (z 5.0) is at 0.91 C, just under head height: **a player cannot step
    over it; they jump onto it** (Roblox's default jump height is 7.2) **or climb it by the rocks** on the +X flank
    (1.7–2.3 tall, then 2.7–3.3 up), then **walk along the top** from the cap end to the broken end, round the branch
    (it stands on the +X shoulder at Y +1.4, leaving the −X half of the crest clear). The bore (inner Ø 3.4 = 0.62 C) is
    too small to walk through: it is dark decoration. The branch tip (8.1) is 1.5 C.
- **Build frame:** log axis along **Y**, the **open end at −Y facing the front camera**, the cap end at +Y, **+X right**
  (the side cell's flank, with the branch shoulder), ground z 0. The log axis at x 0, z 2.45 (bottom sunk 0.05). Origin
  = bbox bottom centre; the dressing runs about −5.2 … +6.3 in X, so the origin sits about +0.55 X of the log axis
  (record it).

### 1.2 Measured views (`measure.py`)

| View (box) | Silhouette bbox (px) | W : H | T | G | R | O | fill |
| --- | --- | --- | --- | --- | --- | --- | --- |
| Front three-quarter (16,209,511,528) | 38–491 × 209–510 (454 × 302) | **1.503** | **55.7 %** | **27.8** | 12.4 | 4.0 | 0.611 |
| "Rear" three-quarter (516,210,1010,528) | 536–985 × 228–509 (450 × 282) | 1.596 | 55.9 | 29.4 | 11.8 | 3.0 | 0.636 |
| Front (16,572,250,745) | 32–229 × 589–731 (198 × 143) | 1.385 | 44.3 | 22.9 | 15.5 | **17.4** (the bore) | 0.507 |
| Side (254,572,540,745) | 270–523 × 589–732 (254 × 144) | 1.764 | 58.4 | 25.1 | 13.7 | 2.8 | 0.650 |
| Rear (543,572,746,745) | 551–730 × 590–731 (180 × 142) | 1.268 | 60.2 | 23.9 | 13.2 | 2.6 | 0.524 |
| Top (749,572,1010,745) | 770–991 × 589–722 (222 × 134) | 1.657 (W : D) | 42.9 | 35.4 | 20.3 | 1.4 | 0.692 |

- Shares are of the silhouette (O included, X excluded). **Verifier tolerance:** T ±4, G ±3, R ±3 points; W : H ±0.08;
  fill ±0.05; the front O (bore) 17 ± 4.
- **Green split (f34):** moss on the log (G above y 420) 12 284 px, ground tufts (G below y 440) 8 704 px: **the green
  is about 55 % moss on the log, 40 % tufts, 5 % low sprigs.**

**Top profiles** (highest silhouette pixel per column, fraction of H, every 0.1 W):

| f | .0 | .1 | .2 | .3 | .4 | .5 | .6 | .7 | .8 | .9 | 1.0 |
| --- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- |
| f34 | .26 | .54 | .62 | .67 | .69 | .66 | .75 | .91 | .93 | .78 | .21 |
| r34 | .30 | .75 | .76 | 1.0 | .82 | .72 | .68 | .81 | .87 | .54 | .14 |
| Front | .08 | .25 | .39 | .58 | .70 | .70 | .91 | .93 | .47 | .32 | .07 |
| Side | .05 | .66 | .73 | .64 | .98 | .87 | .70 | .62 | .71 | .62 | .06 |
| Rear | .09 | .28 | .40 | .96 | .96 | .84 | .73 | .70 | .59 | .27 | .06 |

**Width per height** (silhouette width at h .0 → 1.0 as a fraction of W):

```
f34    .02 .83 .98 .96 .91 .91 .84 .62 .13 .14 .03
r34    .09 .89 .98 .96 .90 .89 .82 .73 .56 .14 .03
front  .60 .94 .91 .81 .61 .56 .47 .28 .15 .18 .03
side   .67 .96 .96 .97 .96 .95 .93 .63 .15 .14 .03
rear   .69 .93 .88 .81 .67 .58 .49 .41 .16 .18 .04
```

- Reading (side): h .1–.6 the log and its base dressing at full width; h .7 the moss tops on the crest (.63); h .8–1.0
  only the branch (.14–.15 of W). Reading (front): the round end narrows from .94 at h .1 to .28 at h .7; above .8 only
  the branch.

**Height fifths** (bottom → top, % of each class):
- f34: T 10.2 / 34.6 / 36.9 / 12.3 / 6.0; G 30.0 / 20.9 / 27.2 / 22.0 / 0; R 69.8 / 25.0 / 0.3 / 4.1 / 0.8.
- Side: T 7.8 / 44.4 / 32.6 / 10.1 / 5.0; G 34.7 / 10.5 / 38.8 / 16.0 / 0; R 88.9 / 7.0 / …
- **Green sits in two bands** (the ground tufts in fifth 1, the moss on the crest in fifths 3–4); **rock is all in the
  bottom two fifths**; the top fifth is the branch only (5–7 % of the wood).

**Ground dressing blobs** (`comps.py`, ortho cells, studs at 17.4 px / stud; x from the log axis, front x+ = world +X;
rear x+ = world −X):

| View | Rocks | Plants |
| --- | --- | --- |
| Front | −X: low (−3.4…−1.2, h 0.8), taller behind (−4.0…−2.6, top 2.8), pebble (−5.1…−3.8, h 1.0); +X: low wide (+1.0…+4.6, h 1.5), taller behind (+3.7…+5.2, top 3.0) | −X tuft (−4.5…−2.2, 2.0 tall); +X: the moss drape and tufts merge (+1.5…+6.3, to the crest) |
| Side (+X flank; Y from the open end at −7.0) | corner rock (Y −7.2…−5.0, h 1.4); two big rocks merged (Y −3.0…+3.2, top 2.1); small (Y +5.0…+5.7, h 0.4–0.8) | moss + tufts (Y −5.8…−0.2, to z 5.9), moss (Y +1.6…+5.4, crest to z 2.9), tufts (Y +3.0…+7.0, 2.2 tall) |
| Rear | +X: wide low (h 1.6) with a taller one behind (top 2.9–3.3); −X: (−2.6…−3.9, h 1.0) | +X: moss drape on the shoulder; −X: tuft (2.4 tall) |

**Plan (top cell, `z_top.png`).** The log drawn horizontally (§3.5), a rank of grey rocks along both long sides, five
moss rosettes over the top (two big near the left third, one at mid, two smaller near the right end), lime tufts poking
out between the rocks on both sides; shadow lower-left. No branch shows from above (§3.5).

### 1.3 Silhouette and composition per view

**Front three-quarter (`p_f34.png`, `z_f34end.png`) — governs with the front cell.** The camera sits about **50–60° to
the right of the front** (the open end's bore ellipse) and about 15–20° up, with visible perspective (the near end is
173 px tall, the far end about 120). The open end is at left, the log recedes to the right; we see the +X flank.
- **Open end:** a ring of ~12 chunky stave-end blocks, each a **chamfered block with a lit orange end face**
  (`#E48C35`–`#F2A45A`), their ends **staggered** (the right-hand blocks stick out toward the camera more), round a
  **round dark bore**; inside, the **planked inner wall** shows dark brown (`#502A11`) and goes black (`#150B04`) deeper
  in.
- **Body:** 4–5 broad staves across the visible flank, each faceted twice along its length, deep dark grooves between;
  a **step seam** at about 0.3 of the length where the front staves end and the body's staves begin (the exploded's
  white line).
- **Branch:** from the upper shoulder at about 0.6 of the length, a thick planked stub rising up-right at ~51° on screen
  (60 px over 90 up in the cell) to a Y: a long main prong and a short side prong, both with flat lit cut ends.
- **Moss:** a big leafy drape over the crest and down the flank from 0.15 to 0.45 of the length, hanging to about 0.35
  D above the log's bottom; a band of leaves along the crest to the branch; a small drape at 0.75–0.85; a leafy clump
  upright on the far top-back near the cap end.
- **Base:** a tuft and a pebble left of the open end; along the flank a small rock near the open end, a mid rock, a
  **tall rock under the branch**, tall spiky tufts between them and a big tuft group at the far end.

**"Rear" three-quarter (`p_r34.png`).** The **same open end, from the front-left** (bore ellipse w : h 0.69, so about
46° off the front): open end at right, the −X flank facing us, cap end at far left. The big Y branch leans left on
screen (toward the cap end); **a second, smaller Y stub stands near the open end** (§3.4). Moss drape at mid-length on
the −X flank, a leafy clump on the −X shoulder near the cap end; a big rock near the cap end, a mid rock, a small rock
near the open end; tufts between and a big tuft at far left.

**Front / side / rear (`z_front.png`, `z_side.png`, `z_rear.png`).** Low views (e ≈ 0–5°) at one scale (17.4 px / stud
at Ø 5). Front: the open end straight on (outer Ø 87–89 px, bore 72 × 72 px dark core, ring blocks 10–18 px thick),
the branch rising from the upper right shoulder (base x +1.7 off the axis, about 43° round from the top), leaning +X to
two tips at x +2.4 / +3.3, z 8.05 / 7.6; rocks and tufts both sides, the +X ones bigger. Side (+X): the log broadside,
the open end at left (hollow-end moss drape at left, as in the f34), the branch leaning **left** (toward the open end,
§3.3) at ~46°. Rear: the cap face (an outer ring of ~12 blocks over r 0.7–1.0 R, an inner disc with ~9 radial cracks
and a centre), the branch on screen left (+X), leaning +X.

**Close-up A (hollow interior).** The open end close: 12 chamfered blocks with lit end faces and darker chamfers, the
planked inner wall with long plank lines going back, black at depth; moss over the top right, a rock at the foot.

**Close-up B (branch stub junction).** The branch base **flares into the log top**: the stub's long planked facets run
down into a wider collar that sits into the bark (no gap, no pale ring); moss leaves round the foot.

**Close-up C (thickness / cross-section).** A curved wedge of the shell, dark inside face (`#7D4824` median, interior
shade), lit outer face, **the same thickness all round**: one stave thick.

### 1.4 Parts (exploded, `p_expl.png`)

The exploded is an elevated front-right view like the f34 (open end at left). **The hero governs every size and
position** (§3.6); the parts give shapes, counts and joints.

| Part (label) | Box (px) | Notes |
| --- | --- | --- |
| Log shell | (195–700, 960–1180) | the staved barrel, open at the near end showing the planked bore; the **white break line** at about 0.3 of the length; sockets (small dark marks) on the top where the branch and two moss clumps plug in |
| Cut End (Cap) | (40–150, 1040–1190) | a **disc with an outer ring of ~13 chamfered block ends**, concentric grain rings in the middle (`#CB7A36` face, lit rim `#FCB35B`); arrow into the open end (§3.5) |
| Branch Stub | (200–330, 830–940) | a short thick planked stem with a **Y of two stubby prongs** with flat ends; the base cut for the socket |
| Moss / Foliage | (370–550, 870–990) | two leafy rosettes of **flat lobed leaves** (5–7 pointed lobes each) |
| Rock Module | (520–660, 1120–1210), (110–260, 1190–1320) | chunky faceted boulders, 10–16 broad facets, lavender grey, light tops |
| Foliage Clump | (400–520, 1200–1310) and others | upright tufts of **pointed lanceolate blades**, lime outside, deeper green inside |

### 1.5 How 055 differs from 026 Softwood Log and W05 `FallenHollowLog` (binding: the verifier checks these)

| | 026 Softwood Log (`FallenSoftwoodLog`) | W05 `FallenHollowLog` (old kit) | **055 Fallen Log** |
| --- | --- | --- | --- |
| Size | Ø 3.2 × 9.3, hip high | Ø 5.5 × 13.2 along X | **Ø 5.0 × 14.2 along Y, top 5.0, branch to 8.1** |
| Body | solid 11-sided log, bark plates with slits | a clean cylinder of staves | **a hollow barrel of 12 planked staves with V grooves and a step seam at 0.3 L** |
| Ends | a pale ringed cut face + a domed end | a **pale** heartwood rim, a flat cap | **open broken end: 12 staggered chamfered orange stave blocks round a black bore; closed end: a cut cap (disc + block ring, radial cracks)** |
| Cut-wood colour | pale cream | pale | **orange (`#E48C35`), never pale cream** |
| Branch | two stubs with pale broken tops | a Y limb | **one thick Y stub from the +X shoulder, flared collar, flat orange prong ends** |
| Green | four flat 6-leaf stars | lime moss mounds | **lobed-leaf rosettes matting the crest and draping down both flanks (G 25–29 %), spiky tufts** |
| Rocks | none | grey kit rock | **7 lavender-grey faceted rocks on both flanks** |

## 2. Layout (starting values; tune on the renders)

Studs, build frame (open end −Y, +X right, ground z 0, log axis x 0, z 2.45).

### 2.1 Stack (binding contact chain, bottom up; every seat gap 0.015)

| Piece | Sits on / in | Contact |
| --- | --- | --- |
| Log shell | ground | lowest stave facets sunk 0.05 below z 0 (the log rests on its bottom staves; no floating) |
| Cut-end cap | the shell's +Y end | disc plug 0.30 into the bore, 0.015 radial clearance; rim blocks 0.015 off the stave ends |
| Bore plug (decision §8.5) | inside the bore | its rim touches the bore wall (0.015) |
| Branch stub | the shell's +X shoulder | collar sunk 0.25 into the shell (a closed shell inside the shell's solid, but never through the bore wall: the wall is 0.8 thick, so cap the sink at 0.35) |
| Moss leaves | the shell (or a leaf below them) | each leaf's underside 0.00–0.03 off the bark, never more than 0.05 into it; drape leaves chain leaf to leaf up to the crest |
| Rocks, pebbles | ground (and may touch the log) | sunk 0.10 / 0.04; ≤ 0.05 into the log |
| Tufts | ground | hub sunk 0.03; every blade within 0.03 of its hub; ≥ 0.3 clear of rock and log surfaces |

### 2.2 Log shell

| Station Y | −7.1 … −6.6 (stave ends, staggered) | −6.6 | −2.9 (seam) | +1.0 | +4.5 | +6.65 (back end) |
| --- | --- | --- | --- | --- | --- | --- |
| Outer R (stave crests) | 2.50 | 2.50 | 2.48 / 2.54 (step) | 2.52 | 2.50 | 2.48 |
| Twist of the stave lines | 0° | 0° | 3° | 5° | 7° | 8° |

- **Section:** **12 staves**, each 2 facets wide (24 sides); the vertex between two staves pulled in 0.14–0.18 (a dark
  V groove), each stave's middle ridge proud 0.04–0.06; alternating staves ±0.04 thicker; a slight (≤ 8°) twist so the
  grooves run gently diagonal on the flank, as in the f34. No ring finer than these stations.
- **Step seam at Y −2.9** (0.3 L from the open end): the front section's staves end at a chamfered step, the body's
  staves start 0.06 proud and **offset by half a stave** (15°), so the grooves jog; a dark crease ring 0.08 deep. This
  is the exploded's white line and the f34's ring step.
- **Bore:** inner R 1.70 (Ø 3.4; wall 0.80 = one stave, close-up C), 12-sided, the inner facets planked (the inner
  vertices on the stave grooves, pulled out 0.04 so plank lines show inside, `z_f34end.png`).
- **Open (broken) end:** each of the 12 staves ends in its own **end block**: the annular end face (r 1.70–2.50) with a
  0.12 chamfer on both edges, the stave's Y end staggered: offsets (clockwise from the top, seen from the front) 0.0,
  −0.35, −0.15, −0.5, −0.2, 0.0, −0.3, −0.1, −0.45, −0.05, −0.25, −0.4 (so ends run −6.6 … −7.1); the blocks on the
  right (+X) side stick out most, as in the f34. 2–3 blocks carry a notch or a broken corner (a 0.2 chip).
- **Back end (+Y 6.65):** stave ends flat, hidden by the cap's rim blocks.
- **Plank splits:** 6–8 short dark splits (0.06 wide, 0.8–1.6 long) along stave crests on the visible flanks and top
  (the side cell's breaks in the plank lines), inset faces, no booleans.

### 2.3 Cut-end cap (+Y end)

- **Disc:** 12-sided, Ø 3.4 − 0.03, face at Y +6.95 (recessed 0.12 behind the rim faces), plug 0.30 deep into the bore;
  **9 radial cracks** (0.05 deep V grooves from r 0.25 to r 1.6) and a small centre pip (Ø 0.3, 0.04 proud), a faint
  grain ring at r 0.9 (an edge loop with a 0.02 step).
- **Rim:** **12 chamfered blocks** (r 1.72–2.62, 0.45 long in Y, 0.10 chamfers), each aligned to a stave, butting the
  stave ends at +6.65 (gap 0.015), faces at Y +7.07–7.12 (±0.03 per block). They stick out 0.1 past the staves, as the
  rear cell's blocky outline shows.

### 2.4 Branch stub

| Point | Option A (recommended, §3.3) | Option B | Ø |
| --- | --- | --- | --- |
| Collar base (on the shell, 43° round from the top toward +X) | (1.70, +1.4, 4.28) | same | collar 2.1 → stem 1.6 |
| Fork | (2.35, +2.55, 6.75) | (2.35, +0.25, 6.75) | 1.25 |
| Main prong tip (flat cut end) | (2.55, +3.30, 8.10) | (2.55, −0.50, 8.10) | 0.90 |
| Side prong tip (flat cut end) | (3.35, +3.00, 7.60) | (3.35, −1.55, 7.60) | 0.75 |

- **Shape:** a 7-sided planked prism (long facets running along it, two dark creases), **hard kink at the fork**, the
  prongs 6-sided, **flat cut ends** with a 0.06 chamfer, end faces `wood_cut`. The collar is a short wider ring (Ø 2.1,
  0.5 long) sunk 0.25 into the shell so the stub **flares into the bark** (close-up B), with two moss leaves at its
  foot (§2.5).
- Projected checks: front tips x +2.4 / +3.3, z 8.05 / 7.6; base x +1.7; side lean ≈ 46–52° above horizontal.

### 2.5 Moss (leaf rosettes)

Leaves: flat **lobed leaves**, 0.9–1.6 across, 5 pointed lobes (a 10-point star outline), a shallow raised centre
(0.06), a flat underside; laid on the bark following its curvature (each leaf turned to the local surface normal), the
next layer overlapping by 30–50 %. Drape leaves hang down the flank in a chain (each one seated on the one above and
the bark). Rosette tops lime, lower and under leaves the deeper MOSS green (§5).

| Clump | Where (Y range, side) | Reaches down to | Leaves |
| --- | --- | --- | --- |
| M1 big drape | Y −4.6 … −1.6, crest and +X flank | z 1.7 (f34; side z 2.4) | 12–14 |
| M2 crest band | Y −1.6 … +0.8 along the crest, to the branch foot (2 leaves on the collar) | crest only | 6–8 |
| M3 drape | Y +2.0 … +5.2, crest and +X flank | z 2.9 (side) | 8–10 |
| M4 upright clump | Y +4.4 … +6.2, top-back (−X shoulder near the crest) | crest; 2 leaves stand up 40–60° | 5–6 |
| M5 drape | Y −2.6 … +0.4, crest and −X flank (r34) | z 2.0 | 10–12 |
| M6 shoulder clump | Y +5.0 … +6.6, −X shoulder (r34 near the cap end) | z 3.2 | 5–6 |
| Front-end cap | 3 leaves on the top of the open end (front cell: moss over the ring's top and right) | the ring top | 3 |

Total ≈ 50 leaves. Keep the crest between M2 and M3 partly bare (the f34 shows bark round the branch).

### 2.6 Rocks and tufts

| Piece | Position (x, y) | Size W × D × H | Evidence |
| --- | --- | --- | --- |
| RK1 tall (+X, under the branch) | (3.6, +1.6) | 2.6 × 2.2 × 2.3 | f34 tall rock; side merged blob; front +X behind, top 3.0 |
| RK2 mid (+X) | (3.4, −1.0) | 2.6 × 2.2 × 1.7 | f34 mid rock; side merged blob |
| RK3 small (+X, near the open end) | (3.0, −4.4) | 1.8 × 1.6 × 1.3 | f34 small rock; front +X low |
| RK4 corner (+X, by the open end) | (2.4, −6.6) | 1.5 × 1.3 × 0.9 | side corner rock (Y −7.2 … −5.0) |
| RK5 big (−X, near the cap end) | (−3.4, +3.8) | 2.6 × 2.2 × 2.2 | r34 big rock; front −X taller (top 2.8) |
| RK6 mid (−X) | (−3.5, −0.4) | 2.2 × 1.9 × 1.6 | r34 mid rock |
| RK7 small (−X, near the open end) | (−3.3, −4.6) | 1.3 × 1.1 × 0.9 | r34 small rock; front −X low |
| Pebbles ×4 | (4.8, −0.1), (4.4, +5.4), (2.6, +6.9), (−3.0, −6.6) | 0.45–0.8 | small greys in every view |
| T1 (−X by the open end) | (−3.4, −6.0) | Ø 2.2, 1.8 tall, 7 blades | f34 far-left; front −X tuft |
| T2 (+X front) | (4.6, −4.8) | Ø 2.0, 2.0 tall, 7 blades | front +X |
| T3 (+X between RK3 and RK2, tallest) | (3.7, −2.6) | Ø 1.8, 2.4 tall, 7 blades | f34 tall tuft in front of the drape |
| T4 (+X far end group) | (3.9, +4.6) and (4.6, +6.2) | Ø 3.0 together, 2.2 tall, 13 blades | f34 right group; side tufts Y +3 … +7 |
| T5 sprigs (+X between RK2 and RK1) | (4.6, +0.4) | Ø 1.0, 0.8 tall, 5 blades | f34 low sprigs |
| T6 (−X cap-end corner) | (−3.9, +5.9) | Ø 2.4, 2.2 tall, 8 blades | r34 far left; rear −X tuft 2.4 |
| T7 (−X mid, between RK6 and RK5) | (−4.2, +1.7) | Ø 1.4, 1.2 tall, 6 blades | r34 |
| T8 (−X near the open end) | (−3.8, −2.5) | Ø 1.6, 2.0 tall, 6 blades | r34 tall middle tuft |

- **Blades:** pointed lanceolate, broad at the base (L : W ≈ 4), folded once along the midrib (closed, 6 tris), rising
  60–85° and arching out from a small hub; never needles, never edge-on to the f34 or front camera.
- **Rocks:** chunky angular boulders, flat base, 10–16 broad facets, a sloping faceted top; W : H 1.1 for RK1 and RK5,
  1.4–1.8 for the rest. Never eggs or `K.hull_rock` balls.
- **Keep clear:** nothing more than 0.05 inside the log or a rock (047 round-2 blocker); every tuft hub ≥ 0.3 outside
  rock and log surfaces; rocks may touch the log but cut ≤ 0.05.

### 2.7 Expected extents and screen checks

- **Extents:** X −5.2 … +6.3, Y −7.4 … +7.15, Z 0 … 8.1 (bbox ≈ 11.5 × 14.6 × 8.1).
- **Checks on the renders** (floor hidden, `measure_render.py` with this folder's `m.py`):
  - **f34_sheet (55, 18)** (probe az 40 … 70 × e 12 / 18 / 24, keep the best; §3.2): W : H 1.42–1.58 (sheet 1.503);
    shares T 56 ± 4, G 28 ± 3, R 12 ± 3; fill 0.61 ± 0.05; top profile ±0.08 at f .1–.9; the open end at left with a
    dark bore and staggered blocks.
  - **r34_sheet (−48, 18)** (probe −35 … −60): W : H 1.50–1.68; T 56 ± 5, G 29 ± 4.
  - **front_sheet (0, 3):** W : H 1.30–1.46 (sheet 1.385); **O (bore) 17 ± 4 %**; the bore a round dark disc (w : h
    0.9–1.1) in a ring of 12 blocks; the branch tips at x +2.4 / +3.3 ± 0.4, z 8.05 / 7.6 ± 0.3.
  - **side_sheet (90, 3):** W : H 1.66–1.86 (sheet 1.764); T 58 ± 4, G 25 ± 3; the open end at left.
  - **rear_sheet (180, 3):** W : H 1.18–1.36; the cap face (block ring + cracked disc), the branch on screen left.
  - **top (0, 89):** judged for content (§3.5): rocks along both long sides, 5–6 moss rosettes over the top, tufts
    between rocks; T 43 ± 8, G 35 ± 8.

## 3. View conflicts and resolutions

### 3.1 Sheet number

- **Evidence.** The header says "56/132" and "56 — FALLEN LOG"; INDEX row 55 lists `055.png` as "Fallen Log Model
  Study".
- **Resolution.** Our number is 055 (file name, keys `m055_*`). Note the header in the export notes only.

### 3.2 Which way the log lies, and where the 3/4 cameras stand

- **Evidence.** The front ortho shows the open end straight on, the rear ortho the cap, the side the log broadside: the
  log lies **front to back**. Both 3/4 views show the **open end** (f34 at left, bore w : h ≈ 0.55–0.6; the "rear" r34
  at right, bore w : h 0.69). So the f34 camera is front-right (az ≈ +50 … +60, seeing the +X flank, where the front
  and rear orthos put the bigger rocks and the branch shoulder) and the "rear 3/4" camera is **front-left** (az ≈ −46,
  seeing the −X flank).
- **Resolution (decision §8.2).** Log along Y, open end −Y. Cameras `f34_sheet (55, 18)` (probe 40 … 70, e 12–24) and
  `r34_sheet (−48, 18)` (probe −35 … −60). Record the chosen ones. The r34 is named "rear 3/4" on the sheet but is
  compared from the front-left.

### 3.3 Which way the branch leans

- **Evidence.** Both 3/4 views lean the branch **toward the cap end** (f34: up-right at ~51° on screen; r34: up-left at
  ~56°); with the cameras of §3.2 both need the branch to lean +Y. The **side ortho** leans it **toward the open end**
  (~46°), and the exploded draws the stub leaning toward the open end too. Front and rear agree with either (they show
  only the +X lean).
- **Resolution (decision §8.3).** **Option A: lean toward the cap end (+Y), ~50° above horizontal, +X 15°** (§2.4): the
  two hero views (the biggest drawings, and they agree) and the front and rear match; the side's lean comes out mirrored
  (judge the side for content: branch position, height, Y fork). Option B (lean −Y) matches the side and the exploded
  but makes both 3/4 views lean the wrong way.

### 3.4 One branch stub or two

- **Evidence.** The r34 shows a second, smaller Y stub (about 2.6 above the crest) near the open end. The f34, front,
  side, rear and top show one branch; the notes say "One branch stub (reusable)"; the exploded has one.
- **Resolution (decision §8.4).** **One stub.** If the main session wants the r34's second stub, reuse the branch part
  at 0.65 scale on the −X shoulder at Y −4.2 (about 110 tris).

### 3.5 The exploded cap, the top view and the bore

- **Cap.** The exploded's dashed arrow sends the cap into the **open** end; the rear ortho shows the cap on the
  **other** end and every assembled view shows the open end open. → **The cap closes the +Y end** (decision §8.6).
- **Top view.** It draws the log left-right (rotated 90° to the sheet convention), at about 0.9 of the side's length
  and a flatter width (63 px vs 87), with no branch visible. → **Judged for content only** (rocks along both sides,
  moss rosettes on top, tufts); the branch must show from above in ours.
- **Bore depth.** The open end shows black from about one diameter in; the rear shows a solid cap. → A bore of the
  full wall thickness from the open end to a **dark plug at 5.0 deep** (decision §8.5), or the full length to the cap.

### 3.6 Exploded positions vs the hero

- **Evidence.** The exploded puts the branch socket at about 0.26 of the length from the open end and the moss sockets
  at 0.45 / 0.68; the assembled views put the branch at 0.58–0.69 (side 0.58, f34 ~0.65, r34 0.64) and moss as §2.5.
- **Resolution.** **The hero governs positions**; the exploded gives shapes, counts and joints. Branch at Y +1.4 (0.60).

### 3.7 "WOOD A (DARK)" vs the no-facing rule

- **Evidence.** The WOOD A swatch `#AF6737` equals the body's rendered median (`#B96E34` f34, `#B26933` side); WOOD B
  `#E09952` equals the lit facets and cut ends (v > .7 `#DD8D46`–`#E3934B`; stave ends `#E48C35`).
- **Resolution.** `wood` is the body colour (WOOD A); `wood_cut` (WOOD B) goes on **cut faces only** (stave-end blocks,
  cap rim faces, prong ends), never on lit-facing facets. Shade comes from the light; `wood_deep` only in grooves, the
  bore, the seam and under the collar.

### 3.8 Ground and cast shadow

- No soil patch in any cell: rocks, tufts and the log sit on the paper. No patch. The lavender shadow is excluded by the
  X mask; render every `*_sheet` view with the floor hidden.

## 4. Construction plan (stages 1–3)

### 4.1 Parts first, each from its own function, checked against its exploded cell

1. `stave_shell()` → the log shell (§2.2) as **one closed ring-stack shell**: outer 24-sided rings at the stations,
   the seam step as two close rings (a chamfered step, not a boolean), the open end's 12 staggered end blocks built as
   part of the same ring stack (each stave's outer and inner facet pair runs to its own end Y, closed by its chamfered
   end face; the side faces between neighbouring staves are the step faces), the bore's 12-sided inner ring stack from
   the open end to the plug, closed by the plug disc (decision §8.5). Groove vertices pulled in, plank splits as inset
   faces. **No booleans.** If the staggered ends are too fiddly as one shell, build each end block as its own closed
   shell seated 0.015 off a flat shell end (and say so in the stage record).
2. `cut_end_cap()` → disc + 12 rim blocks (§2.3): the disc one closed shell (cracks as V edge loops), each rim block a
   closed chamfered box, all seated by contact.
3. `branch_stub(lean)` → collar + stem + fork + two prongs (§2.4) as one ring-stack shell (mitred rings at the fork;
   the side prong a closed prism buried ≥ 0.15 in the stem, as 053's tines) with flat chamfered ends.
4. `moss_leaf(size)` / `moss_clump(spec)` → lobed leaves (§2.5), placed on the shell by ray-cast to the surface, each
   turned to the surface normal and lifted 0.01–0.02; drapes chain leaf to leaf.
5. `rock(spec)` ×7 (explicit ring stacks: base ring, widest ring at 0.3 h, shoulder ring at 0.7 h, a sloping faceted
   top), `pebble()` ×4.
6. `tuft(spec)` ×8 groups (§2.6) with the placement guard (§6).
7. **Hero `MossyHollowLog`** = shell + cap + branch + moss + rocks + tufts, joined into one object of closed shells.
8. **Parts shot** (55, 22) laid out like the exploded: the shell in the middle, the cap off its +Y end, the branch
   above, two moss clumps above the top, a rock module and a foliage clump in front; gaps 1.5–2.

### 4.2 Stage 1 acceptance

1. **Overall read:** a hollow staved log with a round black bore in a ring of staggered orange blocks, a cut cap on the
   far end, one Y branch, leafy lime moss over the top and down both flanks, lavender rocks and lime tufts along both
   sides.
2. **f34_sheet**, **front**, **side**, **rear**, **r34**, **top** per §2.7.
3. **Close-up renders:** `bore_cu (20, 8)` on the open end against close-up A (12 chamfered blocks, planked inner wall,
   black depth); `branch_cu (55, 25)` cropped on the collar against close-up B (flare into the bark, no ring, moss at
   the foot); `section_cu` — a part render of one shell end-on, against close-up C (one stave thick, the same all
   round); `cap_cu (180, 5)` against the rear cap.
4. **Contact counts** (§6): floating shells 0; buried dressing 0.
5. **Size** per §1.1; a **scale shot** with a 5.5-stud marker beside the log at Y −1 (the log top at 0.91 of its height)
   and one on the crest at Y −4 (standing on the log).

### 4.3 Budget

| Piece | Count | Tris each | Total |
| --- | --- | --- | --- |
| Shell outer (24 sides × 5 bands + seam step) | 1 | 290–330 | 290–330 |
| Open-end blocks (stagger, chamfers) | 12 | 14–20 | 170–240 |
| Bore (12 sides × 2 bands) + plug | 1 | 60–70 | 60–70 |
| Plank splits | 6–8 | 8 | 50–65 |
| **Log shell part** | | | **570–700** |
| Cap disc (12 sides, 9 cracks, pip) + 12 rim blocks (12 each) | | | 230–270 |
| Branch stub (collar, stem 7-sided, fork, prongs 6-sided) | 1 | 140–180 | 140–180 |
| Moss leaves (20 tris each) | 48–52 | 20 | 960–1040 |
| Rocks (32–44) + pebbles (8–10) | 7 + 4 | | 270–340 |
| Tuft blades (6 tris) + hubs (8) | ~57 + 9 | | 410–420 |
| **Hero** | | | **about 2600–2950** (limit 4000; ceiling 3600) |
| Parts: LogShell / CutEndCap / BranchStub / MossClump (M1) / RockModule (RK1) / FoliageClump (T3) | | | 570–700 / 230–270 / 140–180 / 260–300 / 40 / 50 (limit 1000) |

- **Spend headroom on the read:** first a 3rd facet per stave on the visible flanks or more stagger detail on the open
  end; then more leaves on the drapes. Never subdivide.
- If the hero passes 3600, drop to 16-tri leaves (8-point stars) before cutting leaves.

### 4.4 What to do better than W05 and 026

| Earlier | This one |
| --- | --- |
| W05: "clean cylinder, flat cap" | 12 staves, V grooves, a step seam, plank splits; a cap with a block rim and cracks |
| W05: pale heartwood rim; the bore read as a slot from the front (VR4) | orange stave-end blocks; the bore a round black disc straight on in the front cell |
| W05: "flat moss"; "stub a block" | lobed-leaf rosettes that drape; a planked Y stub with a flared collar |
| 026: hovering ground clumps (0.2 above the floor) | every tuft hub sunk 0.03; contact counted |

### 4.5 Stages 2 and 3

- **Stage 2:** every shell closed and manifold; 0 bowties (stagger steps, the seam step, leaf tips and tuft hubs are the
  likely spots: `M.fix_bowties`); **0 winding errors per shell** (STAGES "Consistent winding": the bore's inner faces
  must face into the bore, i.e. away from the wall's solid, and the step faces flip easily); no zero-area faces; n-gons
  only on flat caps (triangulate the 12-sided disc as a fan round the pip); corners ≥ 3°. Origin bottom centre,
  transforms applied.
- **Stage 3:** Smart UV (margin ≥ 0.008), no overlaps, even texel density; the exporter writes palette UVs.

## 5. Colour plan (stage 4)

### 5.1 Swatches (flat; medians of the inner box, sd ≤ 1.3)

| Swatch | Box | Hex | HSV | Use |
| --- | --- | --- | --- | --- |
| WOOD A (DARK) | (643,84,688,129) | `#AF6737` | 24°, 0.69, 0.69 | start for `wood` |
| WOOD B (LIGHT) | (705,84,750,129) | `#E09952` | 30°, 0.63, 0.88 | start for `wood_cut` |
| MOSS | (767,84,812,129) | `#6CA433` | 90°, 0.69, 0.64 | start for `leaf_green` |
| FOLIAGE | (829,84,874,129) | `#C5CF17` | 63°, 0.89, 0.81 | start for `leaf_lime` |
| ROCK A (LIGHT) | (890,84,935,129) | `#A8A4AE` | 264°, 0.06, 0.68 | start for `rock` |
| ROCK B (DARK) | (952,84,997,129) | `#868586` | ~0°, 0.01, 0.53 | start for `rock_dark` |

### 5.2 Rendered regions (`samp.py`, `samp2.py`; median / v > .7 / lit quartile / shade quartile)

| Region | Median | v > .7 | Lit Q | Shade Q |
| --- | --- | --- | --- | --- |
| Wood f34 / side / r34 | `#B96E34` (26°, .72, .73) / `#B26933` / `#A56232` | `#DD8D46` / `#E2914A` / `#E79548` | `#F2A45A` | `#4D2A11`–`#5E3316` |
| Log body f34 (x > 200) / side (y 640–720) / exploded body | `#BE7236` / `#B06732` / `#BC7236` | `#E19350` / `#E3934B` / `#DD8F4C` | `#F1A45C` | `#623918` / `#5B3215` |
| Open-end stave blocks (front) | `#E48C35` (30°, .77, .89) | `#E9923C` | `#F19F47` | `#45230C` (groove gaps) |
| Cap disc face (rear) / exploded cap | `#CA702E` (25°, .77, .79) / `#CB7A36` | `#D0762F` | `#FBAE4C` (rim blocks) | `#AF6127` |
| Branch f34 / side / exploded | `#BE6F38` / `#CE7E3E` / `#A66036` | `#D87F3F` / `#E18C48` | `#EDA055` | `#683A1F` |
| Bore inner wall (f34, v .2–.5) / close-up C inside | `#502A11` (24°, .79, .31) / `#7D4824` | | `#733C18` | `#3B1F0E` |
| Bore depth (front / f34 / close-up A) | `#070602` / `#150B04` / `#0C0702` | | | |
| Moss on the log (f34 / side / exploded) | `#CEDB09` (64°, .96, .86) / `#BFD005` / `#CAD709` | `#D6E109` | `#DDE80B` | `#52800A` (83°) / `#4F7407` / `#5D8E0A` |
| Tufts (f34 / side / exploded) | `#8CA904` (71°, .98, .66) / `#A3B803` / `#88A904` | `#CED702` / `#C7D202` | `#D7DE03` | `#416806` (84°) |
| Rock f34 / r34 / front / side / rear / top | `#AFA0A0` / `#A2959A` / `#988F93` / `#B1A1A0` / `#A79D9A` / `#9D9496` | `#D3C2BE` / `#D4C7C5` / `#D1CABE` / `#CFC2BA` / `#CCC5BB` / `#D0C5C0` | `#E4D7D1` … `#D6CFC7` | `#696269` / `#6B666E` / `#5F6262` / `#6F6B72` (cool lavender) |

### 5.3 How the colour works

- **Wood:** one warm orange-brown (`wood`, 24–27°, sat 0.68–0.73, R > G > B) on the staves and the branch; **deeper**
  (`wood_deep`) in the stave grooves (faces touching a pulled-in groove vertex: position), the seam crease, the plank
  splits' insides, the lowest 0.4 of the shell (ground contact) and a ring under the branch collar; **cut orange**
  (`wood_cut`) on the open-end block end faces, the cap rim block faces and the prong ends; **end grain**
  (`wood_end`) on the cap disc; the **bore** `wood_deep` at its mouth blending to `hollow` by depth (position along −Y,
  never by facing) over the first 2.5 studs; the plug `hollow`.
- **Moss:** rosette top leaves `leaf_lime`; lower leaves, under-layer leaves and the bottom leaves of every drape
  `leaf_green` (the MOSS swatch), blended by layer and by height down the drape (by role and position). The sheet's moss
  is mostly lime with green under it.
- **Tufts:** outer and taller blades `leaf_lime`, inner and lower blades `leaf_green`, by role.
- **Rocks:** a neutral lavender grey (`rock`), upper 35 % of each rock a step lighter (`rock_light`), the lowest 25 %
  `rock_dark`, by height within the rock. The sheet's lit rock faces read warm (19–40°) and the shade faces cool
  lavender (240–300°): that is the light, not the material.
- **Hues stay apart:** wood 24–27°, cut wood 29–32°, leaf_lime 62–66°, leaf_green 80–90°, rock neutral (sat ≤ 0.07).

### 5.4 Keys (start from these; `K.calibrate`; write the calibrated hexes into `palette()`)

Calibration targets are rendered-region medians, not swatches. `K.sample` kinds: `"brown"` for wood, `"stone"` for
rock, `"vivid"` for the greens.

| Key | Calibration target | Hue / sat / order | Where | Finish |
| --- | --- | --- | --- | --- |
| `m055_wood` | log body median `#B86C34` ± 15 (f34 `#BE7236`, side `#B06732`); v > .7 `#E0914A` ± 12 (start `#AF6737`) | 24–27°, 0.68–0.73, **R > G > B** | staves, branch | rough 0.9 |
| `m055_wood_deep` | bore wall `#502A11` ± 12 | 22–26°, 0.75–0.82, v 0.25–0.35 | grooves 45 %, seam, splits, shell bottom 25 %, collar ring 30 %, bore mouth | rough 0.95 |
| `m055_wood_cut` | open-end blocks `#E48C35` ± 12 (start `#E09952`) | 29–32°, 0.65–0.78 | block end faces, cap rim faces, prong ends (hard: cut faces) | rough 0.85 |
| `m055_wood_end` | cap disc `#CA702E` ± 12 | 24–27°, 0.74–0.80 | cap disc face (hard against the rim) | rough 0.9 |
| `m055_hollow` | bore depth `#140B04` ± 8 | 24–30°, v ≤ 0.10 | bore beyond 2.5 deep, the plug, crack bottoms | rough 1.0 |
| `m055_leaf_lime` | moss on log `#CEDB09` ± 12; tuft v > .7 `#CED702` (start `#C5CF17`) | **62–66°**, ≥ 0.85 | rosette tops, outer blades | rough 0.85, low spec |
| `m055_leaf_green` | the MOSS swatch `#6CA433` rendered lit ± 12; shade band `#52800A` | 82–90°, 0.70–0.92 | under / lower leaves, drape bottoms, inner blades, hubs | rough 0.85, low spec |
| `m055_rock` | rock v > .7 `#D0C5BF` ± 10 (start `#A8A4AE`) | neutral, sat ≤ 0.07, \|R−B\| ≤ 8 | rocks, pebbles | rough 0.85, metal 0 |
| `m055_rock_light` | lit quartile `#DCD3CC` ± 10 | neutral, sat ≤ 0.07 | top 35 % of each rock at 40 % | rough 0.85 |
| `m055_rock_dark` | the ROCK B swatch `#868586` ± 10 | neutral, sat ≤ 0.04 | lowest 25 % at 30 % | rough 0.9 |

**Calibration warnings:**
- **The kit studio lights both halves** (042, 047): calibrate `wood` to the body median and the v > .7 median together,
  not the lit half, or the log goes flat orange (W05 V8 / V16). Our whole median may read up to 20 levels lighter than
  the sheet's: record it.
- **Cut wood stays orange, never cream** (§1.5): `wood_cut` ≥ 30 levels lighter (V) than `wood` and 3–6° yellower, sat
  ≥ 0.65.
- **Rock must not go pink or mauve** (M034, M037): the sheet's rock median hue (0°, s 0.09 in the f34) is wood bounce;
  keep R, G, B within 8 of each other on every median.
- **Green must not go yellow** (047's "plants leaning yellow"): the lime ≥ 62°, the all-green median of the f34 66–71°
  (sheet `#B7CC06` 66°, tufts `#8CA904` 71°); `leaf_green` ≥ 15° greener than `leaf_lime` after calibration.

### 5.5 Blending (`K.blend(mode="blend", steps=3)` over explicit face lists; fields are positions and roles)

- **Shell:** `wood` base; `wood_deep` 45 % in the groove columns (one facet out, steps 3) so each stave reads rounded;
  25 % on the lowest 0.4; the seam crease ring 40 %; hard `wood_cut` on the end-block faces; the bore `wood_deep` →
  `hollow` over Y −7.0 … −4.5 by depth. Per-stave Tint ±0.04 held along each stave, plus broad noise 0.03 at scale 0.35.
- **Branch:** `wood` base, a `wood_deep` ring under the collar and at the fork crotch (30 %), hard `wood_cut` ends.
- **Cap:** `wood_end` disc, crack bottoms `hollow`, rim faces hard `wood_cut`, rim sides `wood`.
- **Moss / tufts:** by layer and role; drapes blend `leaf_lime` → `leaf_green` downward (steps 3).
- **Rocks:** height bands within each rock.
- **Hard edges only** where materials meet: cut face | bark, bore | wall, wood | moss leaf, rock | ground.

### 5.6 Texture (Tint) and finish

- **Tint:** wood 0.04 per stave column plus 0.03 broad; rock 0.04 per facet; leaves 0.04 per leaf; blades 0.04 per
  blade. Never per-triangle confetti.
- **Finish:** wood 0.9, cut and end wood 0.85–0.9, hollow 1.0; rock 0.85; greens low spec. No emission.

### 5.7 Re-measure (final renders against the sheet, same masks)

- **Wood:** f34 body median within 20 of `#BE7236`; v > .7 within 12 of `#E19350`; R > G > B; hue 24–27°.
- **Cut wood:** the front cell's block faces within 15 of `#E48C35`.
- **Bore:** the front cell's bore core v ≤ 0.10 over ≥ 60 % of its disc.
- **Rock:** v > .7 within 10 of `#D0C5BF`, neutral.
- **Green:** f34 moss within 12 of `#CEDB09`; tufts median within 15 of `#8CA904`; shade quartile 80–86°.
- **Shares** per §2.7.

## 6. Joins and contact (no floating dressing, no buried dressing)

- **Shells:** the log shell one closed shell (or the shell plus 12 seated end blocks, §4.1); the cap disc and each rim
  block; the branch stem (one ring-stack shell) and its side prong; each leaf, rock, pebble, blade and hub its own closed
  shell. All in one hero object.
- **Seats:** cap disc 0.30 into the bore with 0.015 clearance, rim blocks 0.015 off the stave ends; branch collar 0.25
  into the shell, **no collar vertex through the bore wall** (ray parity against the bore: 0 inside); leaves 0–0.03 off
  the bark or the leaf below; tuft hubs 0.03 into z 0.
- **Count floating shells before reporting** (STAGES; 035 / 036 round 1): **0**. A shell floats if its nearest distance
  to every other shell and the ground is > 0.03 or it doesn't chain to the ground: leaf → leaf / shell → ground; prong →
  stem → collar → shell → ground; rim block → shell; blade → hub → ground; rock → ground.
- **Count buried shells** (STAGES; 047 round 2 blocker): **0 dressing shells more than 0.05 inside the log or a rock**,
  by ray parity against the full hero after the final placement step. Use 047's guard from the start (`_Solids`: the
  shell + every rock as built; three skewed rays, two of three agree; placement accepts ≤ 0.03; a blade or leaf that
  still cuts after its retries is **dropped**, never kept). Drape leaves on the flank are the likely offenders (the
  surface curves away under them): ray-cast each leaf's 5 lobe tips to the bark.
- **Bowties:** `M.fix_bowties` on every object; `nonmanifold_verts` 0.

## 7. Lighting and VFX plan (stages 5 and 6)

**What the sheet shows:** nothing glowing, no light, no particles, no falling leaves, no dust, no insects. The bore's
darkness is geometry and colour.

- **Stage 5 (lighting): skip, and record why.** No emission, no lights. Studio notes (Requires Manual Validation): the
  bore stays black under the game sun (a `hollow` plug, not open sky behind); the wood stays orange-brown, not red; the
  cut ends read lighter orange; the rocks stay neutral grey; the moss lime with green under it.
- **Stage 6 (VFX): skip, and record "the sheet shows no effect".** Not recommended: fireflies or spores from the bore
  (not on the sheet).
- **Collision:** hero `precise` (players jump on, walk the crest and step round the branch; a hull would fill the bore
  and wrap the branch); log shell part `precise`; cap, branch and rock modules `hull`. Moss leaves and tufts
  walk-through (`kit_nocollide = 1`) only if the exporter already supports it for this kit (decision §8.11).

## 8. Naming and decisions for the main session

**Names owned elsewhere.** Searched `art/blender/kit/mcp/*.py`, every `art/roblox/kit/*/manifest.json` and the repo
text (`git grep`) for Log, Fallen, Trunk, Stump, Timber, Hollow, Mossy, Deadfall:
- **W05:** `FallenHollowLog` (script hero), `LogAndStump`, `LogAndStumpHollowLog`, `…LogShell`, `…BranchStub`,
  `…CutEndCap`, `…MossFoliage`, `…BrokenLog`, `…LowStump`; also `HardwoodStump*`, `ResinheartStump*`,
  `AncientTreeHollowTrunk`, `GoldencrownHollowGiant`, `ResinheartHarvestedHollow`.
- **Numbered models:** `FallenSoftwoodLog*` (026: `…Trunk`, `…CutEnd`, `…BranchStubLarge/Small`, `…LeafClump`),
  `ChoppedHardwoodStump*` (020), `MossyBoulder*` (035), `MossAndIvy*` (056 sheet's old-kit names), `Timber*`
  (048–052), `TwistedSnag*` (053), `GnarledPine*` (047).
- **Other:** `SoftwoodLog*` (R06), `PalisadeWallLog`, `BarricadeRailLog`, `ColumnFallen`, `DailyItemsLogRack`.
- **`MossyHollowLog`, `Deadfall*` and `m055` occur nowhere.** `MossyHollowLog*` contains no owned name as a substring
  (`LogAndStumpHollowLog` and `MossyBoulder` are not substrings of it).

| Object | Part | Why |
| --- | --- | --- |
| `MossyHollowLog` | hero: shell, cap, branch, moss, rocks, tufts | W05 owns `FallenHollowLog` and 026 `FallenSoftwoodLog`; "mossy hollow log" names what it is |
| `MossyHollowLogShell` | "single hollow log shell" with the broken open end and the bore | the notes' term |
| `MossyHollowLogCutEndCap` | "CUT END (CAP)" | the label |
| `MossyHollowLogBranchStub` | "BRANCH STUB" | the label |
| `MossyHollowLogMossClump` | "MOSS / FOLIAGE": one rosette (M1) | the label |
| `MossyHollowLogRock` | "ROCK MODULE": RK1 | the label |
| `MossyHollowLogFoliageClump` | "FOLIAGE CLUMP": T3 | the label |

- Palette keys `m055_*` (§5.4). Collection `Kit/M055 Fallen Log`. No VFX sockets.

**Decisions needed (a recommendation each):**
1. **Size (§1.1):** **log Ø 5.0 × 14.2, top 5.0, branch tip 8.1; overall ≈ 11.5 × 14.6 × 8.1** (recommended: a fallen
   053/054 trunk; players jump onto it or climb by the rocks and walk the crest; bore Ø 3.4 is decoration), or Ø 3.6 ×
   10 (a hurdle a player can jump over, top 3.6), or Ø 9 × 25 (a walk-through tunnel, bore 6.2; dwarfs the trees).
2. **Frame (§3.2):** **log along Y, open end −Y facing the front; f34 at az ≈ +55, the sheet's "rear 3/4" compared
   from the front-left at az ≈ −48** (recommended), or lay it along X (W05's way), which breaks every ortho.
3. **Branch lean (§3.3):** **Option A, toward the cap end (+Y), ~50° up and 15° to +X** (recommended: the f34 and r34
   both, plus front and rear), or Option B, toward the open end (the side and exploded).
4. **Branch count (§3.4):** **one stub** (recommended: notes, exploded and four views), or add the r34's small second
   stub at 0.65 scale on the −X shoulder at Y −4.2 (~110 tris).
5. **Bore (§3.5):** **12-sided bore from the open end to a `hollow` plug at 5.0 deep** (recommended: black from one
   diameter in, as drawn; ~70 tris), or the full length to the cap (~140 tris, no visible gain).
6. **Cap (§3.5):** **on the +Y end** (recommended: rear ortho and every assembled view), ignoring the exploded's arrow.
7. **Broken end and seam (§2.2):** **12 staggered chamfered end blocks (0–0.5) and the half-stave step seam at Y
   −2.9** (recommended), or a flush end with no seam (simpler; loses the "broken end").
8. **Moss form (§2.5):** **≈ 50 flat lobed leaves in rosettes and chained drapes** (recommended: the sheet's leafy moss),
   or lumpy mounds (W05's "flat moss" failure).
9. **Side and top cells (§3.3, §3.5):** **judged for content** (recommended).
10. **Comparison cameras (§3.2):** **`f34_sheet (55, 18)` governing with `front_sheet (0, 3)`** (probe az 40 … 70, e
    12–24); `r34_sheet (−48, 18)` (probe −35 … −60); `side_sheet (90, 3)`, `rear_sheet (180, 3)`; kit `top`; extras:
    parts shot (55, 22), `bore_cu (20, 8)`, `branch_cu (55, 25)`, `section_cu`, `cap_cu (180, 5)`, scale shot. Floor
    hidden in every `*_sheet` render.
11. **Collision (§7):** **hero and shell `precise`; cap, branch and rock `hull`** (recommended); moss and tufts
    walk-through only if the exporter already supports `kit_nocollide`.
12. **Exported parts:** **the hero plus the six labelled parts** (recommended).
13. **Colour (§5):** **`wood` `#B86C34` / v > .7 `#E0914A`; `wood_cut` `#E48C35` (orange, not cream); `wood_end`
    `#CA702E`; `wood_deep` `#502A11`; `hollow` `#140B04`; `leaf_lime` `#CEDB09`; `leaf_green` from MOSS `#6CA433`; rock
    neutral lavender `#D0C5BF` lit / `#868586` dark** (recommended).
14. **Stages 5 and 6:** **skip both, recorded** (recommended).
15. **Budget (§4.3):** **4000 limit, about 2600–2950 planned, ceiling 3600; parts under 1000** (recommended).

## 9. Pitfalls to avoid (recent verifier failures written as targets)

1. **A smooth cylinder or a stack of boards (W05 "clean cylinder"; R06 "boxy segmented tube").** 12 staves with V
   grooves 0.14–0.18 deep, a slight twist, a step seam at Y −2.9 and plank splits; the side cell shows 4–5 staves
   across the flank, each rounded by groove shading.
2. **A bore that reads as a slot (W05 VR4; 047's "knot read as a slot").** From the front camera the bore is a round
   black disc (w : h 0.9–1.1), Ø 3.4 in a ring of 12 chunky blocks; front O share 17 ± 4 %. In the f34 the bore is an
   oval opening with the planked inner wall visible, never a dark sliver.
3. **A straight, bare column / stub branch (047 round 1 "stub limbs").** The branch reaches z 8.1 with a real Y fork
   and flat lit prong ends, Ø 1.6 at the collar; it flares into the bark with no pale ring and no gap.
4. **Buried plants (047 round 2 blocker).** 0 leaves, blades or hubs more than 0.05 inside the log or a rock, by ray
   parity after the final placement; drape leaves checked at every lobe tip; hubs ≥ 0.3 clear of rock and log.
5. **Floating dressing (STAGES; 035 / 036; 026's hovering ground clumps).** 0 floating shells; tuft hubs sunk 0.03,
   leaves 0–0.03 off the bark, chained to the ground.
6. **Plants leaning yellow (047 note 3).** Lime ≥ 62°, the f34 all-green median 66–71°, a real `leaf_green` under-layer
   (80–90°) on every rosette and drape bottom and inside every tuft.
7. **Pale cream cut ends (W05's heartwood rim, 026's cut face).** The sheet's cut faces are orange `#E48C35`; the cap
   disc `#CA702E`.
8. **Colour by facing (042 ruling).** `wood_deep` only in grooves, seam, splits, the bore, the bottom and the collar ring,
   by position; `wood_cut` only on cut faces; `K.check` facing correlation < 0.5 per material.
9. **Flat saturated orange or red wood (W05 V8 / V16).** Body median within 20 of `#BE7236`, hue 24–27°, R > G > B.
10. **Egg, pink or blue rocks (M034, M037).** Angular boulders, 10–16 broad facets, flat bases, neutral grey (R, G, B
    within 8).
11. **Edge-on or needle grass (039).** Folded lanceolate blades L : W ≈ 4, facing the f34 and front cameras.
12. **Winding (044) and bowties.** 0 faces wound against their neighbours per shell; the bore's inner faces point into
    the bore; stagger and seam steps checked; `M.fix_bowties`; corners ≥ 3°.
13. **Booleans.** None planned (ring stacks and seated shells). If one is truly needed, run it at the origin on clean
    manifold inputs and save first (STAGES "Booleans").
14. **Names and scope.** No `FallenHollowLog` / `LogAndStump*` (W05), no `FallenSoftwoodLog*` (026), no `MossyBoulder*`
    (035); one agent per Blender session; no commits, pushes or exports in stage agents; don't edit the frozen shared
    helpers or `lib/vfx.py`; don't touch other models' collections.

## Decisions (main session, 2026-10-30)
All 15 recommendations are accepted.
1. **Size.** Ø 5.0 × 14.2, top at z 5.0, branch tip at z 8.1. Players jump onto it or climb it via the +X rocks and walk along the top. The bore is decoration.
2. **Orientation.** Front to back, open end at −Y. The f34 camera sits at about az +55. The "rear 3/4" cell is compared from az −48.
3. **Branch.** It leans toward the cap end (+Y), about 50° up and 15° toward +X. The side and exploded views are judged on content only.
4. **Branch count.** One stub.
5. **Bore.** A 12-sided bore with a dark plug 5.0 deep. **It must read as a round dark disc, not a slot.**
6. **Cap.** On the +Y end.
7. **Broken end.** Staggered stave ends, plus a half-stave step seam at Y −2.9.
8. **Moss.** About 50 flat lobed leaves in rosettes and hanging chains, not lumpy mounds. Lime ≥ 62° over a green under-layer, never yellow.
9. **Side and top views.** Judged on content only.
10. **Cameras.** `f34_sheet (55, 18)` and `front_sheet (0, 3)` govern, with `r34_sheet (−48, 18)` alongside.
11. **Collision.** Hero and shell precise; cap, branch and rock hull.
12. **Exports.** The hero plus the six parts (`MossyHollowLog*`, keys `m055_*`).
13. **Colour.**

    | Part | Colour |
    | --- | --- |
    | Body wood | `#B86C34` |
    | Cut faces | `#E48C35` |
    | Cap disc | `#CA702E` |
    | Deep wood | `#502A11` |
    | Bore | `#140B04` |
    | Lime leaves | `#CEDB09` |
    | Green under-layer | `#6CA433` |

    - **Rocks are neutral grey,** as the sheet draws them: R, G and B within 8, lit target `#D0C5BF`, and B never more than G + 4, so they never read mauve or pink. They are faceted, never egg-shaped.
    - Blend by position and role, **never by facing.**
14. **Stages 5 and 6.** Both skipped and recorded.
15. **Budget.** Limit 4000, ceiling 3600.

**Shell and dressing.** The log reads as a staved barrel, not a smooth cylinder. 0 winding errors. **No floating dressing, and nothing buried**: ray-check every moss lobe tip.
