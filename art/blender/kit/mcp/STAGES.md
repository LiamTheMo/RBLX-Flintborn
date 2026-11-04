# Numbered-model stage procedure

**Agent grouping (user decisions of 2026-10-28, revised 2026-11-04 for speed):**
- **Two new-model modellers at a time** (user decision, 2026-11-04). Fix modellers and verifiers come on top of that, but never more than **5 Blender agents in all** (the machine has 32 GB and 16 cores). Each agent runs on the high-effort model and starts with a fresh context. A modeller does stages 1–6 (modelling, optimisation and cleanup, UV, materials/colour/texture, lighting, VFX) for one model in its own background Blender (see "Parallel sessions").
- **No separate study stage** (2026-11-04). The modeller writes a one-page brief (`BRIEF_TEMPLATE.md`) as its first step, answering everything the sheet doesn't decide from `HOUSE_RULES.md`. It doesn't wait for rulings; it notes departures and carries on.
- **Family builders.** Sheets that are variants of one design (ore deposits, picked/depleted states, building sets, gear tiers, armor sets) get one parametric builder for the family. Each sheet's `mNNN.py` calls it with that sheet's parameters.
- **A separate verifier, with a fresh context, does stage 7.** It didn't do any other stage. The user wants clean context, because context bloat hurts the modelling. It works read-only in its own background Blender, on a copy of the kit file taken after the model has been put into it.
- **Verification is sized to the model** (2026-11-04):
  - **Small models** (prop and asset classes, nothing to walk into): one verifier checks 3–4 of them in one session, in one round. On a fail, a fix modeller fixes it, and the main session confirms the fix with `kit_verify` and the compare image instead of a second verifier, unless the blocker was visual.
  - **Large models** (structures, buildings, landmarks, anything enterable): one model per verifier, up to two rounds, as before.
  - The pass bar is the same for both.
- **The main session is the hub.** It:
  - starts every agent;
  - owns the open GUI Blender (`FlintbornWorldKit.blend`);
  - puts each finished model into it (`mNNN.build()` there, then save);
  - rules on verifier results;
  - exports, commits and merges.
