# W01 Row 2: Rock Spire — spec and goals

Reference: `art/reference/kit/W01_boulders_rocks_scatter.png`, row 2. Builder: `art/blender/kit/mcp/w01.py` → `spire_row()`.

## Study of the reference

- **Silhouette:** a tall faceted obelisk (base ≈ 0.55–0.6 of its height) tapering to an angled peak, in a broad heaped foot; the whole mass is about as wide as it is tall.
- **Parts:** Rock Spire (main mesh) + Foot Collar (separate): a low jagged rim of big flat-topped angular blocks, taller at the back, round the spire's footprint.
- **Composition:** an angular slab at ~50% of the spire's height on the left, stepped slabs on the right and behind, one big boulder front-right, a smaller one front-left, low rocks stepping outward, pebbles.
- **Colours (sampled):** rock ≈ (216,205,199) with lilac-grey shadow facets; greens in this row (171,195,33): lime clover clumps on ledges and round the foot, lime moss patches on ledges and on the spire's right flank.
- **Effects:** none (no VFX/lighting stage).
- **Variations:** Short (stubby spire, low foot), Tall (high spire, stepped slabs both sides), Leaning (spire tilted, rocks at its foot).

## Scale

Character 5.5 studs. Spire 12.4 tall (≈ 2.3 characters); hero 15.7 × 12.8 × 12.5 with dressing; Tall 16.0; Short 7.6; Leaning 11.6.

## Result

- Verifier rounds: 1 FAIL 6.5 (greens too dark) · 2 FAIL 6 (shoulders as round boulders, slim spire, collar not a ring) · 3 FAIL 7 (collar scattered) · 4 FAIL 7 (collar loose pebbles) · **5 PASS 7.5/10**.
- Tris: hero 5633 (budget 6000, landmark), Main 180, FootCollar 588, Short 2945, Tall 3546, Leaning 3226. 0 check problems.
- Colours: rock (215,203,196) vs (216,205,199); greens (181,202,49) vs (171,195,33).
- Open minors (for review): clover clumps chunkier than the master's small rosettes; spire moss reads as a streak; shadow facets warmer than the master; collar's hollow hidden in the parts cell framing; Short/Tall/Leaning feet lighter than the master's.

## Goals (all MET at the passing build)

1. Spire base/height ≈ 0.55, angled peak · 2. left slab ≈ 50%, stepped slabs right and behind · 3. big front boulder + smaller front-left, foot steps outward · 4. Foot Collar = fused rim of 6 flat-topped blocks, tallest at the back, moss on three · 5. exploded: spire floating above its collar · 6. rock colour within 3 of the master · 7. lime greens in the master's range · 8. moss on ledges and the spire flank · 9. Short / Tall / Leaning distinct and as labelled · 10. budgets, origin, names, 0 problems · 11. no VFX (none in the master).
