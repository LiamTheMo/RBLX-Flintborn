# Flintborn — Character and Creature Modeling Guide

> **Purpose:** A self-contained art specification for an LLM building Blender models and preparing them for Roblox.  
> **Scope:** The shared R6 survivor, hair and primitive clothing, regular wildlife, passive wildlife and event-creature concept designs.  
> **Authority:** [GDD.md](GDD.md) governs gameplay; [visuals.md](visuals.md) governs the wider world; [art/blender/README.md](art/blender/README.md) describes the existing production pipeline.  
> **Status:** Character direction and creature reference vocabulary, with proposed modeling recipes. Animal concepts are not an approved spawn catalog, balance table or completed runtime implementation.

## 1. Read this before generating geometry

Flintborn's inhabitants belong to a **bright, cartoony, primitive Roblox world**. They have generous readable volumes, warm natural colors, deliberate simplification and very little surface noise. A viewer should recognize the body shape and species before noticing individual facets. Characters should look comfortable beside chunky trees, angular rocks, timber shelters, hide, bone and rope.

There are two related surface treatments. The humanoid is a classic R6 avatar with clean softly rounded block limbs and a rounded cylindrical head. Animals use more visible planar facets, with broad angular muscle masses and a few geometric fur or feather groups. Do not turn the avatar into a sharply triangulated animal sculpture, or smooth every animal into an inflated clay toy. Their shared identity comes from simple forms, readable faces, palette and material restraint.

### Authority and reference interpretation

1. Follow the owner's explicit current brief for the requested asset.
2. Preserve current repository integration contracts when modifying an existing model, especially the R6 rig, clothing assignments, texture names and export transforms.
3. Use this guide for the character and animal shape language. Use `visuals.md` for environmental consistency.
4. Use concept sheets for silhouette, colors and identifying features. Reconcile inconsistent views into one coherent model rather than reproducing generation errors.
5. Use marketing icons for character identity and overall appeal only. Their huge chasing animals, exaggerated expressions, golden outlines, dust and camera distortion are presentation choices.

The early bald-character sheet and icons show a side knot on the tunic. The current `build_09_character.py` explicitly describes a later master without the tie. **Preserve the current knot-free production default.** A knot is an optional reference-specific variant when requested; do not silently add it back to the shipped asset. Similarly, the Blender README's older head dimensions differ from the current builder and generated manifest: use the current builder and manifest together for an actual rebuild.

## 2. Visual identity and shape hierarchy

### Primary forms

Begin with three to six large masses: torso, head, shoulder/hip masses and the main appendage. A bear is a heavy barrel with a low broad head; a stag is a lifted chest and narrow body on long legs; a boar is a wedge head attached to a low barrel; a mammoth is a high shoulder hump and hanging trunk. These differences must survive a solid-black silhouette test.

Enlarge functional identifying features selectively. A boar needs a broad snout; a dodo needs a hooked beak; a rabbit needs tall ears and long rear feet. Make these features thick enough to survive gameplay distance. Avoid enlarging every feature equally, which produces the same generic animal with different ears.

### Secondary forms

Use cheeks, muzzles, brow ridges, chest ruffs, shell rims, shoulder humps and broad belly transitions to establish the design. Each secondary piece must explain anatomy, material or species. Large geometric tufts can break a silhouette; a forest of tiny tufts cannot substitute for a correctly shaped body.

### Tertiary detail

Limit fine detail to features players actually read: nostrils, eye shapes, a simple mouth line, a few stripes, hoof separation or a small cloth fold. Avoid pores, dense stitching, individual hairs, whisker cylinders, realistic scales, vein networks, randomly chipped surfaces and high-frequency procedural noise.

### Mood

The baseline mood is adventurous and approachable. Passive wildlife has calm brows, relaxed ears and closed mouths. Ordinary predators can look alert or stern. Event animals may have heavier brows, larger natural weapons and more mass while retaining the same art style. Terrified avatar faces and roaring animals belong in expression variants and marketing poses, not the neutral modeling default.

## 3. Blender coordinate, scale and scene contract

The existing pipeline uses **1 Blender unit = 1 Roblox stud**. Model upright with **+Z up and front toward -Y**. With this orientation, the subject's anatomical right is **-X** and its left is **+X**. Use anatomical left/right consistently in names; a front camera reverses the viewer's impression.