- **Every agent starts with a fresh context** (a new agent, never a fork or a continuation of a finished one). It loads exactly what its job needs: the `roblox-blender-model` skill (Skill tool), this file, the model's spec, and the reference. Modellers also read the builder. Fixes after a failed verification go to a fresh modeller.
- Each modeller still runs every check listed for its stages below and records each stage in the spec under its own heading.
- Verification findings go back to a modeller (a fresh one if the first has finished). A model gets at most 2 verification rounds; after that the main session commits it with the leftovers noted, unless something is actually broken or the model's defining feature still reads clearly unlike the sheet. In those cases a targeted third round fixes only the named blockers (018's leaf rosette was the first).
- Each passed model gets its own commit, straight on the active version branch (no feature branch or PR; owner's decision, 2026-11-04). Commits stay local: the owner pushes.

## Shared library (2026-11-04)

Build every new model on the shared library, in the light work file. A builder is then a few hundred lines of
model-specific shapes and data (`demo_m067.py`, 396 lines, rebuilds 067 exactly: m067.py is 1,582).
- **`kit_parts.py` (P): the pieces.** Closed, outward-wound, flat-shaded shells with defaults from the best passed
  model: `plank` (chamfered, V-seam option), `plank_wall` (board rows and butt joints that close), `post` (pyramid tip,
  foot bands), `log`, `leg`, `bolt`, `stairs`, `rope` / `rope_turn` / `rope_band` / `x_lashing` / `strap`, `canvas`
  (sag, hem, thickness, holes), `banner` / `emblem` / `banner_set`, `crate`, `barrel`, `lantern` (glass key) /
  `bracket`, `block` (chamfers, chips), `rock`, `stone`, `moss`, `leaf` (m070's tent leaf that passes the 5° sweep),
  `ivy`; and the core `shell` / `prism` / `box` / `ext` / `beam` / `hull`, `frame()` placement, `earclip`. Every named
  piece goes into the register kit_verify reads. The file's docstring lists the API.
- **`kit_build.py` (B): the scaffold.** `MODEL = B.Model(NNN, title, palette=PALETTE, targets=TARGETS)`, then
  `MODEL.run(hero=(name, fn), parts=..., notes=..., collision=..., budgets=..., target_size=..., points=..., fx=...,
  views=...)` builds the parts and hero, cleans them (normals, bowties, ear-clipped n-gons, UVs, origin), stores points
  and sockets, puts them on display, calls `kit_verify.run` and renders. Default renders: the sheet views you list, an
  exploded view and a scale view, all on `MNNN_views.png`; close-ups, part shots and the spin only when asked. Add
  model-specific checks with `checks=[fn]`; pass kit_verify's optional checks with `verify={...}`.
- **The light work file.** `art/blender/assets/kit/wip/LIGHT.blend` (3.3 MB against the kit's 36 MB): the studio,
  the Kit collection and every palette material, no models. Copy it to `wip/MNNN.blend` and start bgmcp on that copy.
  Make or refresh it with `make_workfile.py` (its docstring says how; `--keep M067` keeps a model to build next to).
  In a background session it opens about 3x faster, renders about 3x faster and saves about 5x faster than a kit copy,
  and a build there gives the same tris, sizes, offsets and materials as in the kit file.
- **New reusable pieces go into `kit_parts.py` only through the main session.** A modeller who needs one writes it in
  its own `mNNN.py` and reports it; the main session moves it into the library. The same holds for `kit_build.py`.

## Parallel sessions

Each modeller drives its own live Blender. The open GUI (`FlintbornWorldKit.blend`, the MCP tool, port 9876)
belongs to the main session for integration and verification. Modellers use background Blender processes running
the same MCP bridge on their own ports, driven through `bgmcp.py`. The main session gives each agent a port that no
running session holds; check with `Get-CimInstance Win32_Process -Filter "Name='blender.exe'"` before assigning one
(a 024 verifier was once given 9880 while 027's modeller held it). Tested 2026-10-28: an M014 build there gave the
same tris, sizes and renders as the GUI, mean pixel difference 0.02/255.

```bash
PY=python3                                     # the owner's uv Python on Windows, or Blender's own: "<blender dir>/5.2/python/bin/python.exe"
export BLENDER_PATH=...                         # if blender.exe is not at D:/Steam/steamapps/common/Blender/
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
`roblox-blender-model` skill (`art/blender/skills/roblox-blender-model/SKILL.md`) and `docs/art/WorldModeling.md` (read §1, §2,
§5, §12, §17 and §18). Agents run on the high-effort model and are grouped as described above. Each Blender
session (the GUI or a background one) is driven by only one agent at a time.

## Rules for every stage

- **Source of truth.** `art/blender/kit/mcp/mNNN.py` is the model.
  - Change the model by editing this builder, then rebuild in the open Blender:
    `import importlib, kit_models, mNNN; importlib.reload(kit_models); importlib.reload(mNNN); mNNN.build()`.
  - Never hand-edit meshes that the builder would overwrite.
  - Load the helpers once if `NS` is empty:
    `import sys; sys.path.insert(0, "<repo>/art/blender/kit/mcp"); import kit_mcp; kit_mcp.install()`, where `<repo>` is this checkout's root.
- **Shared tools** live in `kit_models.py` (M) and `kit_mcp.py` (K). Read them before writing new code.
  - M: `mk`, `union_loose`, `carve`, `merge_in`, `finish`, `audit`, `views`, `display`, `sample`, `raw_sample`, `drop_specks`.
  - K: `hull_rock`, `blend`, `mix_key`, `noise_field`, `texture`, `refine`, `set_colour`, `calibrate`, `socket`, `check`.
- **Check every step through the MCP.** Never assume a script worked. Read back the counts, sizes and materials.
- **Bowtie vertices.** `M.audit()` reports `nonmanifold_verts`: two closed face fans meeting at one vertex, which edge checks miss. It must be 0 on every object. `M.fix_bowties(o)` repairs them (019, 020 and 021 had them at leaf hubs).
- **Consistent winding.** Check every shell for faces wound against their neighbours. A positive total volume does not prove the normals are right: 044's wedge back face pointed inward, and Roblox would cull it into a see-through hole. Target 0 winding errors, reported in `build()`'s problems list.
- **No floating dressing.** In multi-shell models, every leaf, petal, flower, pebble and moss shell must sit within 0.03 of a neighbour, the rock or the ground, and must chain by contact to the ground or a rock. No "hidden stems". Count floating shells before reporting (035 and 036 both failed round 1 on this). Leaves are rounded clumps, not pointed ladders. Dressing must not be buried either: no shell more than 0.05 inside rock. Check this with ray parity against the full hero rock after the final placement step; 046 had whole leaves inside a mass core.
- **Foliage reads from every azimuth.** Never turn leaf cards or rosettes toward the front and rear cameras only. Turn them radially outward, or toward the nearest of eight views. 054, 057 and 058 all read as balls with edge-on flaps from the sides.
  - Before reporting, measure all eight azimuths with a ray-grid visibility check (`vis.py`, first written for 054). Targets in every view:
    - bare core at most about 15–30 % of the visible foliage;
    - edge-on **flat** cards at most 10 % (domed puffs and lumps always have an edge-on rim, so judge those by eye: no flaps, fins or slivers);
    - the skeleton showing where the sheet shows it.
  - **Check between the eight views too.** Leaves can be aimed at the gaps between the eight test angles and still turn edge-on there; 063's clusters faced exactly between them and showed combs of slivers at ±25° and ±65°.
    - Sweep the azimuth in 5° steps and count whole leaves within 15° of edge-on: at most about 10 % of the leaf area at any step.
      - A **whole leaf** is edge-on when at least 75 % of its lobe facets are within 15° of edge-on, or when its projected area falls under about 0.26 of its face-on area (a sliver). Both counts bind.
      - The share of leaves whose mean plane is within 15° of edge-on is reported only, not a limit: for flat leaves at any facings it averages about 1/6 of the leaf area (ruling on 063, 2026-11-01).
    - Pixel shares hide edge-on leaves, because they cover few pixels.
    - Leaves in one cluster must not share a plane. Give each its own facing.
  - Clump and rosette **parts** must match their cells' proportions (W : H). They must not be flat tiered tents or single cones.
- **Booleans.** Exact booleans can crash Blender (a 2026-10-28 crash was in `meshintersect::find_patches`). Feed them clean manifold inputs with no coplanar or coincident faces, add pieces one at a time, and save between risky steps. Run unions with the object at the origin, not at its display slot (x ≈ 500+): float32 matrix error there gave 030 hundreds of self-intersections. `M.union_loose` welds within 0.01, so use a merge-0 union for fine parts (`m021._union_fine`).
- **Look at the renders.** `build()` writes `art/blender/renders/models/MNNN/` (single views plus `MNNN_views.png`). Open them with the Read tool and compare them with the reference, view by view.
- **No commits, pushes or exports.** The main session does those.
- **Scope.** Don't touch other models' collections or objects, and don't save over another sheet's names (`M.mk` guards this).
- **Record.** Write what the stage did and why into `art/blender/renders/models/MNNN/MNNN_spec.md`, under a heading for the stage.
- **Report.** Your final message lists what changed, the measured numbers and anything left for later stages.

## Verify suite (2026-11-04)

The technical checks every modeller reports and every verifier re-measures are shared code now. Don't rewrite bmesh,
BVH or raster checks in a builder or a scratch file.
- **`kit_verify.run(objs, cls=..., **opts)`** runs every technical check in one call and returns the numbers plus a
  `problems` list (empty means clean) and the run time per check. It takes about 10 s for an 8000-tri building and
  its 12 parts, including the inside escape scan. It is read-only. `kit_verify.summary(r)` gives one line per object.
  - **Always:**
    - tris against the class budget (`cls`: `part` / `prop` < 1000, `asset` < 4000, `structure` ≤ 6000, `building`
      ≤ 8000; the hero and variants get `cls`, parts get `part`; `classes=` / `budgets=` override);
    - sizes (`size=`), origin at the bottom centre, transforms applied, no modifiers or custom normals;
    - non-manifold edges, bowties, boundary / wire / loose, zero-area faces, n-gons, duplicate verts;
    - per shell: winding errors, ray-parity inward faces, self-intersections, signed volume;
    - the thinnest face corner (floor 0.3°);
    - floating and unchained shells (contact ≤ 0.03, chained to the ground or another shell);
    - buried shells (> 0.05 inside another; `bury_pairs` for ruled exceptions such as rope in rope 0.08). Edge
      midpoints are sampled too, so it finds sinks that the builders' vertex and face-centre sampling misses: 070's
      ivy pads sit 0.07–0.08 inside their stems. `bury_edges=False` gives the builders' numbers;
    - pierces through thin sheets (`thin=`: canvas, banner, emblem, cloth, ...);
    - UV overlaps, flips, island gap and border;
    - Tint against the face normal per material (shading painted inside pieces);
    - sockets (`sockets=`) and stored points (`stored=`), and `K.check`.
  - Shells are named from the builder's piece register (`o["mNNN_pieces"]`) when there is one, else by material.
    Options and reports use the build frame when the object stores `mNNN_offset`.
  - **Optional checks, switched on by options:**
    - `foliage=`: the 5° azimuth sweep with the whole-leaf rule above;
    - `escape=`: the inside light-escape scan of an interior box, with `allow` boxes for doorways;
    - `walk=`: a 5.5-stud character proxy along paths, with clearance, intersections, rises, headroom and turning
      room;
    - `seams=`: tiling, a copy at the pitch, with no crossing, identical end sections and nothing past the seams.
  - The module docstring lists every option. Modellers pass the same options in `build()` and record the result in
    the spec.
- **`compare.compare(num, cells)`** crops each named cell from `references/NNN.png` (pixel boxes from the spec's §1),
  renders the model at the matching camera, and writes one side-by-side PNG per cell and one `MNNN_compare.png`, each
  pair labelled with its camera and the content W : H of both. A cell can be mirrored or turned. Output goes to
  `<temp>/RBLX-Flintborn/compare/MNNN/` unless `out_dir` is given.
- **Verifiers call both first**, quote their numbers, and then spend their time on the visual comparison: the
  compare sheet view by view, colours sampled from both images, close-ups. A verifier re-derives a number with its
  own code only when a result looks wrong; it reports that as a suite bug.
- **Shipping.** The main session ships a passed model with `art/blender/kit/ship.sh MNNN "message"`. It builds in the
  GUI, saves, exports, requires 0 export problems, checks the spec and builder for temp paths and assistant names,
  stages exactly the model's files and commits. It never pushes. `--dry-run` prints the steps.

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
