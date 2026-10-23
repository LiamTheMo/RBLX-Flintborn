# Flintborn — Visual and Modeling Style Guide

> **Status:** Approved art direction with production guidance  
> **Established:** 2026-10-23  
> **Scope:** Environment art, map composition, models, materials, lighting and visual readability  
> **Gameplay authority:** [GDD.md](GDD.md)

## 1. Purpose and approval boundary

Flintborn uses a **bright, cartoony, primitive, chunky low-poly 3D style**. The world should feel rugged, handmade and adventurous while remaining recognizably Roblox. Its strongest visual features are bold geometric trees, faceted stone, grassy terraces, warm dirt paths, blue water and simple timber-and-thatch construction.

This guide records the owner's visual selections and subsequent corrections. The owner selected **image 2 from the initial three-image exploration**, described as chunky low-poly, as the preferred style. The following outer-rim, inner-wilderness and crater-center examples were also accepted stylistically. The owner then requested **more water and large forest areas**, followed by the clarification that the map needs **a mix of water, forest, terrain, caves and other environments**.

The latest mixed-landscape concept demonstrates that composition: substantial woodland, open valley, river and lake, rocky elevations and clearly visible caves coexist within one connected landscape. That individual image is a composition study following the clarification; it has not received a separate final layout approval.

**Confirmed direction:** the style above, substantial water areas, large continuous forests and a varied, connected map. **Production guidance:** the modeling recipes, relative proportions, palette descriptions and review criteria below translate that direction into practical art decisions. They do not establish new gameplay mechanics, exact map dimensions, resource distributions, spawn rules or performance budgets.

**Relationship to the GDD's Open art fields:** This guide supersedes the Open status of the exact style bible, broad shape language and visual reference direction recorded in GDD §36.1 (Q57) and §36.5. Those subjects are now established by the owner selections recorded above. Exact production color swatches, texture specifications, asset budgets and final map layout remain Open. The GDD continues to govern gameplay; this clarification does not supersede its region, encounter, resource or progression rules.

Concept images establish visual intent, not surveyed geometry. Do not copy accidental bridges, resource locations, stairs, building placements or camera angles into gameplay requirements. This document is self-contained; it does not depend on temporary conversation image paths.

## 2. Core visual identity

The world should look assembled from strong, understandable forms. A player should recognize a tree, cave, ore deposit, shelter or route before noticing its surface detail. Large shapes establish the environment; secondary shapes describe construction and natural variation; small details provide selective finishing.

Primitive means stone, wood, fiber, rope, hide, bone and hand-worked metal. It should read as a living survival world where players gather, craft and build. Avoid turning every area into an elaborate fantasy ruin or an ornamental showcase.

Cartoony means exaggerated proportions and readable silhouettes, with deliberate color separation and simplified materials. It does not require everything to be spherical, inflated or glossy. Low-poly means visible, purposeful facets and economical geometry, rather than unfinished models or uniformly sharp cubes.

The intended balance is:

| Visual quality | Direction |
| --- | --- |
| Overall mood | Bright, adventurous, natural and primitive |
| Shape language | Chunky, geometric, slightly irregular and easy to read |
| Natural surfaces | Broad color areas, visible facets, restrained texture |
| Construction | Thick timber, simple joints, visible lashings and practical forms |
| Scale | A playable world sized around Roblox characters |
| Detail | Concentrated at useful landmarks and interactions |
| Danger | Communicated through geography, encounters and signals without abandoning the style |

Avoid photorealistic survival art, gritty military styling, realistic leaf cards, microscopic surface noise, polished plastic toy scenery, soft clay-like modeling and painterly scenery that cannot be reproduced consistently in-game.

## 3. Map composition: a connected mixture

The Shattered Crater remains the seamless island with concentric risk regions described in the GDD. Visual variety should support that structure. A region can include woodland, water, meadow and rocky terrain; risk regions do not need to become single-material bands with abrupt circular borders.

**The essential correction is balance.** Adding water and forest must preserve open land, elevation changes, caves, exploration routes and room for building and combat. Avoid replacing the earlier rocky landscape with an almost entirely flooded or wooded map.

### Large forests

Create substantial continuous woodland that players can enter and travel through. From an overlook, forests should form recognizable masses across hillsides or valleys, rather than scattered decorative trees surrounding otherwise empty terrain.

Within those masses, vary density. Include clearings, visible forest edges, deeper wooded interiors, routes between trunks, occasional rock formations and transitions toward shore or grassland. A large forest should feel extensive at ground level as well as from above.

### Water network

Include meaningful water areas: rivers, lakes, pools, shorelines and waterfalls where the terrain supports them. Some views should show broad open water; others should encounter smaller channels within a larger land route.