For a new creature, place a ground-root Empty at the bottom-center of its neutral footprint, at Z=0. Keep the body above that plane and feet resting on it. Give moving objects their own functional origins or bones. The bottom-center asset convention describes the assembly root; it does not mean every limb pivots at the ground.

Reuse the existing humanoid rig instead of recentering its bones. Preserve the character's `HumanoidRootPart`, Motor6D data and clothing mappings. Blender axes differ from Roblox's Y-up frame; do not copy Blender coordinates directly into Roblox CFrames. The character exporter and importer already account for conversion and an import-facing half-turn; applying another guessed rotation breaks offsets.

Use a separate collection for reference images, cameras, lights and explanatory pivot markers. None belongs in the runtime export. Keep working meshes and export meshes clearly separated so joining a contact-sheet assembly cannot destroy the rig.

### Current R6 body measurements

These values describe the current builder, in Blender **X × Y × Z**, not Roblox's axis ordering. They are a reproducible starting point, not a new redesign.

| Part | Dimensions in studs | Center in Blender | Shape |
| --- | --- | --- | --- |
| Torso | 2 × 1 × 2 | (0, 0, 3) | Rounded rectangular block |
| Head | 1.38 × 1.38 × 1.3 | (0, 0, 4.65) | Upright cylinder with softly filleted ends |
| Right Arm | 1 × 1 × 2 | (-1.5, 0, 3) | One rigid rounded block |
| Left Arm | 1 × 1 × 2 | (1.5, 0, 3) | One rigid rounded block |
| Right Leg | 1 × 1 × 2 | (-0.5, 0, 1) | One rigid rounded block |
| Left Leg | 1 × 1 × 2 | (0.5, 0, 1) | One rigid rounded block |

The current visible body reaches approximately 5.3 studs, excluding hair. Do not substitute the pipeline README's approximate avatar-height shorthand for these coordinates. Preserve current joint matrices from `build_09_character.py` and `art/roblox/character/manifest.json`; the head's neck offset is customized to this mesh.

Animal sizes remain an art/gameplay decision. Block them out beside this R6 body, record chosen width, depth and height, and seek consistency within a species. Do not infer approved world size, hitboxes, aggro radius or boss scale from a close-up icon. A helpful provisional scale brief is “rabbit smaller than the avatar's lower leg” or “mammoth towers over the avatar”; convert it to explicit dimensions in the asset task before final export.

## 4. The shared R6 survivor

### Body and identity

Use one gender-neutral character design. Keep a straight block torso, equal block arms, equal block legs and simple rounded head. The chosen base reference has light warm peach skin. Do not add gender-specific anatomy, muscular sculpting, realistic fingers, toes, nails, kneecaps, elbows, ears, a modeled human nose or realistic lips.

The body should feel solid but approachable: broad planes with soft edge transitions, not a featureless sphere or a jagged low-poly human. Maintain the characteristic rectangular limb profile in side and front views. Feet are the bottom of each leg block; hands are the ends of each arm block. Do not append human hands or shoes to “improve” anatomy.

Keep the head centered and seated naturally above the torso. It is a softly rounded cylinder, not a sphere, egg, cube or detailed skull. Its vertical sides remain readable between the rounded top and bottom. In the current builder, the cylinder uses controlled rings and fillets; preserve its profile rather than adding subdivision until it looks like a different avatar.

### Face

The baseline is the classic simple black Roblox smile: two upright oval eyes and a curved mouth. Place the face on the front of the cylinder, centered horizontally with enough spacing to avoid a crowded expression. Use the existing face texture and UV treatment for production continuity. Do not add realistic eyeball sockets or protruding eyes to the humanoid.

For expressions, change only the graphic shapes: brows, eye openings and mouth. A frightened face can use raised brows and an open mouth; an alert face can use a smaller smile. Keep the same head geometry and face placement. Never bake the icon's illumination, sweat, motion blur or rim glow into the face texture.

### Primitive tunic

Construct a matte tan hide wrap over the **anatomical left shoulder (+X in Blender)**, with a diagonal neckline descending toward the opposite side. Cover the torso while leaving the other shoulder and the block arms exposed. The neckline should be a deliberate continuous contour, not a random boolean cut.

Use a thin closed shell offset slightly from the torso. Build a broad front and back surface, a readable edge at the neckline and a gently uneven lower hem. A few large folds suggest soft hide; avoid hanging rags everywhere, tiny wrinkles, modern seams, collars, buttons, zippers and ornamental trim. Keep arm/neck openings clear during animation.

