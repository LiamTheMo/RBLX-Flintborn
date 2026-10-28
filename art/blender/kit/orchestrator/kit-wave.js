export const meta = {
  name: 'kit-wave',
  description: 'Build a wave of world-kit sheets: plan each sheet, one goal-driven builder per model, independent goal-based verifier, fix loop',
  whenToUse: 'Pass args.sheets = [{id, ref}] (4 sheets per wave). existing:true re-verifies modules that are already built.',
  phases: [
    { title: 'Plan', detail: 'one planner per sheet: 4 model specs, names, scale, palette, VFX' },
    { title: 'Build', detail: 'one goal-driven builder agent per model' },
    { title: 'Verify', detail: 'independent verifier writes its own goals from the reference first' },
    { title: 'Fix', detail: 'builder revises from unmet goals, up to 2 rounds' },
  ],
}

const REPO = 'D:/Projects/Roblox/RBLX-Flintborn'

const COMMON = `
You are working on Flintborn's world kit: reusable low-poly Blender models for a Roblox game, each built to match a master reference image as closely as possible. Repo: ${REPO} (git branch feat/kit-pilot; do NOT commit, push or switch branches). Work only from the shell running Blender headless; do NOT use the Blender MCP / GUI tools.

Read art/blender/kit/BUILDER_GUIDE.md first: it is the whole API, the module contract and every rule, and it is all you need.
TOKEN BUDGET RULES (enforced; the user is hitting usage limits):
- Do NOT open art/blender/lib/flintkit.py, vfx.py, kitwater.py, scripts/build_kit.py, scripts/export_kit_roblox.py, art/blender/README.md, the lobby scripts build_0*.py, or other models' modules. If you need one signature the guide lacks, grep that single def with a few lines of context.
- Never cat whole files or full logs: use the run.sh summary and grep for KITPROBLEM / KITSTAT.
- Read an image only when it has changed. Read the compare image; open a single cell only for a specific doubt. No extra renders.
- Keep your final result concise.

`

const GOALS_RULES = `
GOALS — mandatory, this is how your work is judged:
1. BEFORE writing any modelling code, study the reference row image and the full sheet, then write a goals file at GOALS_PATH. List at least 15 concrete, checkable visual goals, grouped by reference cell (ASSEMBLED/HERO, FRONT, SIDE, TOP, PARTS, VARIATIONS or DROPS/DEPLETED). Tag each "must" or "should". Make them measurable from a render, e.g. "hero is ~1.4x wider than tall", "moss drapes over the top ~40% and runs down the front-left facet", "front view shows 8-12 large facets, no noisy small ones", "3 white flowers in the base foliage", "rope lashing wraps both post joints twice", "top view: round crown of 5 clumps". Include palette goals (the ONE base colour of each material, sampled from its mid-tone, and where each material sits) and scale goals in studs. Never write goals about painting light or dark sides: the light/dark you see on the reference is lighting.
2. After EVERY build, read the compare image and update the goals file: mark each goal MET or UNMET with one line of evidence from the render. Judge each goal BY EYE, comparing your row cell by cell with the reference row directly above it: would a viewer see the same silhouette, proportions, clump sizes and colours? Your own measurements (bounding-box ratios, counts, tri numbers) support a judgement but never prove a visual goal; verifiers have repeatedly failed builders who marked goals MET from numbers alone. Keep a short iteration log at the bottom (what you changed, what improved).
3. You may not finish while any "must" goal is UNMET, unless it is genuinely impossible within the conventions — then say why in the goals file and in open_issues. Run at least 3 build-look-fix iterations, and stop as soon as every "must" goal is MET (at most 4 builds). Be economical: don't re-read images that haven't changed, and read only the parts of the shared libraries you need. Aim for a viewer to recognise your row as the same objects as the reference row, cell for cell.
4. Return the final goals list (goal, priority, met, evidence) in your structured result. An independent verifier will write its own goals from the reference and audit yours; goals you mark MET that are not met count against you.
`

