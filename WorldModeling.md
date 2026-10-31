# Flintborn — World Modeling Guide for Blender MCP

> Audience: an LLM controlling Blender through MCP, Python execution, scene inspection, and screenshots.
> Purpose: turn Flintborn's world and vegetation reference sheets into coherent, editable, reusable Roblox assets.
> Scope: foliage and vegetation in depth; supporting construction rules for terrain, resources, buildings, ruins, and props.
> Status: art production guidance. Numerical dimensions, mesh budgets, palette values, and botanical/rare-resource names below are **proposed modeling baselines**, not approved gameplay balance, spawn rates, map dimensions, or engine limits.

## Repository integration — read before the generic recipes

This guide supplements [visuals.md](visuals.md). [GDD.md](GDD.md) remains the gameplay authority; [Modeling.md](Modeling.md) covers the R6 survivor and creature pipeline. Follow [AGENTS.md](AGENTS.md) and [art/blender/README.md](art/blender/README.md) for the actual repository build and export contracts. If a generic example below differs from those contracts, **the repository contracts win**.

The current production pipeline already establishes:

- **Scale:** one Blender unit equals one Roblox stud, with front facing **-Y** and origin at the **bottom center**. Preserve the existing sheet dimensions rather than replacing them with this guide's exploratory character-relative ranges. The terrain kit uses a **32-stud grid**. Existing tree/plant dimensions are listed in the Blender README; for example, `PineTreeMature` is 17 studs wide by 24 tall, and `GrassClumpSmall` is 2 wide by 1.4 tall.
- **Shared code:** production sheet scripts import `art/blender/lib/flintkit.py`. Reuse its `Asset` builder, material lookup, studio camera, and sheet renderer. The standalone helper in section 7 is a geometry-study example, not a replacement production framework.
- **Palette and tint:** production materials use `flintkit.PALETTE` keys and a `Tint` color attribute. Use `leaf`, `leaf_light`, `leaf_dark`, `pine`, `pine_dark`, `bark`, `wood`, `flower_white`, `flower_yellow`, and `berry` as appropriate. The generic hex palette below is for isolated studies; do not install it over the shared palette. Unrepresented rare-plant colors need an explicit shared-palette extension before production export, not ad hoc per-asset materials. Custom geometry must preserve the expected `Tint` data; do not replace the shared tint shader to conceal a missing attribute.
- **Asset packaging:** finished static library assets are **one multi-material mesh object per asset**, named in PascalCase, marked as Blender assets, and organized by category. Separate editable construction pieces are useful during authoring and inspection, but consolidate an export/library copy through the existing builder. Preserve the editable source. Where a harvestable piece must be independently addressable at runtime, define a supported export/runtime contract first; otherwise deliver harvested states as separate complete asset variants.
- **Builds:** run existing sheet scripts through `art/blender/run.sh`, for example `art/blender/run.sh scripts/build_05_trees_plants.py`. The wrapper checks Python errors and whether expected outputs were actually rewritten. Do not replace it with bare Blender commands or pipe its output through an error filter. Rebuild a changed library sheet before rebuilding the lobby that links it. Only the main session controls the open Blender GUI through MCP.
- **Effects and export:** follow the existing VFX socket system in `art/blender/lib/vfx.py`. Lobby export uses the current `.glb`/palette texture/placement-manifest pipeline described in the Blender README. An FBX or loose multi-object export is not a drop-in substitute. Character export has its own separate contract.

The current release candidate is `v0.18`; remaining launch work is tracked in [docs/RELEASE_CHECKLIST.md](docs/RELEASE_CHECKLIST.md). This document does not mark those manual checks complete. Publishing this guide does not regenerate or upload art, replace existing Blender libraries, or change the live world layout.

## 1. Read this before touching the scene

Flintborn is a bright, cartoony, primitive survival and extraction game. Its world uses broad faceted rocks, stepped landforms, layered conifers, chunky leaves, warm timber, pale ruins, cream canvas, and turquoise water. Assets should look deliberately shaped by a person. They should not look like photorealistic scans, noisy procedural sculptures, smooth plastic blobs, or collections of arbitrary triangles.

The central modeling problem is **shape hierarchy**. Build a recognizable silhouette first, divide it into a few large functional parts, and then add only the small features that explain its identity. Do not compensate for a weak silhouette with more polygons, random colors, glowing effects, or decorative clutter.

For vegetation, the visual hierarchy is:

1. Overall plant silhouette: fan, rosette, umbrella, upright shrub, hanging vine, tiered conifer, or branching tree.
2. Structural skeleton: roots, main stem/trunk, and a small number of branches.
3. Foliage masses: broad leaves, fronds, tiers, or deliberately arranged clumps.
4. Signature feature: fruit, flower, nut, seedpod, resin pocket, unusual bark, or distinctive curl.
5. Optional small supporting details, only when the preceding four levels already read clearly.

An ordinary plant must still look intentional. A rare plant must still belong to the same world. Rarity is not permission to add machinery, elaborate runes, floating parts, excessive spikes, characters, or large particle clouds.

### 1.1 What the reference sheets mean

Use the supplied asset sheets as visual targets, not dimensionally exact engineering drawings. Their hero, front, side, and top views can disagree because they are generated concepts. Resolve such disagreements as follows:

- Explicit user instructions take priority.
- A user-selected hero view controls silhouette and character.
- The other views clarify attachment, thickness, back surfaces, and construction.
- Exploded parts describe useful separations; they do not require identical object counts when a cleaner mesh achieves the same result.
- Variations are different assets. Do not mix their shapes into one representative model.
- The illustrations sometimes include foliage around every root or stone. Those are optional dressing, not a requirement to merge a miniature landscape into each asset.
- Plant names are identification labels for art concepts. Do not infer real-world edibility, healing effects, harvesting tools, or gameplay rewards from them.

If views conflict, choose a coherent construction and record the interpretation. Continue without repeatedly asking the user to decide minor hidden surfaces. Ask only if a missing decision would substantially change the requested asset.

### 1.2 Non-negotiable visual rules

| Rule | Required behavior | Common incorrect interpretation |
| --- | --- | --- |
| Low poly | A few well-placed planes describe a form | Randomly triangulate everything |
| Chunky foliage | Broad, visibly thick blades and leaf lobes | Hundreds of thin needles or leaf cards |
| Flat shading | Planar lighting explains useful facets | Assign a different color to every face |
| Natural asymmetry | Controlled differences in width, lean, and branch placement | Add noise independently to every vertex |
| Reusable parts | Separate stems, foliage modules, pods, and overlays | Join an entire decorated scene into one mesh |
| Readability | A recognizable outline and clear negative space | Hide all structure inside dense foliage |
| Primitive fantasy | Natural materials and simple timber/stone craft | Industrial machinery, firearms, or science-fiction components |
| Rare identity | Distinct silhouette plus restrained color accents | An ordinary asset recolored neon with a glow halo |

## 2. Blender MCP working protocol

Do not assume the MCP server exposes specific tool names. First inspect its available capabilities. The required operations are conceptually: inspect scene, execute Blender Python if supported, view/capture the viewport or render, inspect object data, and save a project file. Use the actual tools exposed by the connected server.

### 2.1 Preflight

Before creating anything:

1. Report Blender's version, current file path, object count, active scene, active mode, and available rendering/capture capabilities.
2. Identify the current asset collection, its origin, its object names, and any existing reference images.
3. Inspect existing materials and scale calibration. Reuse established project settings instead of silently replacing them.
4. Confirm that Python execution, if available, runs inside the same Blender scene the screenshots show.
5. Read this document and inspect the selected reference at useful resolution. Describe its silhouette and part hierarchy in a short asset specification.
6. Save a checkpoint of an existing project before a substantial change. Use the user's authorized output directory; do not invent a path and claim it was saved.

Never start with `select_all` followed by global delete. Do not clear every collection, material, image, or world datablock. Work in a clearly named asset collection and replace only objects that your current generator owns.

### 2.2 Build one representative asset first

For a large sheet or family, start with one representative middle-sized asset. Finish and inspect it before making 10–50 variants. A flawed generator multiplied across a scene creates more cleanup, not progress.

Use these gates in order:

| Gate | Build | Inspect | Pass condition |
| --- | --- | --- | --- |
| A — silhouette | Skeleton and large masses only | Front, side, top, three-quarter | Plant family reads without color or tiny detail |
| B — construction | Leaf, branch, flower, and attachment geometry | Close side and underside | Thickness, taper, and attachments make physical sense |
| C — material | Shared flat-color materials | Neutral rendered view and material preview | Colors match the intended family; no noise or accidental glass |
| D — identity | Signature fruit, bloom, pod, resin, or bark feature | Small on-screen thumbnail | Identity remains visible at normal gameplay distance |
| E — variants | Controlled young, mature, wide, sparse, or harvested variants | Side-by-side contact sheet | Silhouettes differ; each still belongs to the same family |
| F — delivery | Clean transforms, origin, export copy, simple collision plan | Mesh report and target-app import when available | No missing parts, wrong scale, or unexplained export changes |

At each gate: capture an actual screenshot, inspect it, state one or two concrete mismatches, adjust the responsible parameters, and capture again. Do not claim visual verification from a successful Python return value alone.

### 2.3 Keep execution recoverable

