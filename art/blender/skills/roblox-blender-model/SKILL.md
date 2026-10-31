---
name: roblox-blender-model
description: Build or rebuild Blender models that match their reference images 1:1 and are production-ready for Roblox, through the Blender MCP, one model at a time with specialist stages and an independent verifier. Use when asked to model, rebuild or finish Roblox assets from reference sheets or images.
---

# Roblox Blender Modeling

Act as an expert 3D Technical Artist and Roblox Optimization Specialist. Build or rebuild Blender models that match their reference images 1:1 and are production-ready for Roblox.

## Inputs to establish first

Before any work, determine:

- Repository (if any) and its design doc (e.g. WorldModeling.md or similar art/modeling spec). Search the repo for it if not named.
- Blender file to work in, or whether to start a new one.
- References: either reference sheets inside the Blender file / repo, or image(s) attached in the conversation.
- Mode: single model (one reference) or batch (many models across sheets).

If something essential can't be found, ask once, briefly. Otherwise proceed.

All Blender work is done by writing and executing bpy scripts through the Blender MCP server. After every significant step, query the scene through MCP to inspect the actual result (mesh stats, object list, dimensions). Never assume a script worked without checking. If the MCP server is unreachable, stop and report that as a blocker.

## Step 1: Read and inventory

1. Read the design doc in full. Treat it as the source of truth for art style, naming, scale, poly budgets, texture rules, and export settings. If it conflicts with this skill, follow the design doc and report the conflict.
2. Inventory the work:
   - Every reference sheet/image and which models each contains
   - Every existing model, mapped to its reference
   - Current state of each (rough / partial / mostly done), current triangle count, specific problems
3. In batch mode, write the inventory to a tracking file (e.g. MODEL_PROGRESS.md) and keep it updated so progress survives across sessions.

Do not assume any existing model is correct. Audit every one against its reference. Rebuild from scratch when the existing mesh is a worse starting point than a clean rebuild.

## Step 2: Work one MODEL at a time (not one sheet at a time)

A sheet may contain several models. Finish and verify one model completely before starting the next, even if the next is on the same sheet.

### 2a. Study the reference

Before editing, analyze the model's reference individually and write down:

- Silhouette and overall proportions (measured against a known dimension)
- Every distinct part and sub-part, and how they connect
- Key structural details that define the shape and must survive optimization
- Exact colors (sample hex values from the reference), materials, surface finish (matte, glossy, metallic, emissive)
- Surface details: bevels, trim, panel lines, wear, patterns, decals
- Any lighting, glow, or effects shown
- All views provided (front, side, back, top, 3/4) - use every one
- Classification: full asset or accessory/small prop (sets the triangle budget)

### 2b. Split work across specialist subagents

Use a dedicated subagent per discipline. Give each the reference image(s), the notes from 2a, relevant design-doc rules, the technical requirements in 2c, and the previous stage's output.

1. Modeling: low-poly hard-surface geometry matching the reference 1:1 in silhouette, proportions, and detail. No subdivision modifiers (level 0); detail comes from deliberate edge placement, not density.
2. Optimization and cleanup: hit the triangle budget while preserving silhouette; meet every topology requirement.
3. UV unwrapping: per requirements below.
4. Materials and color: colors matching the reference, set up so they carry into Roblox.
5. Lighting: what the model needs to read correctly in Roblox (emissive surfaces, baked detail, light placement). Blender lights and shader effects do not export to Roblox - deliver lighting in a form Roblox can use and document the Studio-side setup.
6. VFX: glows, particles, trails, beams, or animated effects shown or implied. Roblox VFX use ParticleEmitter, Beam, Trail, and light objects plus textures, not Blender simulations. Produce required textures/flipbooks and a written spec (or Luau/rbxm setup) for the Studio side.

Skip a stage only if the reference clearly has nothing for it, and note that.

### 2c. Technical requirements (every model)

**Triangle budget**

- Under 4,000 triangles for a full asset; under 1,000 for accessories and small props, unless the design doc says otherwise.
- Measured on the triangulated mesh across all of the model's parts combined.
- If the reference genuinely can't be matched within budget, stop and report which details would be lost, rather than silently dropping them or exceeding the budget.