const BUILD_RULES = `
Build rules:
- You own exactly one file: MODULE_PATH (create or revise it). Do not edit flintkit.py, vfx.py, build_kit.py, run.sh or any other module; other agents build other modules in parallel. Shared-library needs go in shared_lib_requests.
- Colours: palette keys only. Use the sheet palette below exactly as given (copy every key you use into your module's PALETTE dict verbatim, so all modules of the sheet agree), plus existing PALETTE/KIT_PALETTE keys. Any further colour gets a key prefixed with the lower-case sheet id, sampled from the reference.
- Build and render with (from the repo root; timeout 600000 ms):
    BUILD_CMD
  It prints KITSTAT lines (tris/budget, size in studs) and must end with "0 problems". It renders COMPARE_PATH: the reference row on top, your row below (hero iso, front, side, top, parts, then variants or drops and depleted), with cells in the _cells folder beside it. READ the compare image after every build.
- Roblox-ready optimisation: stay under the triangle budget (lower is better; spend triangles on silhouette, not hidden faces); nothing below z=0 (cut or flatten buried undersides); no pointless hidden interior geometry; each asset is ONE mesh object with its origin at the bottom centre; collision tagged sensibly (box/hull solid, precise for walkable/hollow shapes like arches, stairs, ledges, bridges, huts; none for small scatter players walk through).
- ONE COLOUR PER MATERIAL. Every material gets exactly one palette key: never light/dark/cool/deep/lit/shadow/pale/tip variants of a material, under any name. The light and dark sides in the reference are LIGHTING: Blender and Roblox shade the faces. Choose each material's single base colour so that your RENDER matches the reference: lit faces as bright and saturated as the reference's lit faces, and shadow faces as dark as its shadow faces. Start from the reference's middle tone (between its lit and shadow sides, not the lit highlight). If your render looks paler or greyer than the reference, darken and saturate the base colour. Foliage especially tends to render washed out. Distinct materials (moss vs leaves vs grass, bark vs heartwood, ore vs host rock) each get their own single key. The runner rejects shade sets: keys that differ only by a shade word, or same-kind materials with near colours.
- WATER AND VAPOUR ARE VFX (from the user). Falling water, waterfalls, spray, splash, mist, foam lines, flow streaks, smoke, steam and vapour are VFX sockets, never meshes. Use a waterfall_curtain beam socket at the top lip with end=(x, y, z) where the fall meets the pool (several side by side for a wide fall), waterfall_mist where it lands, water_foam along shore lines and pool rims, water_flow beams lying on rivers and streams (start to end = the flow direction), vapour for steam and haze, and chimney_smoke or campfire for smoke. Water SURFACES (pools, rivers, lakes, sea) stay simple flat meshes with a water palette key (water, water_shallow, water_deep or a sheet-prefixed *_water* key). The exporter turns them into a tiled, semi-transparent water texture in Roblox, so don't fake ripples or foam in geometry. The master references show deep, saturated cyan water, and semi-transparent water shows what lies beneath it. So anything under the water (riverbed, pool floor, seabed, submerged rock bases) gets a deep blue-teal underwater colour around #0B6E8F: one key per sheet named '<sheet>_riverbed'. Never use 'water' in its name; that would make it see-through. Light sand or soil sits only on the shore above the waterline. Keep flow streaks subtle. If the reference's PARTS column shows a curtain, foam ribbon, splash disc, foam ring or flow strip, it becomes a socket on the assets that use it, not a part asset; list it in kit.tag notes.
- LIGHTING IS NOT PAINT. The light tops, dark sides and soft gradients in the reference come from the sun and sky, not from the colours. Give each material ONE flat base colour (rock is one grey, a canopy is one green; choose it so the render matches the reference's lit and shadow tones), shape the facets, and let the renderer and Roblox's lighting shade them. Never pick a lighter material or a higher Tint for upward/sunward faces, or a darker one for downward/shadow faces. Tint stays a small random per-part variation (about +/-7%). Use a second colour only where the reference shows a genuinely different material (moss on rock, cut wood ends, rope, a darker bark band, ore inserts, snow). The runner measures this and reports 'lighting is painted into the colours' as a problem; a real material change may set obj['kit_shading_ok'] = 'reason'.
- Camera: if the sheet draws the hero from another side, set module-level HERO_AZIMUTH (degrees, default -22 = front-left; e.g. +22 front-right), and SIDE_AZIMUTH = 135 when the SIDE/REAR cell shows the back (e.g. connector plates). The parts cell lays parts out in a compact grid automatically.
- Every labelled part in the PARTS column is its own part asset, and every variation is its own asset, with the PascalCase names in your spec.
- VFX: include every effect the reference implies (flames, lantern glow, water foam/mist/flow, glowing crystals/resin/embers, harvest bursts on resource nodes). Emissive meshes carry the static look; sockets carry the live effect. Note each socket's purpose in kit.tag notes.
`

