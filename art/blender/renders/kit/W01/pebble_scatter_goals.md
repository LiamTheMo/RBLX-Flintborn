# W01 Pebble Scatter — asset spec and verification (MCP rework, 2026-10-27)

```yaml
asset_id: PebbleScatter (W01 row 4)
builder: art/blender/kit/mcp/w01.py (pebble_row)
parts_first: [Flat Slab (low plate, flat top plane, angular bevels, thin moss at one end),
              Wedge Rock (blocky, thin moss tuft on top), Round Rock (squat, damp moss stain low on one side),
              Pebble, Small Stone]
hero: pieces spread apart with gaps (as the master's top view shows): slab centre-left, tall angular rock behind,
      wedge rock right, round rock front-right, small stones; clover clumps with daisies at the rocks' feet
variants: [Sparse (3 pieces), Medium (5), Dense (9)]
collision: none for the scatter sets and small stones; hull for the larger single pieces
budget: hero 3656 / 4500; variants 1042 / 2040 / 3232
vfx: none (the master shows none)
```

## Verification (haiku verifier, own 16 goals)

- Pass 1: 6/10. Slab was a smooth lozenge, Round Rock egg-shaped, heavy wedge moss, loose clumps, wrong piece counts.
- Pass 2: 8/10, after a flat-topped plate slab, squat Round Rock, small tuft, clumps at the feet and 3/5/9 pieces.
- Final: larger daisies, thinner slab moss, slightly warmer stone.

Status: **Completed / Passed** (Blender renders). Exported to `art/roblox/kit/W01/` with 0 problems.
**Requires Manual Validation**: Studio import.
