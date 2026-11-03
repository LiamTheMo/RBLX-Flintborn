# World kit orchestration handoff

This is how the 34-sheet world kit is built and how to keep it going. Read it top to bottom before starting a run.

## Goal

The user supplied 34 master reference sheets in `art/reference/kit/`: World `W01`–`W16`, Resources `R01`–`R08` and Vegetation `V01`–`V10`. Each sheet has 4 subjects (rows), 136 models in all.

- **What a model is:** a Blender build of one subject, as close to its master reference as possible. It comes with all its parts and variations (or drops and a depleted state), all related VFX, Roblox-ready (triangle budgets, one mesh per asset, collision tags), and saved for reuse in one big map.
- **Who does the work:** one builder agent per model, then an independent verifier agent, then a fix round.
- **Batch size:** 4 sheets per run.
- **Progress:** `art/reference/kit/CHECKLIST.md`.

## The user's standing instructions

1. **Waves of 4 sheets,** using the workflow script below (one agent per model, separate verifiers).
2. **Goals.** Every builder writes goals from its master reference before modelling, then marks them met or unmet **by eye** after every build. Every verifier writes its own goals from the reference before looking at the build. A model passes only at resemblance ≥ 7 with every must goal met.
3. **Proper colouring, but lighting is not paint.** Materials get rich colour (related shade keys for real regions, broad Tint texture); the owner removed the old one-colour rule on 2026-10-27. Faces are still never coloured by which way they face; the runner's `baked_shading` check enforces that.
4. **Water, falling water, mist, smoke and vapour are VFX, never meshes.** Water exports as a tiled, semi-transparent texture. Anything under water gets a deep `<sheet>_riverbed` colour.
5. **Photo updates and checklist.** Send the user the compare image at each model's final verdict (pass, or fail after the fix round), and `CHECKLIST.md` per run. Don't send one per build: that's part of the token budget below.
6. **Auto-continue.** Always resume when usage limits reset, using an hourly cron job that runs the "next batch" steps below.
7. **Token budget** (the user approved it after repeated limit hits). The workflow script already enforces it:
   - Agents read only `art/blender/kit/BUILDER_GUIDE.md`.
   - One fix round.
   - Builders at medium effort, at most 4 builds.
   - Planners and verifiers on Sonnet.
   - Verifiers grade from the runner's stats JSON and compare image, without rebuilding or exporting.
   - Keep the orchestrator session short: hand off again when it grows long.
8. **Never commit or push** unless the user asks. All work is on branch `feat/kit-pilot` and is uncommitted so far.

## Files

| Path | What it is |
| --- | --- |
| `art/blender/kit/BUILDER_GUIDE.md` | the one page every agent reads: module contract, API, rules, VFX kinds, commands |
| `art/blender/kit/orchestrator/kit-wave.js` | the workflow script: plan, then build, verify and fix for each model. Takes `args.sheets` |
| `art/blender/kit/orchestrator/kit_watch.py` | watcher: `--active`, `--next 4` (Workflow args for the next batch), `--once` (rewrite the checklist), or no flag (stream final verdicts for Monitor) |
| `art/blender/kit/orchestrator/kit_active.json` | the run in progress (`runId`, `taskId`, `sheets`, `done`); git-ignored |
| `art/blender/kit_export_sheet.sh` | `kit_export_sheet.sh W07 W08 ...` builds each sheet's `.blend` and exports it to `art/roblox/kit/<SHEET>/`; run it after every run |
| `art/blender/scripts/build_kit.py`, `kit/<SHEET>/<module>.py` | the runner and one module per model |
| `art/blender/scripts/kit_crop_refs.py` | reference row crops (all 34 are done; W14 uses a manual override) |
| `art/blender/README.md` → "World kit" | full pipeline documentation |

## Running the next batch

1. `python art/blender/kit/orchestrator/kit_watch.py --active`. If it prints `running …`, wait.
2. `python art/blender/kit/orchestrator/kit_watch.py --next 4` prints the Workflow args. They contain:
   - `skip` for models that passed or failed after their fix round;
   - `verifyFirst` for models that are built but unchecked;
   - `rework` for models that broke the colour, water or foliage rules;
   - everything else gets a normal build.
3. Launch: run the Workflow tool with `scriptPath` = `art/blender/kit/orchestrator/kit-wave.js` (absolute path) and those args.
4. Write `{"runId", "taskId", "sheets"}` to `kit_active.json`.
5. Arm Monitor on `kit_watch.py`, with a 30-minute timeout; re-arm it whenever it expires. Each `FINAL` line means: send the user that compare image with a one-line caption.
6. When the run completes:
   - set `"done": true` in `kit_active.json`;
   - run `kit_export_sheet.sh` for its sheets;
   - send `CHECKLIST.md`;
   - start the next batch.

   If many agents stop with "session limit", the next hourly cron check relaunches after the reset.

Use the Python at `C:/Users/Orang/.local/bin/python3.14.exe`. Run Blender only through `art/blender/run.sh` (see AGENTS.md).

## State at handoff (2026-10-26)

- **Passed (12):**
  - W01: PebbleScatter, RockCluster
  - R01: CoalNode, CopperNode, FlintNode
  - W02: CliffWall
  - W03: ShoreIslet, StreambedPatch, WaterfallModule
  - W04: Sapling
  - W06: MossAndIvy, HangingVine
- **Set aside for the user's review (⚠️):** Boulder, RockSpire, StoneNode, NaturalArch, NaturalRamp, TerracedLedge, RiverbankChunk, YoungFir.
- **Queued for rework:** the W04, W05 and W06 foliage models that failed, which now get rebuilt with the new `canopy` and `leaf_cluster` helpers.
- **Next sheet:** W07.
- **Exported:** W01–W06 to `art/roblox/kit/`. All 6 have 0 problems.
- **To check in Studio:**
  - W03 has 393 VFX sockets, mostly `water_foam` and `water_flow`, which may be heavy.
  - Beam orientation, TextureSpeed units and texture wrap are unverified (see README).

## Lessons learned (don't repeat)

- **Verifier goals.** A re-check must grade the previous verifier's goals, not invent new ones. The script does this.
- **Colour.** Builders pick colours to match the render, not the reference swatch; the kit studio uses the "Medium High Contrast" look.
- **Foliage.** Use `Asset.canopy` and `Asset.leaf_cluster`, not single blobs.
- **Vertex hazard.** `rock()`, `ico(subdiv>=2)`, and `ico` or `leaf_blob` with `facets=` invalidate verts returned earlier on the same Asset.
- **Shared files.** Edit shared library files atomically (temp copy, then rename) while runs are active: agents import them on every build.