const PLAN_SCHEMA = {
  type: 'object',
  properties: {
    sheet: { type: 'string' },
    kind: { type: 'string', enum: ['world', 'resource', 'vegetation'] },
    palette: { type: 'array', items: { type: 'object', properties: {
      key: { type: 'string' }, hex: { type: 'string' }, roughness: { type: 'number' }, metallic: { type: 'number' },
      emission: { type: 'number' }, use: { type: 'string' } }, required: ['key', 'hex', 'roughness', 'metallic', 'emission', 'use'] } },
    models: { type: 'array', items: { type: 'object', properties: {
      row: { type: 'number' }, module: { type: 'string' }, subject: { type: 'string' },
      spec: { type: 'string', description: 'full build spec: hero description and size in studs, every part name, every variant/drop/depleted name with caption, budgets, collision, VFX plan' } },
      required: ['row', 'module', 'subject', 'spec'] } },
    notes: { type: 'string' },
  },
  required: ['sheet', 'kind', 'palette', 'models'],
}

const BUILD_SCHEMA = {
  type: 'object',
  properties: {
    module_file: { type: 'string' },
    goals_file: { type: 'string' },
    goals: { type: 'array', items: { type: 'object', properties: {
      goal: { type: 'string' }, priority: { type: 'string', enum: ['must', 'should'] }, met: { type: 'boolean' }, evidence: { type: 'string' } },
      required: ['goal', 'priority', 'met'] } },
    assets: { type: 'array', items: { type: 'object', properties: {
      name: { type: 'string' }, role: { type: 'string' }, tris: { type: 'number' }, studs: { type: 'string' } }, required: ['name', 'role', 'tris'] } },
    vfx: { type: 'array', items: { type: 'string' } },
    iterations: { type: 'number' },
    self_assessment: { type: 'string' },
    open_issues: { type: 'array', items: { type: 'string' } },
    shared_lib_requests: { type: 'array', items: { type: 'string' } },
  },
  required: ['module_file', 'goals_file', 'goals', 'assets', 'self_assessment'],
}

const VERDICT_SCHEMA = {
  type: 'object',
  properties: {
    verdict: { type: 'string', enum: ['pass', 'fail'] },
    resemblance: { type: 'number', description: '1-10, how closely the row matches the reference row' },
    own_goals: { type: 'array', items: { type: 'object', properties: {
      goal: { type: 'string' }, priority: { type: 'string', enum: ['must', 'should'] }, met: { type: 'boolean' }, evidence: { type: 'string' } },
      required: ['goal', 'priority', 'met', 'evidence'] } },
    builder_goal_audit: { type: 'string', description: 'which builder goals were wrongly marked met, or missing' },
    checks: { type: 'object', properties: {
      build_clean: { type: 'boolean' }, budgets_ok: { type: 'boolean' }, origin_ok: { type: 'boolean' },
      parts_complete: { type: 'boolean' }, variants_complete: { type: 'boolean' },
      collision_ok: { type: 'boolean' }, vfx_ok: { type: 'boolean' }, export_ok: { type: 'boolean' } } },
    fixes: { type: 'array', items: { type: 'object', properties: {
      priority: { type: 'string', enum: ['must', 'should', 'nice'] }, asset: { type: 'string' },
      issue: { type: 'string' }, fix: { type: 'string' } }, required: ['priority', 'issue', 'fix'] } },
    summary: { type: 'string' },
  },
  required: ['verdict', 'resemblance', 'own_goals', 'builder_goal_audit', 'checks', 'fixes', 'summary'],
}

function P(sheet, m) {
  return {
    module: `art/blender/scripts/kit/${sheet.id}/${m.module}.py`,
    goals: `art/blender/renders/kit/${sheet.id}/${m.module}_goals.md`,
    cmd: `BLENDER_ARGS="${sheet.id} --only ${m.module}" art/blender/run.sh scripts/build_kit.py art/blender/assets/kit/wip/${sheet.id}_${m.module}.blend`,
    compare: `art/blender/renders/kit/${sheet.id}/${m.module}_compare.png`,
    cells: `art/blender/renders/kit/${sheet.id}/${m.module}_cells/`,
    row: `art/reference/kit/rows/${sheet.id}_row${m.row}.png`,
    wip: `art/blender/assets/kit/wip/${sheet.id}_${m.module}.blend`,
    stats: `art/blender/assets/kit/wip/${sheet.id}_${m.module}_stats.json`,
  }
}