- Use bounded scripts: setup, one primitive, one assembly, one inspection. Avoid a single opaque script that creates an entire biome and immediately exports it.
- Prefer the data API for custom meshes and material assignment. Operators are acceptable when needed, but explicitly establish their object/mode context.
- Store all generation parameters in one specification and use a local seeded random generator. A rerun should produce the same asset.
- Tag generated objects with an owner identifier and asset identifier. Check the tag before deleting or replacing objects.
- Reuse meshes and materials where appropriate. Do not create `LeafGreen.001` through `LeafGreen.400` on successive runs.
- On failure, inspect the exception and the partially created objects. Repair or regenerate only the failing asset.
- Do not retry an unchanged broken script repeatedly. Isolate the failing operation in a minimal example.
- If Python execution is unavailable, use the exposed modeling tools and the same gate sequence. Do not invent an `execute_code` capability.

## 3. Coordinates, scale, pivots, and collections

### 3.1 Coordinate contract

Use Blender Z as up. Use X/Y for the ground plane. Put each asset's root pivot at its planting point or structural placement point, normally local `(0, 0, 0)`. Roots may extend slightly below this plane. Keep the visible asset above it unless it intentionally enters water or soil.

For a new project without calibration, a useful **working convention** is one Blender modeling unit equals one intended Roblox stud. This is a project convention, not a claim about Blender's physical meter settings or automatic importer conversion. Record the export/import scale and verify a calibration cube in Roblox before committing a whole library. Do not apply a second conversion just because a scene unit label says meters.

Let `C` be the height of the actual target R6 character measured in the target scene. All plant scale decisions should be checked against that character or an equivalent calibration proxy. Do not assume every Roblox avatar has the same measured height.

### 3.2 Starting size ranges

These are starting ranges to prevent accidental giant grass and tiny trees. Match the selected image and gameplay needs if they differ.

| Family | Approximate height relative to C | Other useful proportion |
| --- | --- | --- |
| Sparse ground cover | 0.03–0.10 C | Patch width 2–5 times height |
| Grass / small herb | 0.08–0.25 C | Individual broad blade width 0.08–0.22 of blade length |
| Flowering herb | 0.15–0.40 C | Bloom diameter 0.25–0.55 of overall height |
| Ordinary forage shrub | 0.25–0.65 C | Width 0.9–1.6 times height |
| Fern | 0.18–0.45 C | Spread 1.1–1.8 times height |
| Reeds / tall wetland plants | 0.35–0.85 C | Keep stalk count low and gaps visible |
| Sapling | 0.45–1.20 C | Clear single trunk or fork |
| Ordinary tree | 1.4–3.5 C | Canopy width depends on species; do not standardize every tree |
| Rare landmark tree / giant growth | 2.5–5.0 C initially | Requires a placement and sightline check |

For example only, if the calibrated character is 5 modeling units tall, a 0.2 C herb is 1 unit tall. Replace 5 with the actual measured character height when it differs.

### 3.3 Collection and object organization

Suggested structure:

```text
FB_WORLD_LIBRARY
  FB_CALIBRATION
  FB_MATERIALS_PREVIEW
  FB_VEG_Raspberry_A
    FB_VEG_Raspberry_A_ROOT
    ..._Stem_01
    ..._LeafCluster_01
    ..._Fruit_01
  FB_VEG_Raspberry_Harvested
  FB_TERRAIN_CliffStraight_A
  FB_STRUCTURE_TimberGate_A
  FB_RESOURCE_CopperNode_A
  FB_PREVIEW_ONLY
```

The root is a parent empty or an equivalent assembly root. Its children keep meaningful names. Avoid using names such as `Cube.058` to identify export-critical pieces.

Keep authoring sources separate from export copies. Keep preview ground planes, cameras, lights, labels, and exploded-view duplicates out of asset exports. A plant should not accidentally include the studio floor.

## 4. Asset specification before geometry

Write a compact specification like this before running a generator:

```yaml
asset_id: FB_VEG_Raspberry_A
reference: V02 — Common Bushes & Forage / Raspberry Bush hero
intent: common forage shrub concept
height_in_character_units: 0.42
width_over_height: 1.2
silhouette: open three-cane shrub with irregular rounded crown
primary_parts: [3 canes, 2 short forks, 5 foliage groups]
signature_parts: [5 removable berry bunches]
leaf_module: thick pointed three-leaf cluster
negative_space: visible trunk fork and two gaps through crown
materials: [BarkMid, BarkDark, LeafMid, LeafLight, BerryRed]
seed: 2104
variants: [young, full_fruiting, harvested]
pivot: ground center beneath main fork
collision: simple trunk/base proxy only if needed
checkpoints: [silhouette, leaf closeup, full asset, variants]
```

Use explicit count and proportion parameters. Replace “make lush low-poly foliage” with “five foliage groups, each 0.28–0.40 of crown width, arranged around three canes, leaving the lower third of the canes visible.”

## 5. Material and color construction

### 5.1 Shared palette

The following sRGB swatches are approximations derived from the established art direction, not exact colors sampled from a master texture. Use them as starting materials, compare under neutral lighting, and adjust the family together.

| Material | sRGB hex | Use |
| --- | --- | --- |
| LeafDark | `#356D36` | Deep foliage undersides and conifer lower tiers |
| LeafMid | `#69A53D` | Main ordinary broadleaf material |
| LeafLight | `#A0C94C` | Selected top-facing foliage masses |
| LeafLime | `#C0D95A` | Young growth and sunny canopy accents |
| LeafSage | `#91B39A` | Silkleaf and cooler herbs |
| LeafTeal | `#407D70` | Juniper and restrained rare plant accents |
| BarkDark | `#65432D` | Recesses and cut branch junctions |
| BarkMid | `#916039` | Main trunks and branches |
| BarkLight | `#BB8451` | Broad exposed wood planes |
| PaleBark | `#D6D5BF` | Birch / Silverbark concept trunks |
| Cream | `#F0E4BE` | Pale flowers, mushroom stalks, seed tufts |
| FlowerYellow | `#E8BB36` | Flower centers and ordinary yellow blooms |
| BerryRed | `#CF413A` | Red berry masses |
| BerryBlue | `#3F5C94` | Blue-black berry masses |
| FlowerPurple | `#9264BD` | Purple flowers and cave fungus concepts |
| Amber | `#D9942E` | Resin and rare seed accents |
| StoneMid | `#A29E96` | Warm pale-gray world rock |
| SoilMid | `#806246` | Optional small root plugs |

### 5.2 Surface rules

- Start with nonmetallic, opaque materials and roughness approximately 0.75–0.95.
- Create a clear base color in both viewport material settings and render shader nodes. A material can look correct in solid view while rendering gray if the node shader was not configured.
- Convert sRGB color values correctly if assigning linear shader color inputs programmatically. Do not treat hex bytes divided by 255 as guaranteed correct linear-light values.
- Use geometry and lighting for most facet contrast. Assign 2–3 related foliage shades to meaningful clumps or upper/underside regions, not random triangle confetti.
- Avoid noise textures, bump maps, displacement, leaf vein textures, realistic bark, metallic foliage, and glassy berries in the baseline style.
- Leaf thickness is real geometry. Do not depend on a two-sided shader setting to hide an infinitely thin surface.
- Resin, ice, and crystals may use simple accent shading, but must remain readable without transparency, bloom, or emission. Exported target-engine materials may not reproduce Blender shaders automatically.
- Record the view transform and exposure used for approval renders. Lighting and color management can shift saturated greens; do not keep recoloring meshes to compensate for an inconsistent preview setup.

## 6. Topology language: make large planes earn their place

Every added edge should control silhouette, a bend, thickness, an attachment, or a visible color/material boundary. If it does none of those, question it.

### 6.1 Broad solid leaf

This is the most important primitive in the library. Do not model every leaf as a cone, stretched sphere, or flat triangle.

Build a leaf with a base, two shoulder points, two widest-belly points, one tip, and one shallow front ridge. Add a back ridge to close the volume. Its outline should narrow at the stem, widen through the middle, and taper toward the tip.

Useful starting proportions:

- Length `L` follows the main growth direction.
- Width `W` is about 0.30–0.55 L for a broad herb leaf, 0.18–0.30 L for a narrow leaf, and 0.08–0.20 L for a grass blade.
- Widest point sits about 0.50–0.65 L from the base, not at the tip.
- Visible central camber is about 0.04–0.10 L.
- A slight tip bend is about 0.05–0.16 L. Bend a few purposeful stations; do not add a noise modifier.
- Back thickness is small but nonzero. The full cross-section should be a shallow folded wedge, not a puffy rugby ball.

Use 10–20 triangles as a useful starting envelope for a very simple individual leaf. Increase only to express a needed serration, lobe, or bend. This is not a hard engine limit.

For a heart-shaped leaf, move the two shoulders outward near the base and introduce a shallow base notch. For a strap leaf, keep width through more of its length and round the tip with two or three large edges. For a toothed dandelion leaf, add two or three **large** tooth pairs to the outline; do not create dozens of tiny serrations.

### 6.2 Grass blade and sedge fan

A grass blade is a narrow folded leaf with a broad readable base and one or two bends. Use a central ridge and two side strips, then close the underside or give the blade a thin closed cross-section. Avoid cylinders ending in sharp cones; those read as spikes, not grass.

