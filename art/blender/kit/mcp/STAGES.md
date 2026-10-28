# Numbered-model stage procedure

How every numbered model (`art/blender/assets/references/NNN.png`, builders `mNNN.py`) is built. It follows the
`roblox-blender-model` skill (`.claude/skills/roblox-blender-model/SKILL.md`) and `WorldModeling.md` (read §1, §2,
§5, §12, §17 and §18). Each stage is its own agent, running on Opus 5.5 at high effort. Stages run strictly one
after another: only one agent drives the open Blender (`FlintbornWorldKit.blend`) through the MCP at any time.

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
