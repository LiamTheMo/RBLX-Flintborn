# W01 Row 1: Boulder — spec and goals

Reference: `art/reference/kit/W01_boulders_rocks_scatter.png`, row 1 (hero, front, side/rear, top, parts, 3 variations).
Builder: `art/blender/kit/mcp/w01.py` → `boulder_row()`.

## Study of the reference

- **Silhouette:** squat barrel dome, near-vertical lower sides, broad shoulder, gently domed top. Front view width:height about 1.45:1 including the moss. Big flat triangular facets (geodesic look), one soft crease down the front-left.
- **Parts:** Main Rock (mesh) + separate Moss Cap. Dressing round the foot: round-leaf herb clumps (some with small white five-petal flowers, yellow centre) and 3–5 pebbles.
- **Moss cap:** 3–4 overlapping flat lobed mounds with an oak-leaf outline, lime with sun-yellow crowns and a deeper green rim; sits on the crown, slightly back, spanning about half the rock's width. Exploded: a thick lobed lime slab floating above the rock.
- **Colours (sampled with `kit_mcp.sample`, sRGB):** rock median (216,205,199), lit (233,218,209), shade (183,178,178), cool lavender-grey patches; moss median (193,208,46), dark (155,178,28), sun-yellow (233,230,97); herbs median (141,173,42), lime (186,210,42); pebbles (185,181,185).
- **Surface:** matte stone, faint damp moss stain low on the front-left face (exploded main rock).
- **Effects:** none shown (no glow, particles or water). VFX and lighting stages skipped for this model.
- **Variations:** Flat Boulder (wider, lower, moss on crown); Upright Boulder (tall cone, moss tuft on top, streak down one face, small rock at its foot); Split Boulder (tall + squat piece side by side with a crack, moss on both).

## Scale

Character = 5.5 studs. Main rock 11.6 × 10.7 × 6.4 studs (≈1.2 character heights tall); with dressing 14.3 × 13.1 × 7.5. Upright variant 13.9 tall; Flat 5.0; Split 10.1.

## Result

- Verifier rounds: 1 FAIL 6.5 (flat moss decal, melted rock, big upright side rock, studio band) · 2 FAIL 6 (herb blades, small cap) · 3 FAIL 6 (herb language, soft facets, split shape) · 4 FAIL 6.5 (open crown, cap shape) · **5 PASS 8/10**.
- Tris: hero 3812, MainRock 208, MossCap 288, Flat 3477, Upright 3319, Split 3232 (budget 5000 dressed / 1500 part). 0 check problems.
- Colours (hero cell median): rock (214,204,197) vs master (216,205,199); moss (193,210,52) vs (193,208,46).
- Bug found and fixed on the way: `kit_mcp.hull_rock` deleted a flat crown as if it were the base (open top on every rock with a flat top ring).
- Open minors from the passing verifier (for review): herb clumps a little blocky/dark at close range; Upright slimmer than the master; moss small/hidden in the front view.

## Goals (all MET at the passing build)

1. Squat faceted drum, H/W 0.55 · 2. big flat facets, crisp tone steps · 3. moss cap of 5 broad lobed mounds on the crown, ≈42% of the rock width · 4. moss lime with sun-yellow crowns · 5. rock colour within 3 of the master · 6. chunky lobed clover clumps round the foot with white five-petal flowers · 7. 4–6 pebbles, some darker · 8. faint damp stain low on the front-left · 9. exploded: cap floating above the main rock · 10. Flat variant wider and lower · 11. Upright tall tapering rock with moss crown · 12. Split: tall tapering piece + squat angular piece, moss on each · 13. budgets · 14. origin, names, 0 problems · 15. no VFX (none in the master).
