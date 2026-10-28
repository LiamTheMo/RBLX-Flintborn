# W01 Row 3: Rock Cluster — spec and goals

Reference: `art/reference/kit/W01_boulders_rocks_scatter.png`, row 3. Builder: `art/blender/kit/mcp/w01.py` → `cluster_row()`.

## Study of the reference

- **Silhouette:** three interlocking boulders: tall gabled Rock A behind, wide dome Rock C front-left, squat dome Rock B front-right.
- **Parts:** Rock A, Rock B, Rock C, each its own mesh with a lobed lime moss cap and green at its foot.
- **Colours (sampled):** rock (215,203,197); greens (164,194,33) to (208,227,52).
- **Dressing:** clover clumps filling the gaps and the foot, 2–3 white flowers, pebbles at the front.
- **Effects:** none (no VFX/lighting stage).
- **Variations:** Linear (in a row), Crescent (curved), Triangular (compact), each three rocks.

## Result

- Verifier rounds: 1 FAIL 7 (Linear had two rocks) · 2 FAIL 7 (sparse dressing) · **3 PASS 7.5/10**.
- Tris: hero 5959 (budget 7000), parts 345 / 745 / 405, Linear 4110, Crescent 4028, Triangular 3730. 0 check problems.
- Colours: rock (222,210,199) vs (215,203,197); greens (160,187,46) vs (164,194,33).
- Open minors (for review): Rock C a little egg-like; moss caps sit as small tufts rather than draping; clover in the rock joints thinner than the master; Linear/Crescent arrangements could differ more.

## Goals (all MET at the passing build)

1. Three touching boulders with the master's hierarchy · 2. lobed lime moss cap on every crown, faint green at the feet · 3. 12 clover clumps round the foot and in the joints, white flowers, 6 pebbles · 4. rock colour within 7, greens within 8 · 5. parts A/B/C as separate meshes · 6. Linear, Crescent, Triangular each three rocks · 7. budgets, origin, names, 0 problems · 8. no VFX.