Connect water to the terrain. Rivers descend through valleys, waterfalls have an upstream source and a receiving basin, and lakes sit within believable surrounding slopes. Keep adequate connected dry land between water features. Small islands or peninsulas can add variety without making the whole inland map an archipelago.

These are visual requirements. Swimming, boats, fishing, underwater gameplay and water hazards require their own gameplay decisions.

### Open terrain and highlands

Retain broad meadows, buildable-looking clearings, rolling slopes, rocky shelves, ridges and recognizable valleys. Open terrain gives the eye relief between forests and cliffs and provides space for the activities defined in the GDD.

Use height changes selectively. Some land should be broad and gently sloped; some should be steep and distinctive. Avoid reducing the entire island to small disconnected cliff platforms linked by repetitive bridges or stairs.

### Caves

Make cave entrances clear enough to recognize from their approach. Integrate them into actual rock masses, cliff bases, forest slopes or highland faces. A dark opening with a thick, irregular stone surround should read as a traversable space rather than a black decal.

Use paths, exposed stone, changes in vegetation or a restrained light source to guide discovery. Not every cave needs a torch, timber frame or mining structure. Cave placement and contents must follow approved map and resource design.

### Natural transitions

Use transitional terrain to connect these features: forest thinning into meadow, gravel near a river bend, exposed stone beneath a grassy slope, or a cave approach opening from woodland. Avoid rigidly partitioning the map into equal visual compartments.

A useful overview should communicate several destinations at once: a forest to explore, water to navigate around, high ground to approach and a cave to investigate. Individual locations can emphasize one feature while remaining part of this mixed world.

## 4. Terrain and rock modeling

Build terrain around large primary masses. Establish the valley floor, hillside, ridge and cliff silhouette before adding rocks or grass. Broad horizontal shelves and angular cliff faces are characteristic, but their widths, heights and directions should vary.

Grass caps should sit clearly above exposed brown soil or gray stone. Avoid making every terrace the same thickness or every cliff a perfectly vertical wall. Combine stepped rock with natural earth ramps and gentle banks.

Rock models should use a few substantial irregular planes. Boulders need weight, a stable base and distinct silhouettes. Favor angular, weathered-looking forms over smooth spheres, needle-like shards everywhere or detailed scans. Break long cliff walls with larger ledges and changes in direction before adding small surface pieces.

Use a reusable family of rock sizes and silhouettes. Rotate and scale variants deliberately, checking for obvious repetition and unnatural stretching. Small stones belong near meaningful formations or shores; they should not cover every walkable surface.

Visual ledges, ramps and paths must agree with actual collision. A slope that appears passable should be evaluated with the game's movement rules before final dressing.

## 5. Trees, foliage and forest construction

### Broadleaf trees

Use stout trunks supporting chunky polygonal canopy masses. Build the crown from several large faceted volumes with purposeful overlap and an irregular outline. Keep the trunk legible beneath the foliage; a few thick branches are more useful than many fine branches.

Vary crown width, trunk lean, height and canopy grouping within a consistent family. Trees should look related without appearing cloned in rows. Use simplified brown trunks and controlled green variation rather than realistic bark and individual leaves.

### Pines

Use a clear tapered silhouette with several broad triangular or conical foliage tiers. Each tier should feel substantial and geometric. Let the trunk remain visible near the base, and vary tier width and spacing between approved variants.

Avoid thin realistic needles, dense branch cards and excessive layers. Pines and broadleaf trees must share the same level of simplification.

### Forest floor

Use shrubs, grass tufts, roots, fallen timber and occasional rocks selectively. The forest should feel inhabited and natural while preserving readable ground and interaction space.

Concentrate ground cover around edges and nonessential gaps. Keep important routes, gathering targets and combat sightlines legible. Bushes should use the same faceted foliage language as trees.

### Forest scale

Show depth through overlapping trunks and several layers of canopy, rather than simply multiplying tiny trees in the distance. Test the actual forest interior: canopy density must not produce a solid wall at avatar height.

Use clearings and variations in tree spacing to support play. Landmark trees can be larger or have distinctive branching, but should remain part of the established style.

## 6. Water, banks and waterfalls

Water should read as clean blue, with lighter blue or turquoise near shallow edges where appropriate. Its broad color and contrast with green grass help orientation. Keep reflections, foam and ripples restrained enough to suit the simple surrounding geometry.

Banks should alternate naturally between sandy or gravelly shore, grassy slope and exposed rock. Do not outline every water body with an identical strip of sand.

Waterfalls should have a readable flow direction and a clear top and bottom. A small amount of spray and foam can suggest motion. Avoid filling the scene with particles or using effects to conceal poorly connected terrain.

Bridges should span plausible gaps and visibly meet the banks. Use thick logs, simple planks and rope lashings. Narrow crossings may suit small timber bridges; large rivers should not automatically receive impossibly long, thin log spans. Crossing locations and alternatives require map testing.