Assemble 3–7 blades per ordinary tuft. Vary height and lean, but preserve a family rhythm: one tall blade, two medium blades, two shorter outer blades. Spread the blades away from a shared root. Do not make a perfectly radial porcupine ball with 20 identical spikes.

For sedge, make the blades stiffer, more upright, and visibly folded. For dry tussock, bend the outer blades downward and use a warm tan material on whole blades. Do not sprinkle brown triangles randomly across a green tuft.

### 6.3 Stem, branch, and root

Use a 5–8-sided tapered tube, with 2–5 major direction changes when a bend is needed. Branches should generally taper toward their tips. A child branch's radius might begin around 0.35–0.65 of its parent's radius at the junction, depending on species and exaggeration.

Let branch bases enter the parent slightly so joints do not float. Do not leave open gaps. For repeated side branches, separate overlapped tubes are acceptable in authoring if the seam is hidden and the exported result reads cleanly. Merge or rebuild conspicuous junctions when the silhouette exposes them. Boolean union and remeshing are not the default solution.

Roots are broader, lower, and more wedge-like than branches. They fan into the ground. Do not attach ten long equal-length tentacles to every plant. Small plants can use a tiny detachable root plug or no visible root at all; they do not need a wooden tree stump under each leaf rosette.

### 6.4 Leaf cluster and tree canopy mass

A leaf cluster is an intentional assembly of broad overlapping lobes. It is not a smooth sphere with flat shading enabled.

For a close-to-mid-distance shrub:

1. Build a small hidden fork or short stem.
2. Place three large leaves pointing outward/upward, with unequal lengths.
3. Add one shorter rear leaf if needed to prevent an empty back view.
4. Rotate and scale the completed module as a unit when assembling the shrub.
5. Preserve a few visible leaf tips and overlaps on the outside silhouette.

For a larger tree canopy:

1. Block out 3–6 flattened, irregular convex foliage masses, each with several broad planes.
2. Make each mass wider than thick, with one or two deliberate protruding lobes.
3. Place the masses on branch tips with overlap at the center and readable separations around the perimeter.
4. Add a small number of large wedge-like leaf lobes only where they improve the outer contour.
5. Inspect without color. If it reads as a pile of equal balls, flatten, offset, and reshape the masses before adding anything else.

An icosphere may be a temporary blockout volume. Do not treat a collection of identical untouched icospheres as a finished hero canopy. Keep the underside quieter and darker; spend silhouette geometry on the visible outer edge.

### 6.5 Conifer tier

Build a shallow skirt from a 6–10-sided upper ring to an irregular lower outline. The lower outline has a handful of broad downward leaf points. Alternate long and short lobes intentionally. The skirt has thickness or a closed underside.

Stack 3–5 tiers around a tapered trunk. Upper tiers shrink; lower tiers spread. Offset tier rotations and heights slightly. Keep the top a short integrated crown, not a long needle. Make one tier module first, inspect it, and then duplicate it with proportion changes.

Avoid a perfectly smooth cone, a stack of identical flat discs, and a narrow starburst with razor-thin points. These fail different parts of the reference style even if all are technically low poly.

### 6.6 Petal, bloom, and trumpet flower

Petals are broad rounded or pointed wedges with a shallow cup. Use 5–8 large petals for ordinary blooms. Keep the center simple and large enough to read at a distance. Slightly overlap petals at the base; do not leave a visible ring of disconnected pieces around the center.

Build a trumpet or hood flower from a 5–8-sided tube that widens toward its mouth. Give the mouth a short rim and an inner wall or inset cup. A dark painted circle is not a physical opening. Keep the throat shallow enough to inspect and model. Build the bloom, stem, and leaf modules separately.

### 6.7 Fruit, seedpod, nut, and resin

- Berry: a small low-resolution rounded volume, not an extremely sharp diamond. A bunch can be 3–7 overlapping large berries rather than 40 tiny spheres.
- Nut: a squat pointed oval with a separate cup/husk if the concept shows one.
- Seedpod: a larger readable shape with an optional seam between two or three shell parts.
- Resin: a broad amber angular nodule that appears attached to or emerging from wood. Give it a contact surface; do not suspend it in front of a tree.
- Heartpod: intentionally heart-shaped red volume with a broad top notch and pointed base, cradled by separate coarse husk halves. Do not replace it with a generic sphere.

If a resource should disappear when harvested, isolate the harvestable part. A depleted state should remove that part, not shrink or randomly deform the whole plant.

### 6.8 Mushroom and shelf fungus

Create the cap as a low-resolution lathed or ring-based form: a small top ring, wide shoulder ring, lower rim, and shallow underside inset. Use 6–10 radial sectors. The stalk is a short tapered polygon tube.

The cap needs an underside. Do not hide an empty open bowl above the stalk. Use a simple underside disc or a few large radial planes; realistic fine gills are unnecessary. Give the stalk a broad enough connection to appear load-bearing.

A shelf fungus is a flattened half-disc or fan attached along its back edge. Stack a few uneven shelves on a trunk. Keep the attachment face and cap separate in authoring so the support can be changed.

### 6.9 Fern and unfurling coil

A fern's main frond is a curved spine carrying a small number of broad paired lobes. Five paired lobe groups are often enough. Shape the whole frond before adding the side lobes. Do not generate a dense botanical fern with hundreds of leaflets.

An unfurling coil is a thick planar spiral, approximately one to one-and-a-half turns, with a tapered radius and a short upright stem. Keep a clear hole at its center. Use a low-sided swept tube or joined tapered segments; inspect from the side to ensure the spiral is not paper-thin. Add only a few broad fan leaves around the base for the giant variant.

## 7. Reference Python helpers for MCP execution

This section is a **small geometry scaffold**, not a finished asset generator. It demonstrates closed leaf geometry, tapered branch construction, scoped scene ownership, shared materials, a root pivot, and an inspection report. Its rosette is a calibration prototype; tune the specification and inspect screenshots before using it as production art. In this repository, port accepted geometry into the existing `flintkit.Asset` sheet pipeline, using its palette and `Tint` attribute, and finish one production mesh per static asset. Do not ship the example's separate `FB_GUIDE_` materials or multi-object calibration collection as production library assets.

The code targets the stable data-model approach used by Blender's Python API. Probe the connected version rather than assuming a renderer, exporter operator, node layout, or deprecated property exists. The code has been syntax-checked and its pure geometry checked outside Blender for closed surfaces and consistent winding; it has not been executed in a connected Blender session as part of writing this document.