function planPrompt(sheet) {
  return `${COMMON}
You are the PLANNER for kit sheet ${sheet.id}. Reference sheet: ${sheet.ref}. Its four subject rows, at full resolution: art/reference/kit/rows/${sheet.id}_row1.png ... _row4.png. Read all five images closely.
If art/blender/scripts/kit/${sheet.id}/ already contains modules (from an earlier, interrupted run), keep their module file names, SUBJECTs and asset names exactly (read them) and write the specs to match, so work already done is kept.
Produce the build plan for the sheet's 4 subjects (one model = one row = one module), so four builder agents working in parallel produce a consistent sheet:
- kind: "world" (map dressing / structures), "resource" (harvestable node with DROPS and a Depleted state) or "vegetation" (plants; if the sheet shows harvested / fruitless / clipped states, those are role "depleted" and any separate pickups shown are role "drop").
- WATER AND VAPOUR ARE VFX (from the user). Falling water, waterfalls, spray, splash, mist, foam lines, flow streaks, smoke, steam and vapour are VFX sockets, never meshes. Use a waterfall_curtain beam socket at the top lip with end=(x, y, z) where the fall meets the pool (several side by side for a wide fall), waterfall_mist where it lands, water_foam along shore lines and pool rims, water_flow beams lying on rivers and streams (start to end = the flow direction), vapour for steam and haze, and chimney_smoke or campfire for smoke. Water SURFACES (pools, rivers, lakes, sea) stay simple flat meshes with a water palette key (water, water_shallow, water_deep or a sheet-prefixed *_water* key). The exporter turns them into a tiled, semi-transparent water texture in Roblox, so don't fake ripples or foam in geometry. The master references show deep, saturated cyan water, and semi-transparent water shows what lies beneath it. So anything under the water (riverbed, pool floor, seabed, submerged rock bases) gets a deep blue-teal underwater colour around #0B6E8F: one key per sheet named '<sheet>_riverbed'. Never use 'water' in its name; that would make it see-through. Light sand or soil sits only on the shore above the waterline. Keep flow streaks subtle. If the reference's PARTS column shows a curtain, foam ribbon, splash disc, foam ring or flow strip, it becomes a socket on the assets that use it, not a part asset; list it in kit.tag notes.
- palette: ONE COLOUR PER MATERIAL. Every material gets exactly one palette key: never light/dark/cool/deep/lit/shadow/pale/tip variants of a material, under any name. The light and dark sides in the reference are LIGHTING: Blender and Roblox shade the faces. Choose each material's single base colour so that your RENDER matches the reference: lit faces as bright and saturated as the reference's lit faces, and shadow faces as dark as its shadow faces. Start from the reference's middle tone (between its lit and shadow sides, not the lit highlight). If your render looks paler or greyer than the reference, darken and saturate the base colour. Foliage especially tends to render washed out. Distinct materials (moss vs leaves vs grass, bark vs heartwood, ore vs host rock) each get their own single key. The runner rejects shade sets: keys that differ only by a shade word, or same-kind materials with near colours. The sheet's shared colours, sampled from the reference swatches and art (hex), with roughness/metallic/emission. Keys lower-case, prefixed "${sheet.id.toLowerCase()}_", unless an existing flintkit PALETTE/KIT_PALETTE key already matches closely (then list that existing key with its existing values). Emissive colours (fire, lantern glass, glowing crystal/resin) get emission > 0 (1.0+ reads as Neon in Roblox).
- For each row: module (snake_case file name), subject (PascalCase), row number, and a full spec: what the hero is and its size in studs (a Roblox character is 5.5 studs; terrain modules snap to a 32-stud grid like the lobby terrain kit; doorways >= 4 wide x 7 tall; walkable decks/paths/stairs sized for players), the exact PascalCase asset name for the hero, EVERY labelled part, and EVERY variation (or drops + depleted) with its caption; per-asset triangle budget where it should differ from the defaults (hero/variant 3000, part 1500, depleted 2000, drop 300; large terrain, buildings and big trees up to 8000); collision per asset; the VFX each asset needs (socket kind, where, colour overrides) — include every effect the reference implies (fire, lanterns, water flow/foam/mist, glows); and the 3-6 most distinctive visual traits a builder must not miss.
Return the structured plan.`
}