**Scale and origin**

- 1 Blender unit = 1 stud, unless the design doc defines another convention. Studs are not meters (Roblox treats 1 stud as roughly 0.28 m), so size things relative to Roblox characters (roughly 5-6 studs tall), not real-world meters.
- Origin at the bottom center of the model's bounding box.
- Apply rotation and scale; parts positioned correctly relative to the origin.
- Confirm the export settings produce the intended size in Studio and record the result.

**Topology and cleanup**

- Clean low-poly topology: quads where they serve the shape, triangles where cheaper. Roblox counts triangles, so don't force quads at the cost of budget. No n-gons on curved surfaces.
- Zero non-manifold geometry, interior faces, hidden/unseen faces, loose vertices or edges, and overlapping or zero-area faces.
- Merge by distance to remove duplicate vertices.
- Clear custom split normals, recalculate normals outward, set shading deliberately (flat for hard edges, smooth with sharp edges marked where needed).
- Remove unused modifiers, data blocks, materials, and empty objects.

**Part separation**

- Split into separate named mesh objects only when it helps: different materials/textures, parts moved or scripted separately in Roblox, or parts needing different collision. Each mesh object becomes its own MeshPart, so unnecessary splits cost performance.
- Name every object descriptively and consistently with the design doc (e.g. Sword_Blade, Sword_Handle).

**UV mapping**

- Marked seams or Smart UV Project, whichever stretches less for that part.
- No overlapping islands unless mirroring is intentional; consistent texel density; minimal stretching.
- Island margin of at least 2 px at the target resolution (about 0.002 in UV space at 1024x1024).

**Materials and color**

- One Principled BSDF material per distinct surface color/finish, clearly named, base color sampled from the reference.
- Default to flat, vibrant colors. Use full PBR maps (Color, Normal, Metalness, Roughness for SurfaceAppearance) only where the reference shows detail flat color can't reproduce. Max texture size 1024x1024.
- Ensure colors survive import into Roblox: if base-color-only materials don't carry over with the export settings in use, bake to a small palette texture or document the MeshPart Color values to set in Studio.

### 2d. Inspect via MCP

After building and cleaning each model, query through MCP and record:

- Triangle, face, and vertex count per object and total
- Object names, dimensions in studs, origin location
- Non-manifold / loose geometry check results (must be zero)
- Material list and texture sizes
- Remaining issues

### 2e. Independent verification before moving on

Launch a separate verifier subagent that did NOT work on this model. It must:

- Render the model from the same angles as the reference views and compare side by side
- Check silhouette, proportions, part count, colors (hex match), materials, and details against the reference
- Independently re-check every requirement in 2c through MCP (don't trust the builder's numbers)
- Return pass/fail with an itemized list of every discrepancy

On fail, send findings to the relevant specialist(s), fix, and re-verify with a fresh verifier. Repeat until pass. Only then confirm the model is ready for FBX/OBJ export, mark it done, and start the next model.

"Perfect" means: a reviewer comparing render and reference side by side finds no visible differences in shape, proportion, color, or detail, and every technical requirement is met.

## Step 3: Version control (when working in a repository)

- Before editing, identify the active version branch and create a descriptive working branch from it. Never work directly on main or a version branch.
- Commit regularly with clear messages (e.g. one commit per finished model). Use Git LFS for .blend and texture files if the repo is set up for it.
- When complete and validated: push the working branch, check CI, merge into the originating version branch, validate, then merge into main.
- Never delete, force-push, or rewrite main or any version branch.
- Nothing deploys or publishes to Roblox except from main.

## Step 4: Reporting

When finished or blocked, summarize every model as:

- Completed / Passed (export-ready)
- Requires Manual Validation (e.g. in-Studio check of scale, colors, VFX, or lighting)
- Incomplete / Needs Work (exactly what remains and why)

If blocked (MCP server unreachable, reference missing or unreadable, budget undefined, model can't match its reference within budget), state exactly what is blocked, why, and what is needed. Don't guess around it silently.

In batch mode, keep going model by model until all are verified or a genuine blocker is hit.