## 7. Caves and underground forms

Carry the surface rock language indoors: large faceted walls, chunky supports and broad readable floor shapes. Avoid realistic noisy tunnel textures or indiscriminate spikes.

Use variation in ceiling height, bends and openings to create depth. Preserve enough contrast to distinguish floor, wall, entrance and interactable objects. Darkness can establish atmosphere while still allowing navigation on smaller screens.

If supports are appropriate, use thick rough timber and simple braces. If ore is present, build it into a recognizable rock body with a few clear mineral shapes or seams. Decorative crystals and colored light are not a default cave treatment.

A cave concept should clarify how a player enters and moves through it. A visually convincing opening alone does not prove an underground layout exists or is playable.

## 8. Primitive structures and props

Shelters should use simple silhouettes: stout timber posts, a visible frame, an uncomplicated thatch or hide roof, and a modest usable interior. Palisades use thick upright logs with rough points and selected horizontal supports.

Show construction through a small number of readable details: rope at a joint, a large brace, overlapping roof bundles or a hide stretched across a frame. Keep detail subordinate to the building's silhouette.

Thatch should read as broad layered bundles or shaped roof sections. Avoid modeling every straw. Timber should have slight irregularity and simplified end grain or cut faces, without realistic bark displacement or dense wood texture.

Campfires use a small arrangement of thick logs and chunky stones. Workbenches use thick legs and a straightforward surface, with a few recognizable tools. Storage, crafting stations and landmarks should be distinguishable by form before extra decoration.

Handmade does not mean structurally incoherent. Roofs need supports, platforms need visible connections and props need stable placement. Avoid floating accessories, unsupported walkways and clutter that prevents interaction.

Structures shown in concepts are visual examples; they do not add building recipes, station types or world POIs to the gameplay catalog.

## 9. Equipment and character consistency

Retain the blocky Roblox character language. Gear should fit that scale and remain readable against busy terrain.

Tools and weapons use slightly exaggerated functional forms: a clear stone axe head, substantial wooden handle, visible binding and a clean gripping area. Spears and bows should remain primitive and visually distinct. Metal progression can introduce stronger shapes and restrained metallic accents while retaining the same chunky construction language.

Armor should communicate material and silhouette without covering the avatar in tiny overlapping pieces. Hide, bone, wood, stone and hand-worked metal should look related to the environment's material treatment.

Follow current GDD equipment rules. This style guide does not introduce firearms, player shields, player magic or new equipment tiers. Rarity and encounter effects must remain consistent with gameplay signaling rather than making every item luminous.

## 10. Color, materials and surface detail

The approved reference uses a natural, lively palette:

| Material or feature | Color direction | Surface treatment |
| --- | --- | --- |
| Grass | Bright warm green with controlled darker variation | Broad surfaces and selective simple tufts |
| Broadleaf canopy | Mid green through yellow-green | Faceted masses with limited color variation |
| Pine canopy | Slightly cooler or deeper green | Clear layered geometric planes |
| Dirt | Warm ochre, orange-brown and earthy brown | Simple paths with sparse stones |
| Rock | Neutral to cool gray | Large readable facets |
| Timber | Warm medium and dark brown | Restrained grain and broad cut faces |
| Thatch and fiber | Straw gold, tan and muted ochre | Large overlapping bundles |
| Hide | Tan, cream and earthy brown | Matte simplified shapes |
| Water | Clear blue with lighter shallow edges | Controlled highlights and light foam |
| Fire | Warm yellow-orange | Local accent with limited particles |

These are palette relationships, not locked RGB values. Establish final reusable swatches in an art pass and check them in the actual game lighting before treating them as production color constants.

Favor matte surfaces and broad variation. Use detail where it explains material or function. Avoid high-frequency grunge, realistic scanned textures, deep shiny bevels on every object and different texture scales across neighboring assets.

Reserve strong emissive color for approved signals and special objects. Ordinary rocks, plants and buildings should not compete with extraction indicators, rare loot or encounter cues.

## 11. Lighting and atmosphere

The baseline presentation is bright daylight with clear sky, readable shadows and enough ambient light to separate shaded surfaces. The scene should remain colorful without washing out paths, water edges or character silhouettes.

Use distance haze gently to separate far terrain. Avoid heavy bloom, extreme depth of field, crushed shadows and cinematic fog that obscures navigation. Local firelight can warm a camp or cave entrance without recoloring an entire region.

Higher-risk areas may feel harsher through exposed rock, scale, sparse vegetation and encounter design while retaining the same art style. The GDD's central caldera and open boss-space requirements still apply; decorative trees, large cover rocks or extra water must not silently alter those combat rules.