function kindNotes(kind) {
  if (kind === 'resource') return `RESOURCE sheet: build the hero node, each labelled part, the drop item(s) (role "drop", ~1-1.3 studs, collision box, <=300 tris) and the depleted state (role "depleted", same footprint, low base). VFX required: harvest_hit on the strike face at mid height (color = the chips' material), harvest_deplete at the base centre, ore_glint only on glossy/metallic/crystal ore, and a coloured PointLight + motes (via overrides) for glowing materials.`
  if (kind === 'vegetation') return `VEGETATION sheet: build the hero plant, each labelled part, and each variation; harvested/fruitless/clipped states are role "depleted"; separate pickups are role "drop". Plants players walk through use collision "none"; trees and big shrubs use hull. If it is harvestable, add a harvest_hit socket coloured like leaves/petals.`
  return `WORLD sheet: build the hero (ASSEMBLED), every labelled part (PARTS) and the three VARIATIONS. Include the small dressing the reference shows around bases (rubble stones, leafy clumps, flowers, grass) in the hero and variant meshes.`
}

function builderPrompt(sheet, plan, m, feedback) {
  const p = P(sheet, m)
  const pal = plan.palette.map(c => `  "${c.key}": ("${c.hex}", ${c.roughness}, ${c.metallic}, ${c.emission}),  # ${c.use}`).join('\n')
  return `${COMMON}
${kindNotes(plan.kind)}

YOUR MODEL: sheet ${sheet.id}, module "${m.module}", SUBJECT = "${m.subject}", ROW = ${m.row}.
${m.spec}
Sheet palette (shared by all four modules of ${sheet.id}):
${pal}
Planner notes for the sheet: ${plan.notes || '-'}
Reference: full sheet ${sheet.ref}; your row at full resolution ${p.row}. Read both images closely before planning.
${GOALS_RULES.replace('GOALS_PATH', p.goals)}
${BUILD_RULES.replace('MODULE_PATH', p.module).replace('BUILD_CMD', p.cmd).replace('COMPARE_PATH', p.compare)}
If ${p.module} or ${p.goals} already exist from an earlier, interrupted run, read them and CONTINUE from them rather than starting over.
${feedback ? `\nREVISION: ${p.module} and ${p.goals} already exist. An independent verifier FAILED them. Add every unmet verifier goal below to your goals file as a "must", fix every "must" fix and as many "should" fixes as you can, keep what already works, and iterate until those goals are MET:\n${feedback}\n` : ''}
Return the structured result.`
}