The current production wrap has no side tie. For an explicitly requested early-sheet variant, use one small rounded knot and two short thick hanging tabs at the side. Attach that knot to the torso clothing group; keep it subordinate to the wrap and out of the arm swing path.

### Shorts

Use short primitive hide trousers with a broad waist and separate left/right openings. The baseline appearance is earthy brown, with a gently irregular hem. Bare lower legs remain visible. Avoid belts, pockets, buckles, denim, drawstrings and stitched modern sportswear.

Production clothing is split into `PantsWaist`, `PantsLeftLeg` and `PantsRightLeg`. The waist follows the torso; each leg section follows its own R6 leg. Preserve the current hip-roll coverage that prevents holes when legs swing. Do not weld the whole shorts mesh to the torso or skin it across two rotating rigid legs without testing the resulting folds and intersections.

### Hair variants

The bald version is the baseline. Additional hair uses the same head and body; it does not create male/female character categories. Build hair from a close-fitting cap and a few large locks or clumps. Give it a clear front outline, side profile and rear shape. Keep the face and top of the neckline readable.

Suggested construction families include a short crop, side-swept fringe, compact spiky clumps, a broad wavy cap or tied-back mass. These are extension recipes, not a finalized approved hairstyle catalog. Use a small natural palette and avoid realistic hair cards, thin strands, glossy salon styling and dense curls made from hundreds of spheres. Hair follows the head rigidly unless a later brief explicitly requires secondary animation.

## 5. Creature construction grammar

### Blockout before detail

Create the torso as an elongated low-resolution ellipsoid or a controlled sequence of polygon cross-sections. Establish shoulder width, hip width, back slope and belly height. Attach a separate head mass with the correct muzzle or beak length. Set limb lengths and foot contact before adding fur, stripes or teeth.

Do not build every animal from intersecting identical spheres. Slight overlap is acceptable in a blockout; a finished body should have intentional transitions. For a deforming skin, connect surfaces and create useful joint loops. For a rigid segmented rig, overlap joint caps enough to conceal gaps through the intended motion range.

### Facets

Prefer a small number of broad readable planes. A provisional low-resolution cross-section might use 8–12 vertices around a body or limb; add vertices only when the silhouette or deformation requires them. This is a modeling recipe, not an engine limit. A few triangles on a flank should explain its volume; hundreds of random tiny triangles merely add noise.

Use flat shading for animal masses and deliberate smooth shading where a feature needs a clean curve. Keep major shape boundaries crisp. Do not indiscriminately subdivide, remesh or decimate the whole model. Random vertex displacement should never disturb symmetry, foot contact, eye alignment or joint placement.

### Fur, feathers and scales

Fur is implied by the body volume plus a few thick tapered wedges around cheeks, chest, shoulders and back. Each wedge has a broad base and a blunt tip. It follows the direction of the coat and does not look like a crystalline spike. Use fewer, larger wedges on smaller animals; a mammoth can carry more broad overlapping layers.

Bird wings are compact masses with a few large feather tips. Reptile scutes are broad plates or ridges, not individually modeled microscopic scales. A tortoise shell is one coherent dome with large scute regions, not a pile of disconnected rocks. Skin folds on a rhino are part of its organic hide, not armor panels attached with hardware.

### Faces and expression

Animal eyes can be shallow inset shapes or simple low-poly eyeballs with dark pupils and restrained cream sclera. They differ from the avatar's flat face. Keep paired eyes aligned and visible from appropriate side angles. A brow should read as a small natural ridge or graphic shape, not an extra horn.

Use a dark recessed mouth line for closed jaws. Separate the lower jaw when animation requires it. Teeth attach to a jaw and point in coherent directions. Show nostrils as broad dark insets or color shapes. Avoid deep realistic mouth anatomy; an open mouth needs a simple cavity and tongue, not gums and individual molars at full detail.

### Limbs, feet and symmetry

Build mirrored paired features from a common source and preserve symmetry until the main structure works. Use four legs for quadrupeds, two legs and two wings for birds, and two arms plus two hind legs for the gorilla. Do not reproduce additional limbs or inconsistent toe counts from a generated sheet.

Feet are an identity feature: feline/canine paws, pig/goat/deer/bison cloven hooves, elephant column feet, rhino three-toed feet, ape hands, reptile toes and rabbit rear feet must remain distinct. A generic paw cannot stand in for every species. Hide small far-side toes naturally in orthographic views rather than inventing visible duplicates.

## 6. Materials, color and surface restraint

