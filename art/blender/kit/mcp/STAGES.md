# Numbered-model stage procedure

**Agent grouping (user decision, 2026-10-28, revised the same day to speed things up):**
- **Three modellers at a time**, one model each, all Opus 5.5 at high effort, each started with a fresh context. Each modeller does stages 1–6 (modelling, optimisation and cleanup, UV, materials/colour/texture, lighting, VFX) in its own background Blender (see "Parallel sessions").
- **The main session is the hub.** It:
  - starts the modellers;
  - owns the open GUI Blender (`FlintbornWorldKit.blend`);
  - puts each finished model into it;
  - does stage 7, the final verification (it built none of the model);
  - exports, commits and merges.
- Every modeller first loads the `roblox-blender-model` skill (Skill tool), then reads this file and the model's spec.
- Each modeller still runs every check listed for its stages below and records each stage in the spec under its own heading.
- Verification findings go back to a modeller (a fresh one if the first has finished). A model gets at most 2 verification rounds; after that the main session commits it with the leftovers noted, unless something is actually broken.
- A non-Blender study agent writes the next models' 2a studies ahead of time.
- Passed models are batched into one PR into the version branch every 3–5 models; each model still gets its own commit.

## Parallel sessions

Each modeller drives its own live Blender. The open GUI (`FlintbornWorldKit.blend`, the MCP tool, port 9876)
belongs to the main session for integration and verification. Modellers use background Blender processes running
the same MCP bridge on their own ports (9877–9879), driven through
`bgmcp.py` (tested 2026-10-28: an M014 build there gave the same tris, sizes and renders as the GUI, mean pixel
difference 0.02/255):

```bash
PY=C:/Users/Orang/.local/bin/python3.14.exe
$PY art/blender/kit/mcp/bgmcp.py start <port> art/blender/assets/kit/wip/MNNN.blend   # once, at the start
$PY art/blender/kit/mcp/bgmcp.py run <port> <code.py>       # or `run <port> -` with a heredoc; prints the JSON response
$PY art/blender/kit/mcp/bgmcp.py stop <port>                # when your stages are done
```

- **State.** The session keeps its state between calls, exactly like the MCP tool, so run, read back, render and look as usual. Assign a dict to `result`. Put longer code in a scratchpad `.py` file.
- **Work file and port.** The main session gives you a port and a work copy of the kit file at `art/blender/assets/kit/wip/MNNN.blend` (gitignored). Save that file after every good build, so a crash loses nothing. Never open or save `FlintbornWorldKit.blend` from a background session.
- **Renders.** These go to `art/blender/renders/models/MNNN/` as usual. Read them with the Read tool.
- **No viewport.** `K.focus` does nothing in the background; everything else works.
- **Crashes.** A crash takes down only that session, and the log is `art/blender/logs/bgmcp-<port>.log`. Restart with `start` on the saved work file.
- **Shared helpers are frozen while sessions run in parallel.** Don't edit `kit_models.py`, `kit_mcp.py`, `build_kit.py` or `lib/vfx.py`. Put new helpers in your own `mNNN.py`. If a shared change is truly needed, report it and the main session makes it.
- **Into the kit file.** When a model passes, the main session runs `mNNN.build()` in the GUI kit file (the builder is the source of truth), saves it, checks that the renders match, then exports and commits.

How every numbered model (`art/blender/assets/references/NNN.png`, builders `mNNN.py`) is built. It follows the
`roblox-blender-model` skill (`.claude/skills/roblox-blender-model/SKILL.md`) and `WorldModeling.md` (read §1, §2,
§5, §12, §17 and §18). Agents run on Opus 5.5 at high effort and are grouped as described above. Each Blender
session (the GUI or a background one) is driven by only one agent at a time.

## Rules for every stage

- **Source of truth.** `art/blender/kit/mcp/mNNN.py` is the model.
  - Change the model by editing this builder, then rebuild in the open Blender:
    `import importlib, kit_models, mNNN; importlib.reload(kit_models); importlib.reload(mNNN); mNNN.build()`.
  - Never hand-edit meshes that the builder would overwrite.
  - Load the helpers once if `NS` is empty:
    `import sys; sys.path.insert(0, "D:/Projects/Roblox/RBLX-Flintborn/art/blender/kit/mcp"); import kit_mcp; kit_mcp.install()`.