function verifierPrompt(sheet, plan, m, built, prior) {
  const p = P(sheet, m)
  return `${COMMON}
You are an INDEPENDENT, skeptical VERIFIER for one model of the kit. Another agent built it; find where it falls short of the master reference. Do NOT edit ${p.module}, its goals file, or any repo file; any extra renders go in your own scratchpad, never the repo. Default to "fail" when the row is clearly distinguishable from the reference in silhouette, proportions, colour or detail, or any hard check fails.
${kindNotes(plan.kind)}
Model: sheet ${sheet.id}, subject ${m.subject}, row ${m.row}. Spec: ${m.spec}

${prior ? `THIS IS A RE-CHECK AFTER A FIX. The previous verifier set these goals, and the builder was asked to meet them; they are the contract, so do not move the goalposts:
${prior.own_goals.map(g => `- [${g.priority}] ${g.goal}`).join('\n')}
Step 1 — grade EVERY one of these goals first (copy them into own_goals with met/evidence). You may add at most 3 NEW must-goals, only for clear, significant defects the previous check missed or the fix introduced; mark their text with "(new)". Judge resemblance on the same scale as before (previous score: ${prior.resemblance}/10); if the fix improved the goals it targeted, the score should not drop unless you name the regression.
Then continue from Step 2.
` : ''}${prior ? 'For reference, the original first-check instructions were: ' : ''}Step 1 — YOUR OWN GOALS FIRST. Before opening the module, the builder's goals file or any render, read the reference row ${p.row} and the full sheet ${sheet.ref}, and write at least 15 concrete, checkable goals of your own (must/should), grouped by reference cell, covering silhouette and proportions, facet style, base colour of each material (judge colour on the mid-tone; light/dark facets come from lighting and must NOT be painted in — painted-in shading, or a material split into several shades (rock + rock_cool, needle_dark/needle/needle_light), is a must-fix), secondary detail and its counts, parts, variations/drops/depleted, scale in studs, and VFX.
Step 2 — do NOT rebuild. Read the runner's stats file ${p.stats}: it is the honest record of the latest build (assets, tris vs budget, studs, materials, shade_pairs, baked_shading, problems). build_clean = its problems list is empty. Rebuild with ${p.cmd} only if the stats file is missing.
Step 3 — read the compare image ${p.compare} (reference on top, model below). Open a single cell in ${p.cells} only for a specific doubt. No extra renders.
Step 4 — grade every one of YOUR goals met/unmet with evidence. Then read the builder's goals file ${p.goals} and audit it: list goals they marked MET that are not, and important goals they missed.
Step 5 — hard checks: every part and variation/drop/depleted in the spec exists with its name; tris under budget and sensible for Roblox; origin bottom-centre; nothing below z=0; collision tags sensible; VFX sockets present where the reference implies them, with sensible colours and positions.
Step 6 — Roblox export is run once per sheet after the run, not by you: set export_ok = true.

The builder reported: ${built ? JSON.stringify({ assets: built.assets, vfx: built.vfx, self_assessment: built.self_assessment, open_issues: built.open_issues }) : '(no report; the module may predate this run — judge the files as they are)'}

Verdict "pass" ONLY if resemblance >= 7, every one of your "must" goals is met, and every hard check holds. Return your goals with evidence, the audit, the checks, a prioritised list of concrete fixes (asset, what is wrong, exactly what to change), and a short summary.`
}

const REWORK_NOTE = `REWORK. If this is a tree, bush, fern or other foliage model, rebuild its crowns and leaf clumps with the shared helpers Asset.canopy / Asset.leaf_cluster (see BUILDER_GUIDE.md): they give the reference's dense, lumpy cauliflower crowns, which single blobs cannot. Also (from the user): the model hard-codes lighting into its colours. It splits materials into lit and shadow shades (e.g. rock_light / rock / rock_cool, needle_dark / needle / needle_light / needle_tip, bark_light / bark_dark), but the reference's light and dark sides are caused by LIGHTING and shadow. Rework the colours: keep exactly ONE palette key per material (chosen so the render matches the reference's lit and shadow tones), remove every shade variant and the code that picks between them by height, direction, tier or at random, keep Tint variation small (within about +/-10%), and let geometry plus the studio light do the shading. The runner now reports any remaining shade pairs as problems: get to 0 problems. Then re-check the compare image and your goals file, and fix anything the colour change broke. Also, if the model has water, waterfalls, foam, flow strips, mist, smoke or steam: WATER AND VAPOUR ARE VFX (from the user). Falling water, waterfalls, spray, splash, mist, foam lines, flow streaks, smoke, steam and vapour are VFX sockets, never meshes. Use a waterfall_curtain beam socket at the top lip with end=(x, y, z) where the fall meets the pool (several side by side for a wide fall), waterfall_mist where it lands, water_foam along shore lines and pool rims, water_flow beams lying on rivers and streams (start to end = the flow direction), vapour for steam and haze, and chimney_smoke or campfire for smoke. Water SURFACES (pools, rivers, lakes, sea) stay simple flat meshes with a water palette key (water, water_shallow, water_deep or a sheet-prefixed *_water* key). The exporter turns them into a tiled, semi-transparent water texture in Roblox, so don't fake ripples or foam in geometry. The master references show deep, saturated cyan water, and semi-transparent water shows what lies beneath it. So anything under the water (riverbed, pool floor, seabed, submerged rock bases) gets a deep blue-teal underwater colour around #0B6E8F: one key per sheet named '<sheet>_riverbed'. Never use 'water' in its name; that would make it see-through. Light sand or soil sits only on the shore above the waterline. Keep flow streaks subtle. If the reference's PARTS column shows a curtain, foam ribbon, splash disc, foam ring or flow strip, it becomes a socket on the assets that use it, not a part asset; list it in kit.tag notes. Remove the meshes that stood in for those effects and add the sockets. Keep the shapes, parts, variants and VFX that already work.`