Use matte organic materials with broad color regions. Fur, hide, feathers, horn, bone and skin have zero metallic response by default. A provisional roughness range of 0.65–0.95 suits most organic surfaces; these are starting values for a new creature, not replacements for the existing character's tuned maps. Eyes can have a small restrained highlight. Avoid wet glossy skin, plastic-looking fur and chrome horns.

Animal coloration should normally use a dominant body color, a lighter underside or muzzle, a darker accent, an eye/nose color and an ivory horn/tooth color when needed. Use contiguous face-material regions or a simple palette texture. Avoid scattered per-face rainbow variation and outlines painted around every polygon.

### Existing character colors

These are current code values, not colors sampled from a lit concept render. Preserve them when rebuilding the production character; future changes must update the builder, textures and export consistently.

| Role | Current value | Intended appearance |
| --- | --- | --- |
| Skin | `#F7CDB1` | Light pastel peach |
| Shirt | `#C8AC88` | Warm muted tan hide |
| Neutral pants base | `#BDB5A8` | Tintable neutral material |
| Earth pants tint | `#643E20` | Default earthy brown |

The character already has shirt/pants color, normal and roughness maps, plus tribe-color variants under `art/character/textures/`. Preserve that established exception to the shared palette workflow. Do not replace those maps with generic flat environment materials merely because the broader world uses `flintkit.PALETTE`.

For new creatures, reuse appropriate shared palette keys and `Tint` attributes where practical. If a species needs an unavailable color, make an explicit reusable palette extension through the established helper rather than silently editing a shared material used by other assets. The existing environment prop budgets and palette are useful context; neither constitutes a measured animal performance budget.

### Markings

Tiger stripes, capybara muzzle contrast, tapir saddle and gorilla silverback areas should be broad stable shapes. Build one deliberate pattern and carry it across all views. Use material assignments or a clean low-noise texture; do not make every stripe a thick floating mesh. Preserve continuity across the back, belly and moving joints. Keep normal-map detail shallow enough that the silhouette still carries the style.

## 7. Regular and passive creature briefs

The following are reference concepts from the generated sheets. “Passive” describes the intended concept category, not a claim that retaliation, taming, drops, spawning or AI has been implemented. Confirm behavior separately with the GDD and catalogs. No breed, real-world habitat or appearance automatically establishes a game mechanic.

| Concept | Primary silhouette and palette | Required identifying features | Breakdowns to preserve |
| --- | --- | --- | --- |
| Wild Boar | Low dark-brown barrel, wedge head, rusty back ridge | Broad flat pig snout with two nostrils; two small ivory tusks; short legs; split hooves; curled short tail | Head/jaw, torso, foreleg/hoof, bristle ridge, tail |
| Forest Stag | Narrow tan torso, lifted cream chest, long legs | Two matching angular antlers with a modest few prongs; broad ears; black nose; cloven hooves; short tail | Head, antler pair, torso, full leg, ears/tail |
| Grey Wolf | Long grey body, cream underside, angular cheek ruff | Long canine muzzle; upright ears; bushy low tail; four canine paws; no feline face | Head/lower jaw, torso, hind leg/paw, tail |
| Brown Bear | Heavy warm-brown barrel, broad shoulders, low head | Rounded ears; short tan muzzle; very short tail; broad plantigrade paws and claws; four-foot neutral stance | Head/jaw, torso, foreleg/paw, ear, tail |
| River Crocodile | Long low olive body and powerful tapering tail | Broad flattened snout; raised eyes; short splayed legs; pale underside; simple dorsal scutes | Skull/jaw, torso, splayed leg, segmented tail, top view |
| Plains Bison | High shoulder hump sloping toward low hindquarters | Broad low head; two short outward/upward horns; dark shaggy front and chestnut rear; split hooves | Head/horns, hump/torso, leg, mane groups, tufted tail |
| Meadow Rabbit | Compact sandy body, tall ears, large folded rear legs | Cream muzzle/belly; two pink-lined ears; short forelegs; long hind feet; small round tail | Head, ear pair, torso, foreleg, folded hind leg, tail |
| Island Dodo | Plump blue-grey bird, cream belly and tail fan | Huge pale hooked beak with dark tip; orange eye patch; two stubby wings; two ochre bird legs | Head/beak halves, torso, wing, leg/foot, three broad tail-feather groups |
| River Capybara | Long low caramel barrel and blunt rectangular head | Tiny high rounded ears; high eyes; short legs; no visible tail; front four-toed and rear three-toed feet | Head, torso, ear pair, front/rear feet, top view |
| Highland Goat | Compact cream body, taupe face/legs, short upright tail | Two backward-swept horns; sideways ears; small geometric beard; cloven hooves | Head, horn pair, torso, leg/hoof, ears/beard/tail |
| Forest Tapir | Rounded charcoal body with broad cream saddle | Short flexible tapered snout; cream-rimmed round ears; tiny tail; four front toes and three rear toes | Head/snout, patterned torso, ear pair, front/rear legs, tail |
| Giant Ground Sloth | Deep brown barrel, long forelimbs, shorter hind legs | Cream broad face/chest; rounded ears; three large foreclaws; stout tapering tail; calm low stance | Head, torso, long forelimb/claws, hind limb, tail segments |