Concept sunlight and shadow quality are targets for mood, not guarantees about the final Roblox renderer. Validate actual lighting on supported devices.

## 12. Scale, navigation and gameplay readability

Judge assets at normal player-camera distance, not only in close-up renders. The adjustable camera remains governed by the GDD; the elevated concept viewpoint is a presentation choice.

A terrain pass should preserve:

- Recognizable paths, banks, entrances and routes between elevations.
- Open areas suitable for approved building and combat activities.
- Enough spacing for characters around trunks, rocks and props.
- Clear distinction between decorative foliage and interactable nodes.
- Visibility of projectiles, enemies, rare loot and extraction signals.
- Landmark silhouettes that help orientation through forest and varied terrain.
- Consistent visual and physical boundaries at cliffs, banks and cave mouths.

Forest density should be compatible with exploration and PvP. Grass and shrubs should not bury every object. Avoid using visual cues to imply safety: a friendly-looking camp or outer-rim meadow is not automatically a PvP safe zone.

Terrain art must preserve the GDD's extraction protection, boss-area constraints, spawn validation and building restrictions. Validate all gameplay dimensions against actual character movement and implemented rules.

## 13. Production guidance for Roblox assets

Build a coherent kit of terrain masses, rock variants, broadleaf trees, pines, shrubs, primitive construction pieces and cave sections before producing many bespoke decorations. Reuse assets with controlled variation, keeping proportions and materials consistent.

Use geometry where it changes silhouette or explains a function. Evaluate whether an unseen face, tiny rope strand or complicated internal joint adds value at gameplay distance. Dense forests require particular attention to geometry, transparency, shadows, collision and instance count.

Keep collision simple and intentional. Decorative branches and roof fibers should not unexpectedly snag movement. Ensure cave and building openings fit the intended character and camera.

Preserve category organization described in [src/assets/README.md](src/assets/README.md). Models belong under the existing model structure; world layouts belong in `src/maps`. Concept renders are reference art, not runtime models or collision assets.

The repository's automated release publishes scripts; non-script art assets require the existing Studio asset workflow. Adding this document does not apply a visual overhaul to the live game.

Exact triangle, texture, instance, memory and draw-call limits remain to be established through device profiling. Do not treat a guessed per-tree budget or a concept image's apparent tree count as an approved limit.

## 14. Reusable visual brief

Use this brief when commissioning a new asset or generating another scene, followed by the specific subject and gameplay constraints:

> Flintborn is a bright cartoony primitive Roblox survival world with chunky low-poly geometry. Use stout trees with faceted broadleaf crowns and layered triangular pines, angular gray rock formations, grassy terraces, warm earthy paths, clear blue water and simple timber, rope, hide and thatch construction. Keep silhouettes bold, materials mostly matte and surface detail restrained. The island combines substantial continuous forests, rivers and lakes, open grasslands, rocky highlands and discoverable caves through natural connected terrain. Individual scenes can emphasize one area without changing the shared style. Maintain Roblox character scale, readable routes and space for gameplay. Avoid photorealism, gritty military art, soft clay modeling, modern objects, excessive microdetail and decorative effects that conceal important gameplay.

For a map overview, request a balanced landscape and specify which features must be visible. For a forest interior, cave or individual tool, retain the shared style without forcing every landscape feature into the image.

## 15. Art review checklist

### Completed / Passed

Use this classification only when the reviewed asset or scene has actually been inspected.

- [ ] Chunky primitive low-poly style matches the approved reference direction.
- [ ] Silhouette, proportions and material treatment fit neighboring assets.
- [ ] The overall map includes substantial water, large forests, open terrain, elevation changes and caves.
- [ ] Environmental transitions feel connected and natural.
- [ ] Gameplay routes and important interactions remain visually readable.
- [ ] No unapproved mechanics or map rules have been inferred from concept art.

### Requires Manual Validation

- [ ] Inspect at normal gameplay camera distance and multiple zoom settings.
- [ ] Walk forest interiors, cave entrances, shorelines, ramps and bridges.
- [ ] Check actual collision, camera obstruction and interaction access.
- [ ] Test projectile, enemy, loot and extraction-signal visibility.
- [ ] Compare lit and shaded areas on desktop and mobile.
- [ ] Profile representative dense woodland and water-heavy views on supported hardware.
- [ ] Verify Studio asset integration and publication through the established workflow.

### Incomplete / Needs Work

Record unresolved production decisions here or in the relevant task rather than marking the art pass finished:

- Final map layout, cave networks, route lengths and water coverage.
- Final color swatches and reusable material setup.
- Asset kit inventory and finished production models.
- Device-tested asset and scene budgets.
- Implementation and manual validation of the visual overhaul.

The approved direction is established. Those production decisions remain separate work.