```python
import bpy
import math
from mathutils import Vector

OWNER = "Flintborn_WorldModeling_Guide"

def srgb_channel_to_linear(value):
    return value / 12.92 if value <= 0.04045 else ((value + 0.055) / 1.055) ** 2.4

def linear_rgba(hex_color):
    code = hex_color.lstrip("#")
    if len(code) != 6:
        raise ValueError("Expected a six-digit sRGB hex color")
    return tuple(srgb_channel_to_linear(int(code[i:i + 2], 16) / 255.0)
                 for i in (0, 2, 4)) + (1.0,)

def shared_material(name, hex_color):
    full_name = "FB_GUIDE_" + name
    material = bpy.data.materials.get(full_name)
    if material is None:
        material = bpy.data.materials.new(full_name)
        material["fb_owner"] = OWNER
    elif material.get("fb_owner") != OWNER:
        raise RuntimeError("Refusing to overwrite an unowned material: " + full_name)
    # Older versions may require use_nodes; newer versions may already have a tree.
    if material.node_tree is None:
        if not hasattr(material, "use_nodes"):
            raise RuntimeError("Inspect this Blender version's material API")
        material.use_nodes = True
    tree = material.node_tree
    if tree is None:
        raise RuntimeError("No shader node tree available")
    rgba = linear_rgba(hex_color)
    material.diffuse_color = rgba
    shader = next((n for n in tree.nodes if n.type == "BSDF_PRINCIPLED"), None)
    output = next((n for n in tree.nodes if n.type == "OUTPUT_MATERIAL"), None)
    if shader is None:
        shader = tree.nodes.new("ShaderNodeBsdfPrincipled")
    if output is None:
        output = tree.nodes.new("ShaderNodeOutputMaterial")
    if (shader.inputs.get("Base Color") is None or
            shader.inputs.get("Roughness") is None):
        raise RuntimeError("Inspect Principled BSDF input names for this version")
    shader.inputs["Base Color"].default_value = rgba
    shader.inputs["Roughness"].default_value = 0.86
    metallic = shader.inputs.get("Metallic")
    if metallic is not None:
        metallic.default_value = 0.0
    surface = output.inputs.get("Surface")
    bsdf = shader.outputs.get("BSDF")
    if surface is None or bsdf is None:
        raise RuntimeError("Missing shader surface sockets")
    for link in list(surface.links):
        tree.links.remove(link)
    tree.links.new(bsdf, surface)
    return material

def owned_collection(name):
    collection = bpy.data.collections.get(name)
    if collection is None:
        collection = bpy.data.collections.new(name)
        collection["fb_owner"] = OWNER
        bpy.context.scene.collection.children.link(collection)
    elif collection.get("fb_owner") != OWNER:
        raise RuntimeError("Refusing to modify an unowned collection: " + name)
    elif collection.children:
        raise RuntimeError("Inspect child collections before regenerating")
    # This example owns only its named collection and direct generated objects.
    if any(obj.get("fb_owner") != OWNER for obj in collection.objects):
        raise RuntimeError("Unowned object found; inspect before replacing")
    for obj in list(collection.objects):
        if len(obj.users_collection) > 1:
            raise RuntimeError("Shared object found; inspect before replacing")
    old_meshes = {obj.data for obj in collection.objects if obj.type == "MESH"}
    for obj in list(collection.objects):
        bpy.data.objects.remove(obj, do_unlink=True)
    for mesh in old_meshes:
        if mesh.users == 0:
            bpy.data.meshes.remove(mesh)
    return collection

def mesh_object(name, vertices, faces, collection, material, parent):
    mesh = bpy.data.meshes.new(name + "_Mesh")
    mesh.from_pydata(vertices, [], faces)
    mesh.update()
    for polygon in mesh.polygons:
        polygon.use_smooth = False
    obj = bpy.data.objects.new(name, mesh)
    collection.objects.link(obj)
    obj["fb_owner"] = OWNER
    obj.parent = parent
    mesh.materials.append(material)
    return obj

def leaf_geometry(length=1.0, width=0.4, camber=0.06,
                  back_thickness=0.025, bend=0.08):
    if min(length, width, camber, back_thickness) <= 0:
        raise ValueError("Leaf dimensions and ridge depths must be positive")
    # Local +Z is base-to-tip. Local -Y is the front surface.
    # The six-point outline is shared by front and back triangle fans.
    vertices = [
        (0.0, 0.0, 0.0),
        (-0.42 * width, 0.0, 0.28 * length),
        (-0.50 * width, 0.0, 0.58 * length),
        (0.0, 0.0, length),
        (0.50 * width, 0.0, 0.58 * length),
        (0.42 * width, 0.0, 0.28 * length),
        (0.0, -camber, 0.52 * length),
        (0.0, back_thickness, 0.52 * length),
    ]
    vertices = [(x + bend * (z / length) ** 2, y, z)
                for x, y, z in vertices]
    faces = []
    for i in range(6):
        j = (i + 1) % 6
        faces.append((6, j, i))  # front, outward toward local -Y
        faces.append((7, i, j))  # back, outward toward local +Y
    return vertices, faces

def frustum_geometry(length, radius_start, radius_end, sides=6):
    if length <= 0 or min(radius_start, radius_end) <= 0 or sides < 3:
        raise ValueError("Invalid tapered segment parameters")
    vertices = []
    for z, radius in ((0.0, radius_start), (length, radius_end)):
        vertices.extend((radius * math.cos(2 * math.pi * i / sides),
                         radius * math.sin(2 * math.pi * i / sides), z)
                        for i in range(sides))
    faces = [tuple(reversed(range(sides))), tuple(range(sides, 2 * sides))]
    for i in range(sides):
        j = (i + 1) % sides
        faces.append((i, j, sides + j, sides + i))
    return vertices, faces

def tapered_segment(name, start, end, radius_start, radius_end,
                    collection, material, parent, sides=6):
    start, end = Vector(start), Vector(end)
    direction = end - start
    if direction.length <= 1e-8:
        raise ValueError("Segment start and end coincide")
    vertices, faces = frustum_geometry(direction.length, radius_start,
                                      radius_end, sides)
    obj = mesh_object(name, vertices, faces, collection, material, parent)
    obj.location = start
    obj.rotation_mode = "QUATERNION"
    obj.rotation_quaternion = direction.to_track_quat("Z", "Y")
    return obj

def build_calibration_rosette():
    collection = owned_collection("FB_GUIDE_Rosette_A")
    root = bpy.data.objects.new("FB_GUIDE_Rosette_A_ROOT", None)
    collection.objects.link(root)
    root["fb_owner"] = OWNER
    root["asset_id"] = "FB_GUIDE_Rosette_A"
    root["status"] = "calibration prototype — inspect before production"
    root.location = (0.0, 0.0, 0.0)
    leaf_mid = shared_material("LeafMid", "#69A53D")
    leaf_light = shared_material("LeafLight", "#A0C94C")
    bark = shared_material("BarkMid", "#916039")
    tapered_segment("FB_GUIDE_Rosette_A_Stem", (0, 0, 0), (0, 0, 0.26),
                    0.06, 0.04, collection, bark, root)
    # Purposeful variation, not random noise. Dimensions are asset units.
    lengths = (0.86, 0.72, 0.92, 0.78, 0.82)
    pitches = (57, 66, 52, 63, 58)  # degrees from vertical
    for index, (length, pitch) in enumerate(zip(lengths, pitches)):
        phi = math.radians(index * 72.0 + (3.0 if index % 2 else -3.0))
        theta = math.radians(pitch)
        direction = Vector((math.cos(phi) * math.sin(theta),
                            math.sin(phi) * math.sin(theta), math.cos(theta)))
        vertices, faces = leaf_geometry(length, length * 0.43,
                                       length * 0.06, length * 0.025,
                                       length * 0.08)
        obj = mesh_object("FB_GUIDE_Rosette_A_Leaf_%02d" % (index + 1),
                          vertices, faces, collection,
                          leaf_light if index == 1 else leaf_mid, root)
        obj.location = (0.025 * math.cos(phi), 0.025 * math.sin(phi), 0.16)
        obj.rotation_mode = "QUATERNION"
        obj.rotation_quaternion = direction.to_track_quat("Z", "Y")
    bpy.context.view_layer.update()
    triangles = 0
    for obj in collection.objects:
        if obj.type == "MESH":
            obj.data.calc_loop_triangles()
            triangles += len(obj.data.loop_triangles)
    points = [obj.matrix_world @ Vector(corner)
              for obj in collection.objects if obj.type == "MESH"
              for corner in obj.bound_box]
    minimum = tuple(min(p[axis] for p in points) for axis in range(3))
    maximum = tuple(max(p[axis] for p in points) for axis in range(3))
    return {"asset": root["asset_id"], "objects": len(collection.objects),
            "triangles_unmodified": triangles, "bounds_min": minimum,
            "bounds_max": maximum, "next": "capture front/side/top/three-quarter"}

print(build_calibration_rosette())
```

Do not silently run this example on an existing asset collection with the same name. The ownership guards intentionally fail rather than deleting someone else's work. This code also does not set cameras, save files, run exporters, build collision, or validate appearance. Those are separate operations with their own checks.

When extending the helper, keep leaf definition in local coordinates and assemble using transforms. Do not hand-edit every copy's vertices unless it represents an intentionally different module. For fully independent edited variants, copy the mesh datablock before modifying vertices; linked duplicates share edits.

## 8. Assembly recipes: common plants and ground vegetation

The recipes below are intended to be followed, rendered, and adjusted. Counts describe a starting model, not mandatory exact counts in every variant. Use `H` for the selected overall height and `W` for selected overall width.

### 8.1 Meadow families — sheet V01

| Family | Geometry and assembly recipe | Identity and variants |
| --- | --- | --- |
| Clover patch | Build one thin but solid stem with a three-leaf head. Each leaflet is broad and heart-like; use a shallow base notch, not a needle point. Arrange 5–7 stems in an uneven low oval patch; flower stalks can rise slightly above the leaves. | One sprig, wider patch, white flowering patch. Keep the three-leaf grouping visible; do not turn it into generic round bush clumps. |
| Field sedge | Use 5–6 stiff broad folded blades sharing a narrow root, tallest blade at the rear. Add 1–2 simple brown seed spikes on thicker stalks. Overall width approximately 0.8–1.3 H. | Short fan, tall arching fan, cut tuft. Seed spikes are detachable; the depleted tuft retains its rooted blade bases. |
| Bluegrass clump | Make 5 arching blades in cooler green, with 2–3 tan seedheads. Bend outer blades away from the center; keep the middle open enough to see stalks. Model seedheads as 3–5 large overlapping lobes, not a detailed wheat mesh. | Compact, wide, dry late-growth version. Drying changes whole blades or heads, not random tiny triangles. |
| Dandelion rosette | Arrange 5–7 broad toothed leaves low to the ground. Place one thick central stalk with a broad yellow flower and an optional short bud. The flower is a ring of large petals around a simple center. | Yellow bloom, coarse white seed puff, clipped rosette. A seed puff is 5–9 large pale lobes, not hundreds of transparent hairs. |

### 8.2 Forage bushes — sheet V02

Start with the visible cane skeleton. Build no more foliage than needed to explain the crown. In a typical view, expose roughly the lower quarter to third of the stems and preserve at least two visible gaps through an ordinary shrub's crown. These are visual targets, not pixel-accurate measurements.

| Family | Geometry and assembly recipe | Identity and variants |
| --- | --- | --- |
| Raspberry bush | Make three rising canes, two short forks, and 4–6 three-leaf clusters. Attach about five detachable red berry bunches at outer branch nodes; a bunch contains a few coarse lobes. Keep berries in front of or beneath some leaves, not completely hidden. | Young, full/fruiting, fruitless harvested. Do not give every cane the same height and angle. |
| Elderberry shrub | Use a broad low fork with dark green leaf groups arranged outward. Place three blue-black berry bunches in shallow pendant groups. The crown should be wider and less upright than raspberry. | Young, wide mature, fruitless. Distinguish by branch spread and fruit grouping, not blue recolor alone. |
| Hazel shrub | Build 3 upright stems, a compact yellow-green crown, and about three large tan nuts inside coarse green/brown cup husks. Each husk is 3–4 broad lobes around one nut. | Sapling, full/fruiting, harvested. Nut and husk are separate removable meshes. |
| Rosehip scrub | Use a low sprawling branch network with only a few branch forks. Add a few broad olive leaves, 4–6 large triangular thorns, and 3–5 orange oval hips. | Compact, spreading, bare winter. Do not fill the interior with thin tangled branches. |