### Species-specific cautions

The rabbit needs visibly different front and hind limb proportions; it must not become a dog with long ears. A capybara has a blunt rodent head, not a pig nose disk. The tapir's nose is a short prehensile snout, not a hanging elephant trunk. The dodo remains a flightless bird even if its stylized wings are large enough to read clearly.

A crocodile needs side and top views because a front view conceals most of its body length. Keep a clear distinction between forelimb and hind-limb placement. The sloth's large claws are natural digging features; its neutral presentation should not acquire a predator's snarl. Its detailed biological rig can be simplified for the game, but must retain its distinctive forelimb proportions and tail.

## 8. Event-creature briefs

Event creatures use the same material language and polygon scale as ordinary wildlife. Increase body mass, shoulder height or natural feature size deliberately; do not achieve importance with dense ornamental geometry. A rare passive creature can be visually remarkable without looking hostile. The following category assignments are concept labels, not finalized encounter rules.

| Concept | Shape and color direction | Construction requirements | Avoid |
| --- | --- | --- | --- |
| Saber-Toothed Tiger | Broad orange feline head, cream muzzle/chest, dark stripes, heavy shoulders | Exactly two long upper saber teeth attached to the upper jaw; broad paws; hinged lower jaw; ringed tail | Pig tusks, canine proportions, multiple fang pairs, floating teeth |
| Woolly Mammoth | Towering chestnut shoulder hump, long shaggy masses, small ears | One segmented trunk; exactly two matching outward/forward/upward ivory tusks; four columnar elephant feet with nail plates | Cat claws, gorilla hands, multiple trunks, tusks growing from trunk |
| Iron-Tusk Boar | Charcoal broad body, raised shoulders, brick-red bristle crest | Pig snout; two enlarged lateral upward tusks; short cloven-hoof legs; curled tail | Tiger paws, extra horns, forged metal plating; name does not imply metallic skin |
| Ancient Tortoise | High continuous dark shell, olive limbs, tan rim, sparse moss patches | Four short sturdy legs; beaked head; coherent scutes; separate plastron; tiny tail | Sea-turtle flippers, piles of loose rock, trees/buildings/crystals on shell |
| Stonehide Rhino | Low massive grey head, barrel torso, broad natural hide folds | Two nasal horns in a front-to-back line; four pillar legs; three-toed feet; small tufted tail | Side-mounted bull horns, bolted armor, tusks, magical stone effects |
| Crater Gorilla | Huge shoulders, long arms, shorter hind legs, charcoal fur and silver saddle | Knuckle-walking neutral pose; two arms/two legs; five-digit hands/feet; no tail | Cat paws, horns, humanoid clothing, tail, rigid upright human posture |

### Natural exaggeration and effects

An event boar is distinguishable through its raised shoulders, larger tusks and strong crest, not just a uniform scale multiplier. The tortoise is distinguished by its dome and deliberate moss patches; the gorilla by shoulders and forearms. Keep one or two dominant visual signals per species.

Do not add glowing eyes, crystals, lava seams, floating runes or magical armor by default. Such treatments need a separate encounter brief. If effects are later approved, use named sockets and detachable effects so the underlying creature remains usable without them. Runtime hitboxes and attack reach must follow gameplay decisions rather than the size of a decorative horn or tusk.

## 9. Reproducible Blender construction recipes

These are implementation suggestions for a modeling LLM. Reuse the existing helpers and conventions where they already solve the task; do not replace a proven builder with a generic primitive generator.

### A. R6 body and clothing