- **Shared tools** live in `kit_models.py` (M) and `kit_mcp.py` (K). Read them before writing new code.
  - M: `mk`, `union_loose`, `carve`, `merge_in`, `finish`, `audit`, `views`, `display`, `sample`, `raw_sample`, `drop_specks`.
  - K: `hull_rock`, `blend`, `mix_key`, `noise_field`, `texture`, `refine`, `set_colour`, `calibrate`, `socket`, `check`.
- **Check every step through the MCP.** Never assume a script worked. Read back the counts, sizes and materials.
- **Booleans.** Exact booleans can crash Blender (a 2026-10-28 crash was in `meshintersect::find_patches`). Feed them clean manifold inputs with no coplanar or coincident faces, add pieces one at a time, and save between risky steps.
- **Look at the renders.** `build()` writes `art/blender/renders/models/MNNN/` (single views plus `MNNN_views.png`). Open them with the Read tool and compare them with the reference, view by view.
- **No commits, pushes or exports.** The main session does those.
- **Scope.** Don't touch other models' collections or objects, and don't save over another sheet's names (`M.mk` guards this).
- **Record.** Write what the stage did and why into `art/blender/renders/models/MNNN/MNNN_spec.md`, under a heading for the stage.
- **Report.** Your final message lists what changed, the measured numbers and anything left for later stages.

## Stages

1. **Modelling.** Study the reference fully: every view, the exploded parts and the close-ups. Then write the 2a study into the spec.
   - Build each exploded-view part with its own function, check each one against its cell, and assemble the hero strictly from those parts.
   - Match the silhouette, proportions and part relationships 1:1. Use deliberate low-poly planes; no subdivision.
   - Leave colour to stage 4: one placeholder key per material region is fine.
2. **Optimisation and cleanup.** Hero under 4000 tris and each part under 1000, keeping the silhouette.
   - Zero non-manifold, boundary, wire or loose elements; no zero-area faces or n-gons; normals outward.
   - One closed shell for the hero unless the sheet shows separate pieces.
   - Origin at bottom centre and transforms applied. No interior faces left by the unions.
3. **UV.** Smart UV (margin at least 0.008) or seams, whichever stretches less; no overlaps; even texel density.
   - The exporter writes its own palette UVs. The UV layer must still exist and be clean.
4. **Materials, colour and texture.** This stage decides how the model reads, so take the most care here.
   - **Sample.** Sample every material on the master sheet: swatches with `M.raw_sample`, and rendered areas with `M.sample` or `K.sample` with kind stone, brown, green or vivid. Record the hexes.
   - **Calibrate.** Run `K.calibrate({key: (target_srgb, kind)})` so the studio render matches the sheet's render, not just the swatch. Write the calibrated hexes into `palette()`, then re-measure the final renders against the sheet.
   - **Blend.** Colours must blend into their neighbours the way they do on the sheet. Use `K.blend(..., mode="blend", steps=3)` across bands of faces, for example light to mid to dark across a crystal, or stone weathering. Avoid hard random patches.
     - Use `mode="hard"` only where two genuinely different materials meet, such as crystal against rock.
     - Never choose colour by which way a face points; light tops and dark sides come from the lighting.
   - **Texture.** Give broad, per-region Tint mottling (`Asset(tint_var=…)` / `face_tint_var`). Mottling should be visible, but never per-triangle confetti.
   - **Finish.** Set roughness, metal and specular per material as the sheet's finish shows.
5. **Lighting.** Decide what the model needs to read in Roblox. Blender lights don't export.
   - If the sheet shows emissive parts, give them emission ≥ 1.0; they export as Neon glow pieces.
   - Note any Studio-side settings in the spec.
   - Skip this stage only if the sheet shows nothing for it, and record that.
6. **VFX.** Add a socket wherever the sheet shows or implies glow, sparkle, embers, smoke, dust or similar, using the `fx=[(kind, loc, overrides)]` list in `M.mk` (kinds in `art/blender/lib/vfx.py`).
   - Check the export STATS line reports the sockets.
   - Skip this stage only if the sheet clearly has none, and record that.
7. **Verification.** Done by a fresh agent that did no other stage.
   - It is read-only in Blender.
   - It re-measures everything through the MCP and compares every view with the sheet, including colours by sampling both images.
   - It returns PASS or FAIL with an itemised list.
   - On FAIL, the findings go back to the relevant stage, then a new verifier checks again.