### 8.3 Ferns and climbers — sheet V03

| Family | Geometry and assembly recipe | Identity and variants |
| --- | --- | --- |
| Bracken fern | Start with three arching frond spines. Add five broad paired lobe groups per mature frond, tapering toward the tip. Shape a triangular frond outline; use connected thick geometry or a clean solid lobe assembly. | Juvenile curls, full fern, wide spread. Fix the large frond arc before adjusting individual lobes. |
| Strap fern | Assemble five undivided strap leaves in a low uneven rosette. Leaves are wider and blunter than grass and bend once through their upper half. | Upright, low profile, older brown-tipped. Brown tips are an intentional region, not noise. |
| Heartleaf creeper | Build one straight vine segment, one elbow, and one fork. Add broad paired heart leaves at 3–5 nodes. Give the attachment side a small hidden contact surface. | Ground trail, wall climb, hanging loop. Reuse the same leaf modules while changing the path. |
| Trumpet vine | Use one short woody fork and 3–4 broad leaves. Build one or two cream-yellow trumpets from a flared tube and separate petal rim; show the hollow throat. | Small vine, flowering drape, cut/flowerless. Keep the flowers larger than tiny decorative background blooms. |

### 8.4 Riverbank and aquatic plants — sheet V04

| Family | Geometry and assembly recipe | Identity and variants |
| --- | --- | --- |
| Cattail clump | Use three upright thick green stems with tan capsules and five folded leaves. Seedheads sit on coherent stalks; do not attach capsules directly to blade tips. | Short/compact, tall/dense, seedless leafy. Retain clear gaps among stalks. |
| Bulrush fan | Make four thick upright or elbow-bent green stalks, two brown seed clusters, and a few simpler long blades. Give the fan a wider spread than cattail. | Low, splayed, clipped. A seed cluster is a handful of large lobes. |
| Water lily | Make 1–3 thick notched pads with flat upper surfaces, darker closed undersides, and stems extending down to a common depth reference. Assemble one white-yellow bloom or closed bud. | Single pad, flowering group, closed bud. The pad must remain a shallow disc; avoid mushroom-like tall stalks in above-water composition. |
| Pondweed | Make three curved thick stems with broad paired leaves at 2–4 levels. Use olive greens and relatively sparse branching. | Upright, arched/flowing, sparse. The root can be a detachable buried plug. |

Author these without a large water base. Record the intended waterline separately so the asset can be placed in different river depths. Do not automatically make submerged leaves transparent. Avoid hardcoded water physics or harvesting behavior in an art asset.

### 8.5 Fungi and cave growth — sheet V05

| Family | Geometry and assembly recipe | Identity and variants |
| --- | --- | --- |
| Chestnut mushroom | Use 1–3 broad brown caps on short cream stalks. Make the largest cap broad and gently domed, with an inset underside and quiet rim. | Button stage, open cap, harvested stalk. Caps detach without deforming stalk bases. |
| Amber shelf fungus | Build a thick ochre half-disc with a lighter lower rim and flat rear attachment. Stack 1–3 shelves at different heights on an optional support. | Single shelf, tiered stack, old dark bracket. Support wood is optional and separate. |
| Puffball | Use a squat pale faceted bulb with a small base. Mature forms have a coarse polygon mouth and dark inset plug, not a painted black dot. | Young closed, mature open, small group. Preserve the round squat silhouette; do not sharpen into a crystal. |
| Cave trumpet fungus | Build a broad muted-purple funnel with a flared rim and a thick tapering pale stalk. The opening is real geometry with a shallow interior. | Short/wide, taller funnel, pale young. No realistic gills, spore clouds, or emissive mist. |

## 9. Assembly recipes: trees, hardy plants, and uncommon forage

### 9.1 Additional trees — sheet V06

For every tree, block out the trunk and branch silhouette before adding foliage. Inspect the bare skeleton once. Then add canopy modules and inspect again. A canopy cannot repair a trunk that has no believable load-bearing structure.

| Family | Geometry and assembly recipe | Identity and variants |
| --- | --- | --- |
| Birch | Make a slim pale trunk with one or two forks. Add only a few large dark bark patches as material regions or shallow patches; use 3–4 lime canopy clumps. Keep much of the trunk visible. | Sapling, tall single, twin trunk. Avoid covering the pale bark with a dense green sphere. |
| Willow | Make a low thick trunk and 3 spreading branches. Hang roughly five broad leaf-strip clusters from the outer branch ends, each a group of solid downward leaves. | Young, wide, leaning. Avoid hundreds of thin dangling strings; preserve openings beneath the umbrella crown. |
| Rowan | Use a medium warm forked trunk, 3–5 airy green clumps, and about three orange-red berry bunches attached near outer nodes. | Young, fruiting, fruitless. Its upright airy structure should differ from the wide elderberry bush. |
| Juniper | Make a low gnarled multi-stem skeleton with four irregular jagged blue-green foliage groups. Add only a few large blue berry modules. | Ground shrub, upright, gnarled. Foliage lobes are short and thick, not an all-direction starburst of long spikes. |

### 9.2 Hardy and alpine plants — sheet V07

| Family | Geometry and assembly recipe | Identity and variants |
| --- | --- | --- |
| Heather | Build 2–3 low woody forks, 4–5 compact green tufts, and about six coarse mauve bell flowers. Each bell is a short flared hollow volume, not a tiny sphere. | Low mat, upright, flowerless. Keep flower groups countable and leaf tufts broad. |
| Alpine cushion | Assemble 4–6 low rosette modules into a compact pad with 2–3 white flowers. Reduce root visibility; this hugs the ground. | Small, wide, snow-capped. Snow is a separate thick cover over selected upper surfaces. |
| Dry tussock | Use 5–7 broad curled tan/green blades and 2–3 thick seed stalks. Curve outer blades down to broaden the lower silhouette. | Short, tall, half-dry. The silhouette should differ from upright sedge. |
| Thorn scrub | Use three thick angular gray-brown branches with sparse olive leaf modules and 4–6 large triangular thorns. | Low sprawl, restrained tangled form, young green. Stop before the silhouette becomes an unreadable wire nest. |

### 9.3 Uncommon harvestables — sheet V08

| Family | Geometry and assembly recipe | Identity and variants |
| --- | --- | --- |
| Flax patch | Use three stems with broad simplified leaves, 1–3 blue five-petal blooms, and 1–3 coarse tan seed capsules. Keep stems slightly staggered in height. | Young, flowering, seeded. Capsules and blooms are separate modules. |
| Silkleaf | Arrange five broad sage-colored spoon leaves around a low center, with one cream seed tuft. Model the tuft as a few big folded lobes. | Young, mature tuft, trimmed. Do not add fine cotton fibers or fur. |
| Redroot | Make a thick reddish forked root with 3 major branches, a broad green rosette, and two cream buds. Expose enough of the tuber to identify it. | Juvenile buried, mature exposed, harvested bare root. Root and foliage remain separable. |
| Sunpod shrub | Use an open woody fork, 3–5 leaf groups, and three golden pods enclosed in four-point coarse husks. | Closed pod, open husk, harvested. Show a real cavity or cradle in the open husk. |

## 10. Assembly recipes: rare event flora

These are proposed art concepts. Rarity names, rewards, gameplay functions, spawn timing, and harvesting requirements remain separate design decisions. The guide does not approve every illustrated plant for the game.

### 10.1 Rare flowers and shrubs — sheet V09

| Family | Geometry and assembly recipe | Identity and variants |
| --- | --- | --- |
| Sunburst Bloom | Build six broad wedge petals in one shallow radial cup around a large amber seed center. Add a low olive rosette and a short supporting stalk. Petals must connect visually under the center. | Closed bud, full bloom, seed removed. Removing the seed leaves a visible central cup rather than a floating petal ring. |
| Moonveil Orchid | Build two silver-green arching leaves and one thick curved stalk. Add a large purple outer hood with a separate pale-turquoise inner bell. Model the lower opening and attachment. | Single bloom, double bloom, empty stalk. A heavy hood needs a visibly sufficient stalk; avoid a paper-thin dangling skin. |
| Stormreed | Build three short segmented zigzag stalks, broad teal blades, and violet seedheads. Restrict bends to 2–3 purposeful elbows per stalk. | Short, tall, trimmed. Its angular rhythm distinguishes it; no lightning effects are needed. |
| Heartpod Bramble | Use a low forked brown skeleton, dark teal leaves, and three red heartpods in separate two-piece thorn husks. Keep the red core visually distinct from tan/brown shells. | Sealed, open, harvested. Show pod contact and husk interiors; do not add excessive thorns. |

### 10.2 Rare trees and ancient growth — sheet V10