1. Load the current character builder's dimensions, material constants, bone transforms and clothing mappings. Retain its coordinate system.
2. Build the six rigid visible body parts independently. Bevel block edges conservatively while preserving planar centers. Construct the head as a filleted cylinder.
3. Apply the existing face UV orientation and texture. Check it from front and both sides before adding clothing.
4. Construct the diagonal wrap as a shell around the torso, with an intentional neckline and hem; keep it bound to the torso only.
5. Preserve the waist/left-leg/right-leg pants split and hip rolls. Keep torso clothing clear of the rotating legs and shoulders.
6. Assign rigid weights to each body part's bone; preserve current R6 Motor6D matrices in the export. Add hair as a separate head-attached variant only when requested.
7. Test the existing walk/run poses and head turns. Compare neutral front, side and rear views to the current model before changing any production mesh.

### B. Quadruped torso and head

1. Write the neutral width/depth/height and head-to-body ratio into a configuration object. Specify shoulder and hip Z values independently.
2. Place body cross-sections along the -Y/+Y length axis. Vary ring width/height to make a shoulder, flank, belly and rump rather than a stretched sphere.
3. Connect ring vertices with predictable faces; preserve a clean mirror plane at X=0. Add deformation loops only where required by the chosen rig.
4. Build the head from a cranium, cheek volume and species-specific muzzle. Separate the jaw before detailing the mouth.
5. Place paired legs at shoulder and hip stations. Establish full foot contact, proper knee/hock direction and a usable gap between legs.
6. Add ears, tail and only the required horn/tusk pair. Check their attachment in all views.
7. Add a restrained fur/feather/scute pass and broad markings. Recheck the black silhouette after each detail pass.

### C. Horns, tusks and claws

Use a short chain of cross-sections following a smooth centerline. Taper from a broad attached root to a slightly blunt tip. Preserve consistent cross-section orientation so the mesh does not twist unexpectedly. A low-resolution curve sweep or explicit ring mesh is suitable; apply or evaluate curves intentionally before export.

Mirror a single source for paired tusks/horns. Keep the pair's curvature and insertion points consistent. Rhino horns sit sequentially on the nose, not mirrored to either side; mammoth tusks form a bilateral pair. Teeth attach to jaws and claws to digits. Avoid closed tips so thin that they vanish or create unstable shading.

### D. Tortoise shell

Build an upper dome from broad longitudinal and crosswise sections, establish a thick perimeter rim, then define a small number of large scute regions. Use material boundaries or shallow controlled edges to separate scutes. Fit a separate underside plastron and leave head/limb openings with believable clearance. Do not use a solid sphere intersecting all four legs as the final shell.

### E. Bird

Build a broad pear-shaped torso, a short neck, rounded head and two-piece beak. Fit compact mirrored wing masses to the sides and two legs below the center of mass. Make each foot's toes intentional, with a stable standing footprint. Attach a short tail fan to the rump; its large feather pieces should read as one fan rather than a second pair of wings.

### F. Script reliability

Use a species configuration for dimensions, color keys, limb stations and feature counts. Seed any controlled variation for reproducibility. Build inside a named collection and clean up only objects owned by that build; never delete unrelated scene data. Prefer direct mesh/data APIs for predictable construction; when using operators, set object selection, active object and mode explicitly.

Save the source `.blend` and inspection renders through the existing pipeline. For repository builds, run the wrapper:

```bash
art/blender/run.sh scripts/build_09_character.py
```

That is the existing character builder, not a creature builder. Animal script names, library assignments and exporters must be introduced deliberately when animal implementation is authorized. Do not claim a new species is integrated merely because an LLM produced a mesh or render.

The wrapper detects script errors and stale outputs. Consult its documentation before choosing expected outputs for a new builder. Keep build logs, do not treat a bare Blender zero exit code as proof of success, and avoid pipelines that hide errors. Do not run the character builder merely to validate edits to this Markdown guide.

## 10. Rigging and assembly contracts

### R6 survivor

Keep the six visible rigid parts and the existing root hierarchy. No elbow, knee, finger or toe articulation is introduced by this style guide. The face is a graphic surface. Clothing follows its designated part. Hair follows the head. A render pose may look energetic, but it must be achievable by rotating the rigid R6 limbs rather than bending them like R15 anatomy.

### Animals

Choose one runtime strategy before final topology: a skinned mesh with an armature, or a rigid segmented assembly. A connected skinned body is usually useful for bending backs, shoulders and organic tails; a rigid assembly can suit simple low-detail mobs. These are options, not existing repository animal-integration guarantees.