function feedbackText(v) {
  const unmet = v.own_goals.filter(g => !g.met).map(g => `- [${g.priority}] GOAL: ${g.goal} (verifier saw: ${g.evidence})`).join('\n')
  const fixes = v.fixes.map(f => `- [${f.priority}] ${f.asset ? f.asset + ': ' : ''}${f.issue} -> ${f.fix}`).join('\n')
  return `Verifier: ${v.verdict}, resemblance ${v.resemblance}/10. ${v.summary}\nChecks: ${JSON.stringify(v.checks)}\nAudit of your goals: ${v.builder_goal_audit}\nUnmet verifier goals:\n${unmet}\nFixes:\n${fixes}`
}

async function modelLoop(sheet, plan, m) {
  const tag = `${sheet.id}/${m.module}`
  if ((sheet.skip || []).includes(m.module)) return { model: tag, subject: m.subject, skipped: 'already passed' }
  const VOPTS = { phase: 'Verify', schema: VERDICT_SCHEMA, model: 'sonnet', effort: 'medium' }
  let built = null
  if ((sheet.rework || []).includes(m.module)) {
    built = await agent(builderPrompt(sheet, plan, m, REWORK_NOTE), { label: `rework:${tag}`, phase: 'Fix', schema: BUILD_SCHEMA, effort: 'medium' })
    if (!built) return { model: tag, subject: m.subject, stopped: 'rework did not finish (usage limit or error)' }
  } else if (!(sheet.verifyFirst || []).includes(m.module)) {
    built = await agent(builderPrompt(sheet, plan, m, null), { label: `build:${tag}`, phase: 'Build', schema: BUILD_SCHEMA, effort: 'medium' })
    if (!built) return { model: tag, subject: m.subject, stopped: 'builder did not finish (usage limit or error)' }
  }
  let v = await agent(verifierPrompt(sheet, plan, m, built), { ...VOPTS, label: `verify:${tag}` })
  const history = [v]
  for (let round = 1; round <= 1 && v && v.verdict === 'fail'; round++) {  // one fix round (token budget)
    log(`${tag} failed verification (${v.resemblance}/10, ${v.own_goals.filter(g => !g.met && g.priority === 'must').length} must-goals unmet), fix round ${round}`)
    const fixed = await agent(builderPrompt(sheet, plan, m, feedbackText(v)), { label: `fix${round}:${tag}`, phase: 'Fix', schema: BUILD_SCHEMA, effort: 'medium' })
    if (!fixed) break
    built = fixed
    v = await agent(verifierPrompt(sheet, plan, m, built, v), { ...VOPTS, label: `reverify${round}:${tag}` })
    history.push(v)
  }
  const final = history.filter(Boolean).slice(-1)[0]
  return {
    model: tag, subject: m.subject,
    assets: built ? built.assets : null, shared_lib_requests: built ? built.shared_lib_requests : [],
    rounds: history.filter(Boolean).map(x => ({ verdict: x.verdict, resemblance: x.resemblance,
      must_unmet: x.own_goals.filter(g => !g.met && g.priority === 'must').length })),
    final: final ? { verdict: final.verdict, resemblance: final.resemblance, checks: final.checks, summary: final.summary,
      unmet_goals: final.own_goals.filter(g => !g.met).map(g => `[${g.priority}] ${g.goal}`),
      open_fixes: final.fixes.filter(f => f.priority !== 'nice').map(f => `[${f.priority}] ${f.asset || ''} ${f.issue}`) } : null,
  }
}

const sheets = args.sheets
const results = await pipeline(
  sheets,
  sheet => agent(planPrompt(sheet), { label: `plan:${sheet.id}`, phase: 'Plan', schema: PLAN_SCHEMA, model: 'sonnet', effort: 'medium' }),
  (plan, sheet) => {
    log(`${sheet.id} planned: ${plan.models.map(m => m.subject).join(', ')}`)
    return parallel(plan.models.map(m => () => modelLoop(sheet, plan, m)))
      .then(rs => ({ sheet: sheet.id, kind: plan.kind, palette: plan.palette.map(c => c.key), models: rs.filter(Boolean) }))
  },
)
return results.filter(Boolean)