| Family | Geometry and assembly recipe | Identity and variants |
| --- | --- | --- |
| Goldencrown tree | Build a squat twisted trunk with 3 substantial branches and 3–4 broad golden crown clumps. Add warm-green underside groups and one coarse seed-cone module if needed. | Young, ancient fork, hollow giant. Make the fork and crown silhouette special; gold color alone is insufficient. |
| Silverbark tree | Use a pale split trunk, 3 blue-green canopy groups, and two or three hanging pearl-like pods. Build each pod as a pale outer shell with an optional warm inner insert. | Upright, leaning, harvested pods. Removing pods need not remove the canopy; the concept's bare version is an optional separate state. |
| Resinheart stump | Build an open low stump with a broad root arch around an amber nodule. Separate left/right roots, hollow trunk shell, resin, and two leaf clusters. | Sealed resin, exposed resin, harvested hollow. The opening must be physically hollow; do not paint the resin on an unbroken trunk. |
| Giant coil fern | Build a thick upright tapered spiral above a short root pedestal, with two broad fan leaves. Keep its center hole and side thickness clear. | Tight coil, half-unfurled, full fan. This is a plant, not a creature: no eyes, arms, joints, or walking legs. |

### 10.3 How common and rare should differ

Use at most two strong identity changes per rare family at first: for example, a hood-shaped bloom plus cooler leaf color, or a hollow root chamber plus amber resin. Keep the same construction vocabulary, material roughness, and facet scale as common plants.

Rare silhouettes may be larger or more unusual, but should not automatically use 10 times the geometry. Make a rare plant recognizable in a flat silhouette test and at a small thumbnail size before spending polygons on inner details.

## 11. Existing vegetation families from the wider world sheets

The V01–V10 sheets expand, rather than replace, these earlier families:

| Existing family | Build instructions |
| --- | --- |
| Pine / young fir / sapling / old pine | Use the conifer-tier recipe. Separate trunk, lower skirts, middle tiers, crown, and root foot. Vary tier count, crown width, lean, and trunk exposure; do not merely recolor one mesh. |
| Oak / ancient broadleaf | Use 3–6 canopy masses on a visible branching skeleton. Give ancient forms broader root buttresses and a deliberate fork or hollow, not uniformly scaled-up foliage. |
| Berry bush / healing herb / fiber shrub / thorn shrub | Use open shrub, rosette, and fan recipes. Berries, buds, fiber tufts, and thorns are modules. The name “healing herb” is an art label here; no medical or gameplay effect is implied. |
| Moss / wall ivy / hanging vines | Create shallow attachable overlays with a quiet back surface. Make straight, corner, fork, and draped modules that fit to walls and rocks. Avoid merging the supporting wall into every ivy model. |
| Dead trees / logs / stumps / exposed roots | Build fewer, thicker branches; show cut faces with 1–2 broad rings or color bands. A hollow log needs an inner surface and a real opening. |
| Giant red mushrooms / bracket fungi | Use the cap/stalk/underside recipe. White cap spots are a few broad material regions or shallow mesh inserts, not dozens of raised pebbles. |
| Cave moss / cave mushrooms | Use subdued greens and warm neutral stalks. Their visibility should come from shape and placed lighting, not automatic emission. |
| Emberbloom / Frost Shrub / Mooncap / Ancient Root | Keep event inserts separate: seed/core, snow/ice nodules, cap spots, or mineral nodule. Reuse the common plant grammar. Effects, if later requested, must not conceal the geometry during approval. |

## 12. Supporting world assets: terrain, rocks, and resources

Vegetation only fits the world when neighboring assets use the same scale and facet language. Apply these construction recipes when an LLM is building a full zone.

### 12.1 Boulder and rock scatter

Start with an intentionally uneven 5–8-sided footprint and 2–3 height rings. Offset ring centers slightly; vary radius by broad sectors. Use a few large faces for the upright sides and a quieter top. Flatten the bottom for placement. Avoid subdivision followed by random displacement.

For a squat boulder, keep height around 0.5–0.9 of width. For an upright spire, narrow the upper ring and lean the centerline. For a split rock, make two complementary masses with a deliberate gap. Use separate moss caps or ivy overlays. Build 3–5 reusable pebbles and arrange sparse patches; do not scatter hundreds into each base mesh.

### 12.2 Cliffs, ledges, and ramps

Build a terrain chunk with a flat rear/connector region, broad faceted front buttresses, a walkable top, and a separate grass lip. The front can be irregular while the connection area remains consistent. Make straight, inner-corner, outer-corner, and end-cap modules.

Build ramps as genuinely walkable continuous slopes with broad side walls. Do not make them decorative stair-like rock piles that block traversal. Split terraced ledges into an upper cap, lower shelf, and corner filler. Do not assume the illustrations determine exact gameplay slope or character clearance; test against the target controller when available.

### 12.3 Rivers and waterfalls

Separate land, bank slope, sand strip, water surface, waterfall curtain, and foam. Water is a simple surface/volume asset or a target-engine water solution, not a requirement to simulate fluid in Blender. A waterfall can use a broad gently folded curtain with 2–4 large flow bands. Foam should be a few broad strips or rings rather than dense realistic particles.

The foam must not z-fight with the water surface. Record waterline and flow direction. Keep riverbed stones separate for reuse and for controlling traversal. A rendered water shader is a preview choice, not evidence that an exported Roblox material will match it automatically.

### 12.4 Ore nodes and ordinary minerals

Build a host boulder first. Add 2–4 large separate mineral inserts that intersect it enough to look embedded. Leave substantial host rock visible. Inserts need clear shapes and broad facets; they should not form an all-over spiky crust.

- Stone: simple warm-gray boulder and a few independent chunks.
- Flint: pale host rock with a few broad charcoal wedge inserts; drops are coarse flakes.
- Coal: 3–4 low dark lobes with muted facet variation; avoid mirror-black polish.
- Copper: rusty orange inserts with a restrained turquoise edge accent.
- Iron: silver-gray coarse plates/nuggets with limited ochre weathering.
- Gold: broad warm yellow nuggets on a squat host; do not add dense glitter.
- Sulfur: chunky yellow mineral blocks on a broad stepped slab.
- Obsidian: 2–3 broad dark wedges; sharp enough to read as volcanic glass, but not a forest of tiny needles.

The depleted state usually retains the host or base and removes the harvestable inserts. Build loose drops separately. Do not invent mining hardness, rarity odds, or yield values while modeling.

### 12.5 Crystals, geodes, amber, and meteors

Crystals use a 5–7-sided shaft with a short broad faceted tip. Build one large and 1–2 shorter crystals with varied lean. Their side facets should be longer and quieter than the host rock's facets. A crystal is not simply an elongated noisy boulder.

For a geode, build separate outer shell halves with visible inner surfaces and attach a few large crystals inside. For amber, place a warm nodule inside a split wood base; make shell/wood and nodule independent.

For meteors, use a broad heavy outer mass with a few intentional fractures and an interior/core insert where appropriate. Separate shell pieces, core, and low impact rim. Use orange/cyan accents sparingly. No smoke or bloom should be needed to understand the modeled form. Stormglass uses short thick branching tube forms embedded in a sand base, not electrical particle strands.

## 13. Supporting world assets: structures and small props

### 13.1 Timber vocabulary

Use squared or low-sided timbers with lightly irregular outlines and restrained bevels. A main upright must read as stronger than a rail or peg. Bevel width should be a small fraction of beam width, often around 0.02–0.05, with one segment as a starting point. Do not put heavy rounded bevels on every plank or dense chisel detail into every surface.

Define reusable plank, post, crossbeam, diagonal brace, rope binding, collar, and peg modules. Show joints and overlaps. Structural beams should meet or overlap at believable points; do not leave decorative braces floating near posts.

### 13.2 Bridges, docks, boardwalks, and fences

Build load-bearing components first: piles/posts, longitudinal beams, crossbeams, deck planks, then rails and rope. Inspect from underneath. A bridge should not be a hovering plank carpet with ropes added afterward.

Create a short bay, straight span, corner/landing, ramp end, and damaged version. Keep route width consistent within one kit. Rope rails are thick low-resolution curves/tubes with restrained sag. Do not model individual rope fibers. Fences use two posts, one or two rough rails, and a small number of lashings. Broken variants remove or displace specific components coherently.

### 13.3 Canvas, camps, huts, and workshops

Canvas is a low-resolution cloth surface with a broad ridge and gentle sag. A rectangular awning can start with a 3-by-3 or 5-by-3 vertex grid, then receive a few purposeful height adjustments and thin thickness. Avoid high-resolution cloth simulation as the default authoring method.

Place support posts and ties where the cloth actually attaches. Build an A-frame from its two ends and ridgepole before fitting the canvas. Huts use a floor, corner posts, wall panels, doorframe, and roof panels. Roofs should lift off in the authoring model so the interior can be inspected. Do not model the outside as a solid cube with a doorway painted onto it.

### 13.4 Timberwatch fortifications

- Palisade: repeat a few log shapes with controlled height differences, add rear horizontal rails, and keep a consistent wall thickness.
- Gate: separate frame, two door leaves, hinge/pin pieces, latch bar, and optional handles/banner. Doors must occupy a coherent hinge plane.
- Wall walk: deck, rear supports, braces, rail, and a connecting stair or ladder.
- Watchtower: four load-bearing corner posts, repeated brace bays, upper deck, railing, ladder, cream roof, and separate red banner.
- Lodge/workshop: use the same post/beam/plank dimensions as the fort kit, with floor and roof removable for inspection.

Do not scale every component uniformly when making a taller tower. Add or lengthen a structural bay while preserving plausible beam and plank thicknesses.

### 13.5 Ruins, arches, columns, and the keep