Use a ground root, a body/spine root, neck/head control, optional jaw, four limb chains for a quadruped, and the minimal tail chain needed for its silhouette. Add a trunk chain only for a mammoth; wing controls for a bird; arm/hand controls for a gorilla. Horns, tusks and shell scutes follow their parent mass rigidly unless a specific mechanic requires otherwise.

Place joint centers inside the actual anatomy. A pivot marker on a reference sheet is explanatory; **do not export visible ball joints** unless deliberately requested as a style change. Keep shoulders, hips, jaw hinges and tail bases covered through their tested ranges. Do not leave permanent exploded gaps from the reference breakdown.

The environment's “one asset = one mesh object” convention is for those static libraries. Do not join every animated part into one rigid prop. A skinned mesh can contain disconnected rigid islands sharing an armature; a segmented model can contain several objects beneath one root. Preserve the existing R6 special case and document the chosen animal contract.

### Animation checks

Test neutral idle, a walk cycle and turning for every moving creature. Test the jaw only where used, and additional behavior poses only when requested. Check foot sliding, reversed joints, collapsed volume, exposed gaps, crossed legs, tail intersections and tusks clipping through the face. Do not add attacks or hostile behavior to a passive concept as a modeling convenience.

## 11. Modeling-sheet presentation

Each reference sheet describes **one animal design**, not four variants. Show front, left side, rear and three-quarter views at matching scale, in the same neutral stance. Use orthographic cameras for alignment views; perspective is acceptable for the three-quarter presentation. Add a top view where it clarifies a shell, crocodile, body width or marking pattern.

Use a warm off-white background, soft neutral lighting, restrained shadows and generous spacing. Keep every toe, horn, ear, beak and tail in frame. No cinematic depth of field, bloom, motion blur or scenery. Label only useful information: animal name, concept category, view names and major part names. Do not invent numerical dimensions, health, rarity or loot values.

The breakdown should show a head, torso, representative full limb and identifying features. An exploded view must be a view of the same model with reversible offsets, not an unrelated anatomy sketch. Indicate pivots and parent relationships separately. Prefer larger useful panels over many tiny duplicate angles.

Render both the assembled creature and the parts from the actual Blender geometry. A visually convincing generated image is not proof of a watertight mesh, consistent orthographic proportions, correct topology, a working rig or an export that Roblox can load.

## 12. Export, optimization and runtime integration

Preserve an editable source, a separate export collection and a simple diagnostic scene. Use PascalCase asset names and stable part identifiers. Record source script, dimensions, forward/up axes, material keys, texture references, root location, rig strategy and exported triangle count. Do not rename existing character objects or texture files casually.

Inspect unapplied transforms before export. Resolve nonuniform scale and negative mirrored transforms without breaking the armature or animation. Recalculate normals deliberately; remove accidental duplicate faces, floating construction geometry and z-fighting surfaces. Ensure material and UV assignments survive evaluated modifiers. Keep export-time triangulation deterministic and inspect it around joints.

Keep runtime collision separate from visual detail. Use simple body collision proxies; thin fur tips, antlers and tusks should not automatically become movement blockers or damage regions. Rig size, collision, navigation and attack checks need validation in the actual game.

The current character `.glb` files and joint manifest are produced by the character pipeline and consumed by `scripts/roblox_character.py`. Reuse it for that character. The existing lobby exporter is a static environment workflow, not a general animal skinning exporter. Verify bones, weights, materials, scale, orientation and animations through an actual Studio import before claiming a creature export is supported.

The Blender README's prop/building targets do not establish tested character or animal budgets. Count triangles, bones, materials, textures and objects per creature and across a representative populated scene. Keep small wildlife especially economical; event size alone does not justify excessive geometry. LODs should preserve the species silhouette and identifying features while reducing fur groups, internal mouth detail and small appendages.

References under `art/reference`, source libraries under `art/blender`, exports under `art/roblox` and runtime models under the existing `src/assets` structure serve different purposes. Use the current asset documentation and the specific upload workflow for integration. Committing a `.blend`, image or this guide does not replace a live Roblox model. Publish production-affecting asset changes only through the authorized main-based workflow.

## 13. Common failure modes and corrections