Use broad pale stone blocks with simple joints and restrained wear. Build an arch from two piers, wedge stones, and a keystone around a genuinely open hole. Avoid relying on a Boolean to produce the entire arch if explicit wedge construction is clearer and more predictable.

Columns are stacked low-sided shaft sections over a broader base, with optional broken caps. Ruined variants remove selected stones and expose coarse break surfaces. Do not randomly jitter every block. Ivy is a separate overlay and must not conceal the whole masonry kit.

The lake tower needs a hollow interior, doorway, wall-ring segments, and broken crown. The keep gateway needs independently editable piers, arch pieces, broken columns, stairs, floor bays, and decoration. Keep courtyard traversal open; the reference's scenic density is not permission to fill a combat arena with colliders.

### 13.6 Mosswick stump hall

Start with the passage opening and playable interior volume. Surround it with a hollow trunk shell and two broad root pillars. Add the cut-top rim and a floor. Model enough inner surface to read correctly through the entrance. Then attach ivy, mushrooms, lanterns, canvas, and small props as separate pieces. A giant solid stump with a dark doorway decal is not sufficient.

### 13.7 Mine interior and equipment

Create support portals, scaffold bays, wall-mounted catwalks, stair/ladder modules, and rail pieces independently. Catwalks need a visible cantilever or post support. Rails use two continuous tracks over broad ties; curved sections maintain their gauge. A minecart has a separate box, wheels, axles, and optional load. A rope lift uses posts, a crossbeam, pulley, thick rope, and cargo platform; ensure their visual connection is continuous.

### 13.8 Props, boats, lighting, and event dressing

- Crate: panel box, corner posts, coarse diagonal braces, optional lid. Avoid modeling each wood fiber.
- Barrel: 8–12-sided body with broad stave suggestion, a few hoops, and lid; do not produce a perfect smooth cylinder if the silhouette is visible.
- Table/bench: top planks, trestles or legs, crossbar, and visibly joined seat supports.
- Pottery: 6–10-sided profiles with a real rim and shallow interior where visible.
- Bed mat/sack: broad folded or rolled volumes with a few purposeful creases.
- Lantern: frame, roof, bottom, handle/loop, and inset window panels; preview light is separate from export geometry.
- Fire/brazier: fuel and bowl/ring are solid parts; flame is a separate simple preview mesh or later target-engine effect.
- Rowboat: keel, low-resolution ribs, hull sides with closed thickness, benches, and separate oars. Inspect the underside and gunwale.
- Raft: a few thick logs, crossbeams, lashings, and optional plank deck.
- Chest/cache: box, lid, hinge region, broad bands, and latch. Open and closed are coherent states, not unrelated chest designs.
- Banner: simple low-resolution cloth with one readable white diamond emblem. Keep it separate from its post and ties.

## 14. Variations without losing the family

Use controlled parameter sets rather than unrestricted randomness.

| Parameter | Useful initial variation | Guardrail |
| --- | --- | --- |
| Overall height | About ±10–20% within ordinary sibling variants | Keep species recognizable and scale-consistent |
| Crown width | About ±10–25% | Do not hide every branch or turn sparse species into a ball |
| Lean | Roughly 0–12 degrees for ordinary forms | Keep roots and center of mass visually plausible |
| Leaf length | About ±10–15% within one module family | Preserve the leaf's width/length relationship |
| Branch rotation | Small offsets to selected forks | No branches entering empty space with no attachment |
| Fruit count | A few discrete states | Harvested means intentional removal, not random disappearance |
| Color | Slight coordinated material changes | Do not randomize every polygon's hue |
| Damage | Remove/break specific components | Do not apply global noise or decimate until unrecognizable |

Suggested first variants: young, representative mature, wide/sparse or harvested. For a tree, use sapling, mature, and leaning/forked. For a flower, use bud, bloom, and harvested. For structures, use intact, alternate layout, and damaged.

Generate variation specs before generating geometry. Record seed and variant name. Compare siblings in one screenshot at the same scale and lighting. If they look identical at thumbnail size, change structure rather than adding small decorations.

## 15. Biome placement and visual ecology

This is an art placement guide, not an approved spawn table. Keep common ground vegetation subordinate to traversal, resource readability, and PvP sightlines.

| Zone | Ordinary vegetation emphasis | Distinctive / rare concept emphasis | Placement rule |
| --- | --- | --- | --- |
| Rimlands | Sparse grass, clover, sedge, low bushes, young trees | A few unusual forage plants or event growths | Preserve broad beach and trail views |
| Pinewood Wilds | Layered pines, broadleaf trees, ferns, berries, logs | Ancient resin tree / Goldencrown concept | Use patches around clearings, not a continuous screen of trunks |
| Mosswick Forest | Broad roots, giant mushrooms, ivy, shelf fungi, ferns | Giant coil fern / uncommon herb blooms | Keep stump entrances and main paths visually open |
| Riverlands | Reeds, willows, sedge, pondweed, lilies | Stormreed or rare herb patch concepts | Keep bridge landings, ford lines, and shore access clear |
| Crater Lake | Shore shrubs, lilies, limited island trees, ivy on ruins | Distinctive island growth or cache dressing | Do not obscure the island landmark from the shore |
| Emberhollow Caves | Sparse cave fungi and moss near damp surfaces | Unusual trumpet fungus / rare node accents | Avoid filling floors and catwalks with decoration |
| Frostpeak Ridge | Snow pines, alpine cushions, heather, sparse hardy grass | Frost shrub / Silverbark concepts | Group plants in sheltered pockets; preserve ridge sightlines |
| Fallen Temple | Ivy overlays, low grass, a few flowers and shrubs | Moonveil or rare herb concepts | Leave arch openings, stairs, and courtyard routes clear |
| Timberwatch | Trim sparse grass, exterior trees, some camp-edge shrubs | Rare vegetation mainly outside core structures | Gate hinges, stairs, ladders, and work areas stay usable |
| Shattered Keep | Low courtyard growth, ivy on outer ruins, sparse trees | Controlled landmark growth / event markers | Combat floor remains legible with a clear central space |

Use sparse, medium, and concentrated patch presets. Cluster vegetation around habitat cues such as water, logs, cliff bases, and sheltered edges, leaving deliberate empty ground between clusters. Do not distribute every species uniformly across every surface. Never turn ground-cover dressing into hundreds of independent colliders by default.

## 16. Geometry budgets, instancing, and collisions

The budgets below are optional prototype targets, not Roblox limits or guaranteed performance claims. The correct budget depends on how often an asset repeats, screen size, material count, collision, and the target devices.

| Asset | Initial triangle envelope | Main optimization priority |
| --- | --- | --- |
| Single simple leaf | About 10–20 | Reusable shape, no invisible extra loops |
| Grass tuft / tiny cover | About 40–160 | Number of repeated instances and overdraw/coverage |
| Ordinary herb / small flower | About 80–400 | Petal and leaf count |
| Forage shrub | About 250–1,000 | Foliage modules and hidden interior surfaces |
| Ordinary fungus clump | About 100–500 | Radial sectors and cap repetition |
| Ordinary tree | About 500–2,500 | Canopy silhouette and scene repetition |
| Landmark tree / giant stump | About 1,500–5,000 initially | Visible hollow/interior, scale, and placement |

Do not blindly decimate a detailed model to reach a number. Reduce the recipe: fewer canopy lobes, fewer cap sectors, fewer hidden branch segments, fewer flowers. Preserve the identity feature and outside silhouette.

Use linked mesh data for identical repeated modules during authoring, then handle target-engine packaging deliberately. A Blender collection instance is not automatically a verified Roblox-ready asset; realize/export an appropriate copy and test it.

For collision, keep vegetation leaf surfaces and tiny decorations nonblocking unless gameplay explicitly needs them. Use a simple trunk/base collision proxy for large plants if required. Floors, stairs, bridges, walls, and terrain need intentional walkable collision. Collision settings are target-engine configuration; a Blender mesh alone does not establish them.

## 17. Screenshot and mesh verification checklist

### 17.1 Required visual views

Capture front, side, top, and three-quarter views with consistent framing. Also capture:

- A low side/underside view of one leaf, flower, cap, or canopy tier.
- A bare-skeleton view of a shrub/tree before foliage hides its structure.
- An exploded view with parts separated enough to see attachments.
- A thumbnail view at approximately ordinary gameplay screen size.
- A character-scale comparison using the calibrated target rig or proxy.
- A variant contact sheet under identical lighting.

Use a plain neutral background and broad light. Do not hide intersections in darkness, use dramatic bloom to conceal crude shapes, or crop the feet, roots, tips, and backs out of inspection. When an MCP screenshot is unavailable, state that visual validation remains unfinished instead of claiming the asset matches the reference.

### 17.2 Mesh checks

- Inspect evaluated triangle counts, including modifiers, for export copies. The simple helper report above counts only unmodified geometry.
- Check zero-area faces, repeated vertices where inappropriate, flipped normals, self-intersections, and nonmanifold edges in parts intended to be closed.
- Open-ended art modules are permitted only intentionally; do not mistake an accidental hole for an optimized hidden surface.
- Check that leaves have side-visible volume and flowers/caps have undersides.
- Check that branches, stalks, fruit, and flowers actually connect.
- Check that the origin is correct and no unexpected negative scale or unapplied mirror affects export.
- Check material counts, names, missing shaders/textures, and preview-only objects.
- Check that a harvested state removes intended resources while keeping a coherent plant/base.
- Save the actual `.blend` to the authorized location and confirm the saved path exists. Do not claim export or in-engine validation without performing it.

### 17.3 Delivery status language

Classify checks as `Completed / Passed`, `Requires Manual Validation`, or `Incomplete / Needs Work`. A successful generation script is not a passed visual comparison. A Blender preview is not a passed Roblox import. State what was actually checked.

## 18. Common failures and exact corrections

| Symptom | Likely cause | Corrective action |
| --- | --- | --- |
| Foliage resembles crystals or spikes | Leaves are cones or width is too small | Replace with broad leaf wedges; move maximum width to middle; shorten and blunt tip |
| Tree resembles broccoli balls | Equal smooth/icosphere canopy blobs | Flatten and reshape masses, change branch layout, add a few broad contour lobes, preserve gaps |
| Grass resembles a hedgehog | Too many radial identical blades | Reduce to 3–7 blades; use tall/medium/short hierarchy and directional fan |
| Leaf disappears from side view | Zero thickness or one-sided plane | Build a closed shallow wedge or explicit underside; inspect normals |
| Leaf resembles an inflated pillow | Too much thickness/rounded smoothing | Reduce ridge depth; use fewer sharper planes; disable smooth shading where inappropriate |
| Plant looks like a tree stump with leaves | Oversized visible root plug | Bury/shrink/remove root plug; use narrow stem attachment |
| Shrub is an opaque green wall | Too many clumps, hidden structure | Remove some clumps, expose stem bases, create two or more clear crown gaps |
| Branch looks like disconnected sticks | No overlap or poor attachment angle | Reposition branch base into parent; align centerlines; rebuild visible joint if needed |
| Flower looks like disconnected triangles | Petals lack cup/overlap/center support | Widen petal roots; overlap under center; add shallow cup/rim |
| Mushroom is an open bowl balanced on a pole | Missing underside and weak stalk junction | Add inset underside disc and broader stalk connection |
| Berry bunch looks like jewels | Too few sharp apexes / extreme faceting | Use a squat rounded low-resolution volume with a few broad planes |
| Vine is tangled spaghetti | Excessively detailed curves and leaf count | Use short straight/elbow/fork modules and larger paired leaves |
| Rocks have confetti shading | Random material per triangle | Reduce to one main stone material and a few intentional broad regions |
| Rocks look melted | Subdivision, smooth shading, or remesh | Rebuild with broad rings/planes; flatten base; remove smoothing that destroys facets |
| Rare plant looks pasted in from another game | Different shader/detail density | Reuse the shared material/leaf grammar; keep only one or two novel features |
| All variants look the same | Only color/rotation changed | Change growth stage, canopy spread, branch count, or harvest state |
| Tiny details vanish in gameplay | Modeling at extreme close zoom | Inspect thumbnail; enlarge signature shapes and delete unreadable detail |
| Exported asset is giant or tiny | Double unit conversion or inconsistent scale | Import calibration cube, record measured ratio, correct one conversion stage |
| Render is gray though solid view is green | Shader nodes lack base color | Configure Principled base color and verify a rendered material preview |
| MCP rerun creates hundreds of duplicates | No deterministic ownership/naming | Replace only owned asset objects; reuse materials; report generated counts |
| Screenshots show an unchanged scene | Wrong Blender process/scene or stale capture | Verify scene/object counts and add a harmless named probe in the active asset collection |
| Whole world becomes too busy | No placement hierarchy | Reduce patch density, move taller growth to edges, clear paths and combat views |

Do not respond to any of these failures by indiscriminately adding detail. Change the smallest structural parameter that explains the mismatch, render again, and compare.

## 19. Ready-to-paste task prompt for a Blender MCP assistant

```text
Read WorldModeling.md before operating Blender. Use the attached selected asset
reference as the visual target. Build one representative asset first, not a
whole biome. Treat the guide's numerical ranges as starting proposals and
preserve existing project scale/material decisions when present.

In RBLX-Flintborn, read AGENTS.md and art/blender/README.md first. Use flintkit's
palette and Tint data, the existing sheet dimensions and 32-stud terrain grid,
the run.sh wrapper, and one finished mesh per static library asset. Keep editable
parts in authoring sources; use the existing GLB/manifest export contract.

1. Inspect the MCP capabilities and Blender scene/version. Identify the active
   file and collection. Preserve unrelated objects. Save a checkpoint when
   modifying an existing project.
2. Write a short asset spec: silhouette, size relative to the target character,
   part counts, leaf/branch recipe, signature feature, materials, pivot, seed,
   and intended variants. Resolve minor inconsistent concept views coherently.
3. Make the skeleton and big masses. Capture front/side/top/three-quarter views.
   Inspect actual screenshots. Fix silhouette and negative space now.
4. Build one reusable leaf/frond/tier/cap/pod module as explicit simple geometry.
   Inspect its thickness, underside, attachment and face normals close up.
5. Assemble the plant using a few purposeful modules. Keep fruit, pods, flowers,
   resin and overlays separate. Use shared matte colors and broad planes.
   No realistic textures, arbitrary noise, sphere-pile canopies, needle forests,
   decorative particle clouds, or global scene deletion.
6. Render under neutral lighting and compare with the target. State concrete
   mismatches, correct the responsible parameters, and capture again. Do not
   claim visual approval merely because Python ran successfully.
7. After the representative asset passes, build young/mature/harvested or
   structurally different variants with recorded seeds. Inspect a contact sheet.
8. Check measured dimensions, pivot, transforms, normals, intersections, triangle
   count including modifiers, material count and export selection. Keep studio
   cameras/lights/floor out of asset export copies.
9. Save the editable blend and any explicitly requested exports to the authorized
   destination. Report actual output paths, what was visually checked, what
   still needs target-engine validation, and any unresolved issues.

Continue through routine modeling and correction steps autonomously. If a tool
or capability is unavailable, say exactly which step is blocked. Do not invent
screenshots, exports, successful saves, tool calls or completed validation.
```

### 19.1 Concrete first task when the modeler is struggling

Start with **one Silkleaf or strap-fern rosette**. It has five broad leaves, a simple center, and an optional tuft, so it exposes the most important style errors quickly. Build a single thick leaf, inspect its side view, make five arranged copies, then inspect the whole silhouette. Do not begin with a giant ancient tree or an entire forest.

Once the rosette is correct, use the same leaf grammar for a raspberry shrub. Once the shrub is correct, test one canopy module and a small birch. This progression tests leaf shape, plant assembly, branch hierarchy, and large foliage masses separately.

## 20. Reference index and technical lookup notes

Attach the actual relevant images to the modeling session. A reference title alone does not give an LLM visual access to its pixels. Use the matching row within a sheet rather than asking the modeler to infer one plant from an entire zone image.

### Vegetation sheets

| Sheet | Families |
| --- | --- |
| V01 — Common Meadow Plants | Clover patch, field sedge, bluegrass, dandelion |
| V02 — Common Bushes & Forage | Raspberry, elderberry, hazel, rosehip |
| V03 — Forest Ferns & Climbers | Bracken, strap fern, heartleaf creeper, trumpet vine |
| V04 — Riverbank & Aquatic Vegetation | Cattail, bulrush, water lily, pondweed |
| V05 — Mushrooms, Fungi & Cave Growth | Chestnut mushroom, amber shelf fungus, puffball, cave trumpet |
| V06 — Additional Common Trees | Birch, willow, rowan, juniper |
| V07 — Hardy, Dry & Alpine Plants | Heather, alpine cushion, dry tussock, thorn scrub |
| V08 — Uncommon Harvestable Plants | Flax, Silkleaf, Redroot, Sunpod |
| V09 — Rare Event Flowers & Shrubs | Sunburst Bloom, Moonveil Orchid, Stormreed, Heartpod Bramble |
| V10 — Rare Trees & Ancient Growth | Goldencrown, Silverbark, Resinheart stump, giant coil fern |

The wider world sheets cover rocks/scatter; cliffs/ledges/ramps; shorelines/waterfalls; conifers; broadleaf/deadwood; bushes/ferns/vines/moss; grasses/flowers; bridges/docks; paths/stairs/fences; shelters; camp props; Timberwatch walls and buildings; cave shells; mine equipment; masonry; lake/temple structures; Mosswick; Frostpeak; the keep/event dressing; boats/moorings; and mine scaffolds/fittings.

### Technical lookup

Use Blender's official documentation for the **connected version**, especially when a specific property or exporter differs. This document's original art recipes are project guidance, not official Blender or Roblox specifications.

- [Blender Mesh API](https://docs.blender.org/api/current/bpy.types.Mesh.html): mesh creation with `from_pydata`, mesh updates, polygons, and triangle inspection.
- [Blender Material API](https://docs.blender.org/api/current/bpy.types.Material.html): viewport material data and shader access.
- [Blender 5.0 Python API release notes](https://developer.blender.org/docs/release_notes/5.0/python_api/): material-node behavior changes, including deprecation of `Material.use_nodes`; inspect the connected version instead of blindly relying on it.
- [Blender Object API](https://docs.blender.org/api/current/bpy.types.Object.html): parenting, transforms, bounds, and object data.

The operational rule is simple: inspect capabilities, construct a small asset, look at real screenshots, correct the geometry, and only then scale up the library.