| Failure | Correction |
| --- | --- |
| All animals look like the same dog | Rebuild body proportions, muzzle length, shoulder height and foot type before adding species decorations |
| Every surface looks crumpled | Remove random displacement and unnecessary triangulation; restore broad intentional planes |
| Flat-shaded human looks crystalline | Preserve clean block faces and the softly rounded R6 body treatment |
| Animals look like smooth clay | Restore deliberate planar masses and a few broad silhouette accents |
| Fur looks like spikes or scales | Flatten and broaden tufts, reduce their count and align their direction |
| Mammoth tusks cross the trunk unpredictably | Mirror one tusk, place clear roots beside the mouth and inspect front/side/top views |
| Boar has claws or tiger teeth | Use split hooves, a pig snout and lateral lower-jaw tusks |
| Tapir becomes a baby elephant | Shorten the snout, retain a rounded saddle-marked torso and correct toe structure |
| Shorts expose holes while running | Preserve leg-specific clothing, hip rolls and tested overlap with the torso waist |
| Side knot reappears on the current survivor | Keep it excluded from the production default; use only in an explicitly requested variant |
| Rig shows metallic balls and gaps | Remove reference markers from export and restore assembled joint coverage |
| Passive wildlife looks aggressive | Relax brows, close the mouth and present a neutral standing pose |
| Beautiful render imports at wrong scale/facing | Check the exporter/importer axis contract and measure beside the existing R6 character in Studio |
| Different orthographic views disagree | Choose one coherent anatomy, regenerate all views from that single model and record the reconciliation |

## 14. Copyable brief for a Blender modeling LLM

```text
Create an editable Blender model for Flintborn using Modeling.md and the
current repository art pipeline. Subject: <asset name>. Reference: <explicit
reference file or sheet>. Category: <R6 survivor / passive / regular / event>.

Use a bright cartoony primitive Roblox style: broad readable volumes, natural
colors, mostly matte surfaces, deliberate low-poly simplification and minimal
surface noise. Preserve the softly rounded rigid R6 treatment for humanoids;
use broad planar anatomy and restrained fur/feather groups for animals.

Use 1 Blender unit per stud, +Z up, front -Y. Anatomical right is -X. For a
new creature, put its assembly root at bottom-center and document actual
width/depth/height. For the existing R6 character, preserve current dimensions,
bone pivots, Motor6D matrices, clothing assignments, UVs and export transforms.
The current production tunic has no side tie; add one only if this task asks.

First block out the silhouette and feet beside the R6 scale reference.
Then build species-specific head, limb, foot and appendage anatomy. Preserve
paired-feature symmetry and exact limb counts. Add broad color regions and
only details that improve species recognition. Do not copy generation errors,
chase-camera distortion, marketing glow or reference pivot balls into the mesh.

Rig strategy: <existing R6 / skinned creature / rigid segmented creature>.
Required motions: <explicit list>. Keep collision and gameplay hitboxes separate
from the visual mesh. Do not invent stats, spawn rules, abilities or loot.

Deliver the editable source, the reproducible build script, four matching
neutral views and a model-derived parts breakdown. Export only through a
workflow that supports this rig type. Record dimensions, materials, geometry
counts and unresolved issues. Inspect the actual model and actual Studio
import before marking rigging or integration passed.
```

## 15. Completion and review record

Use the following classifications for an implemented asset. Empty checkboxes are requirements to verify, not assertions that this documentation task created or tested a model.

### Completed / Passed

- [ ] Inspected assembled model matches the intended character/species silhouette and shared Flintborn style.
- [ ] Four model-derived views agree on proportions, colors, markings and appendages.
- [ ] Anatomy, paired features, feet and limb counts are correct.
- [ ] Current R6 contracts are preserved where applicable; no accidental R15 joints were introduced.
- [ ] Materials are restrained, UVs are usable and the model has no unintended noise or geometry defects.
- [ ] Build completed with a fresh output and its errors were checked.
- [ ] Animation and export checks listed in the asset task actually passed.

### Requires Manual Validation

- [ ] Compare against approved references in neutral light and at normal gameplay distance.
- [ ] Import into Studio; verify scale, facing, textures, joints and animation playback.
- [ ] Test camera readability, occlusion, collision and interaction in the real scene.
- [ ] Profile representative mob density on supported mobile and desktop devices.
- [ ] Confirm publication through the relevant main-based asset workflow if deployment was requested.

### Incomplete / Needs Work

Record missing species references, unresolved animal sizes, runtime rig/export decisions, actual performance budgets, unfinished geometry, failed poses and untested Studio integration here or in the asset task. Concept categories do not approve gameplay behavior. This guide documents how to build and assess the style; it does not certify that the modeled creature roster exists in the game.
