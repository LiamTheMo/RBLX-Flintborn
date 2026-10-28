# World kit rebuild: model progress

Tracks the rebuild of every world-kit model in `art/blender/assets/kit/FlintbornWorldKit.blend` against its master reference sheet in `art/reference/kit/`. Update this file after every model. It is the hand-over point between sessions.

- **Branch:** `feat/world-kit-rebuild` (from `v0.18`).
- **Sheets:** 34 (W01–W16, R01–R08, V01–V10). Each sheet has 4 rows; each row is one **model** (136 in total).
- **A model** is the whole row: the assembled hero, every exploded part, every variation and, for resources, the depleted state and drops. Each is its own mesh asset tagged with `kit_role`.
- **Builders:** durable per-sheet MCP modules in `art/blender/kit/mcp/<sheet>.py` (shared tools in `kit_mcp.py`). Load with `sys.path.insert(0, ".../art/blender/kit/mcp"); import kit_mcp; kit_mcp.install()`.
- **Renders:** `art/blender/renders/kit/<SHEET>/<module>_compare.png` (master row on top, ours underneath); spec and goals in `<module>_goals.md` beside it.

## How each model is done

1. **Study** the reference row: silhouette and proportions, parts, sampled colours (`kit_mcp.sample`), surface detail, effects, every view. Written to `<module>_goals.md`.
2. **Model** the exploded parts one by one, then assemble the hero and variants from the same part builders (Blender MCP, main session).
3. **Optimise:** triangle counts against the budgets, no hidden faces, bottom-centre origin (`kit_mcp.check`).
4. **UV:** not hand-unwrapped. The exporter writes palette UVs (key × Tint level into `palette.png`) and box-projected water UVs; see "Conflicts" below.
5. **Colour and texture:** palette keys measured from the master and calibrated in the kit studio (`kit_mcp.calibrate`), with broad Tint texture and colour regions.
6. **Lighting:** emissive palette keys (exported as Neon parts) plus PointLight specs inside VFX sockets.
7. **VFX:** `VFX_<kind>` sockets carrying the Roblox ParticleEmitter / Beam / PointLight spec; textures in `art/vfx/textures/`.
8. **Verify:** a fresh verifier agent that did no work on the model compares the renders with the master and checks the technical numbers, returning pass or fail with an itemised list. Fix and re-verify with a new verifier until it passes.
9. **Export** the sheet once all four models pass: `BLENDER_ARGS="art/blender/assets/kit/FlintbornWorldKit.blend --sheet <SHEET>" art/blender/run.sh scripts/export_kit_roblox.py art/roblox/kit/<SHEET>/manifest.json`.

## Conflicts between the task brief and WorldModeling.md / repo contracts

WorldModeling.md and the repo contracts win; each is reported here.

1. **PBR maps (Color/Normal/Metalness/Roughness, SurfaceAppearance).** WorldModeling.md §5.2 bans noise textures, bump maps and realistic textures in the baseline style, and the repo's export contract is one multi-material mesh per asset, coloured through the shared `palette.png` and a `Tint` attribute. So models get no per-asset PBR maps. Colour comes from measured palette keys plus Tint texture, roughness and metalness live on the palette keys, and water uses the exporter's tiled 512×512 texture.
2. **UV unwrapping with consistent texel density.** It doesn't apply in this pipeline: UVs index the palette texture and are written by `export_kit_roblox.py`. No hand-made UV islands exist to pack.
3. **One subagent per discipline driving Blender.** CLAUDE.md says only the main session drives the open Blender GUI through the MCP. So modelling, optimisation, colour, lighting and VFX run in the main session. Independent subagents do the audits and every verification.
4. **"Matches the reference exactly / no visible differences".** WorldModeling.md §1.1 says the sheets are visual targets, not exact engineering drawings, and their views can disagree. Verifiers judge resemblance and list every discrepancy. Minor view-to-view inconsistencies of the concept art are resolved coherently and noted.
5. **Triangle budgets.** WorldModeling.md §16 gives prototype envelopes, not limits. The enforced budgets are the repo's (BUILDER_GUIDE.md: hero/variant 3000, part 1500, depleted 2000, drop 300, large terrain/trees/buildings up to 8000; Roblox hard limit 20,000 per mesh).
6. **Git LFS.** The repo has no LFS set-up (`.gitattributes` absent), so nothing is moved to LFS. Large binaries (renders, exports) are committed sparingly.

## Status key

`⬜ todo` · `🔨 in progress` · `✅ passed` · `🟡 needs manual validation` · `❌ incomplete`

State from the initial audit (2026-10-27, against the existing compare renders): **rough**, **partial** or **mostly-done**.

## Models

| Sheet | Model | Audit state | Main problems at audit | Status | Tris (hero) | Verifier | Manual review |
| --- | --- | --- | --- | --- | --- | --- | --- |
| W01 | Boulder | mostly-done | moss cap a flat decal, not leafy lumps; base plants dark/spiky, few pebbles; exploded moss cap thin; rock slightly dark | ✅ | 3812 (parts 208/288; variants 3477/3319/3232) | PASS 8/10 (round 5) | palette `w01_*` keys only, no textures beyond palette.png; no VFX; check brightness of calibrated moss/herb greens in Studio |
| W01 | RockSpire | partial | spire slender, few facets; foot collar thin; moss streak not clumps; foliage sparse | ✅ | 5633 (parts 180/588; variants 2945/3546/3226) | PASS 7.5/10 (round 5) | palette `w01_*` only; no VFX; minors: clover clumps chunkier than master rosettes, spire moss streak |
| W01 | RockCluster | mostly-done | moss small/flat/pale; foliage sparse; top view cramped | ✅ | 5959 (parts 345/745/405; variants 4110/4028/3730) | PASS 7.5/10 (round 3) | palette `w01_*` only; no VFX; minors: Rock C egg-like, moss caps tuft-like |
| W01 | PebbleScatter | partial | slab dominant; exploded lacks 5 stone types; foliage few; variants barely differ | ⬜ | | | |
| W02 | CliffWall | partial | face smooth, missing chunky spires; grass top flat, no lip; corner variants unclear; too purple | ⬜ | | | |
| W02 | TerracedLedge | partial | rock hidden under flat lime slabs; low smooth cliffs; ramp end flat; wide/shallow identical | ⬜ | | | |
| W02 | NaturalRamp | partial | thin strip on thin slab (ref thick stepped wedge); flat side wall; dotted borders | ⬜ | | | |
| W02 | NaturalArch | partial | narrow low opening, flat top slab; flat side; narrow pillars | ⬜ | | | |
| W03 | WaterfallModule | partial | cliff smooth/pale; thin curtain, little foam/splash; flat pool; two-step not tiered | ⬜ | | | |
| W03 | RiverbankChunk | partial | low flat cliff; sand thin; foam swirls; bends unclear | ⬜ | | | |
| W03 | ShoreIslet | mostly-done | stack plain; no foreground boulders; foam over-stylised; variants weak | ⬜ | | | |
| W03 | StreambedPatch | mostly-done | smooth uniform bank rocks; no flow strips; no pebbles; fork a plain T | ⬜ | | | |
| W04 | ClassicPine | partial | 3 fat tiers (ref 4); flat green, no lime tips; trunk hidden; variants identical | ⬜ | | | |
| W04 | YoungFir | partial | fat dark tiers; trunk hidden; variants similar | ⬜ | | | |
| W04 | Sapling | partial | scaled-down pine (ref 2 tiers on thin trunk); sand disc | ⬜ | | | |
| W04 | OldPine | rough | blob canopy (ref angular clumps on forked limbs); cone trunk | ⬜ | | | |
| W05 | LogAndStump | partial | clean cylinder, flat cap (ref rough bark, cracks); flat moss; stub a block | ⬜ | | | |
| W05 | AncientTree | rough | squat cone trunk; flat pale crown, no vines; hollow variant not hollow | ⬜ | | | |
| W05 | OakTree | rough | flat blob crown (ref 5 clumps on twisting limbs); thin straight trunk; too pale | ⬜ | | | |
| W05 | DeadTree | partial | thick straight branches; block trunk; variants similar | ⬜ | | | |
| W06 | LowBush | partial | flat saturated blob; few flowers; variants off | ⬜ | | | |
| W06 | MossAndIvy | partial | smooth blocks; neon moss; sparse ivy | ⬜ | | | |
| W06 | FernAndBroadleaf | rough | flat star of wide leaves (ref arching fronds) | ⬜ | | | |
| W06 | HangingVine | mostly-done | thin vine, few large flat leaves; plain pad | ⬜ | | | |
| W07 | MeadowDaisy | mostly-done | thin pointed petals, tiny centre; flat leaves | ⬜ | | | |
| W07 | Wildflowers | mostly-done | flat pink star, dark bud; thin blue star; straight stems | ⬜ | | | |
| W07 | GroundScatter | partial | twig planks dominate (ref leaves + pinecone); flat pinecone | ⬜ | | | |
| W07 | GrassTuft | partial | few flat paddle blades (ref 5+ tall pointed) | ⬜ | | | |
| W08 | Footbridge | partial | plank orientation; no X brace; flat orange; arched variant flat | ⬜ | | | |
| W08 | Dock | partial | square posts (ref round with rope ties); flat orange; boxy heads | ⬜ | | | |
| W08 | Boardwalk | partial | plank-fence railing; ramp not stairs; corner not an L | ⬜ | | | |
| W08 | RopeCrossing | mostly-done | round anchor stones (ref blocks); slim posts; shallow sag | ⬜ | | | |
| W09 | StonePath | partial | pale flat pavers on brown slab (ref chunky with grass gaps) | ⬜ | | | |
| W09 | StoneStair | partial | plain cubes on a ramp (ref chunky treads, side walls, moss) | ⬜ | | | |
| W09 | TimberFence | mostly-done | plain flat orange; thin rope joints; flat caps | ⬜ | | | |
| W09 | WayfindingPost | partial | thin pole, flat boards (ref thick carved post) | ⬜ | | | |
| W10 | AFrameTent | partial | thin poles, no lashing; flat canvas, no doorway; variants identical | ⬜ | | | |
| W10 | CampAwning | partial | flat sheet (ref draped canvas on 4 posts); sparse clutter; no lantern glow | ⬜ | | | |
| W10 | RuinLeanTo | partial | regular brick wall (ref broken ruin, moss/ivy); flat canvas | ⬜ | | | |
| W10 | TimberHut | partial | flat plank walls, no framing/window/door frame; plain roof | ⬜ | | | |
| W11 | DailyItems | partial | thin square rack (ref A-frame, bracing); blocky items | ⬜ | | | |
| W11 | FireAndLight | partial | pale uniform stones; weak flames, no logs; thin tripod; flat brazier | ⬜ | | | |
| W11 | Storage | partial | flat crate boards, no corner posts; indistinct staves | ⬜ | | | |
| W11 | TableAndSeating | partial | thin top, straight legs (ref trestle); thin benches | ⬜ | | | |
| W12 | Barricade | partial | thin spikes (ref thick lashed uprights, braces) | ⬜ | | | |
| W12 | DoubleGate | partial | one flat slab, no leaves/hinges/latch | ⬜ | | | |
| W12 | PalisadeWall | partial | uniform thin logs (ref uneven thick trunks); few lashings | ⬜ | | | |
| W12 | WallWalk | rough | solid box (ref open walkway on posts with braces, rails) | ⬜ | | | |
| W13 | FortWorkshop | partial | thin posts, flat canopy, unreadable interior; variants identical | ⬜ | | | |
| W13 | GuardLodge | partial | flat walls, no door/window/posts/stone base | ⬜ | | | |
| W13 | LookoutPlatform | mostly-done | ladder-like stairs; thin railing; small base stones | ⬜ | | | |
| W13 | Watchtower | partial | too tall/thin (ref stocky); sparse bracing; plain roof | ⬜ | | | |
| W14 | CaveColumn | partial | uniform pink-grey, few facets; broken variant a smooth pile | ⬜ | | | |
| W14 | CaveEntranceRing | partial | thin rock hoop (ref thick shell, deep opening); variants same | ⬜ | | | |
| W14 | CaveLedge | rough | pillars + flat slab (ref layered overhang) | ⬜ | | | |
| W14 | TunnelModule | partial | dome with small hole (ref long tunnel); bend/junction unclear | ⬜ | | | |
| W15 | GantryRopeLift | partial | massive beams; small cargo; variants lack basket/scaffold | ⬜ | | | |
| W15 | MineSupport | partial | thin boards; no dark tunnel interior; lanterns no glow | ⬜ | | | |
| W15 | MineTrack | mostly-done | plain end buffer; plain rails; big rocks crowd track | ⬜ | | | |
| W15 | Minecart | partial | tiny wheels; flat bands; extra rails/rocks in hero | ⬜ | | | |
| W16 | BlockWall | partial | thin repetitive blocks; flat ivy; flat tan | ⬜ | | | |
| W16 | RuinColumn | partial | thin square post (ref octagonal segmented shaft); no rubble | ⬜ | | | |
| W16 | CourtyardFloor | partial | flat squares, no gaps/cracks/moss; thin steps | ⬜ | | | |
| W16 | StoneArch | partial | thin/asymmetric; keystone unclear; variants same | ⬜ | | | |
| R01 | CoalNode | partial | smooth pillar shards (ref big faceted chunks); no sheen | ⬜ | | | |
| R01 | CopperNode | partial | tall smooth dome host (ref wide boulder); flat inserts | ⬜ | | | |
| R01 | FlintNode | partial | smooth dome with painted-on flint triangles | ⬜ | | | |
| R01 | StoneNode | mostly-done | smooth dome, few facets; tiny support rocks; flat pink | ⬜ | | | |
| R02 | IronNode | partial | smooth dome host; oversized flat vein plates; drops slabs | ⬜ | | | |
| R02 | GoldNode | partial | spherical host; generic small nuggets | ⬜ | | | |
| R02 | SulfurNode | partial | stacked discs (ref faceted layered slab); few chunks | ⬜ | | | |
| R02 | ObsidianNode | partial | smooth blobs (ref sharp shards with blue edges) | ⬜ | | | |
| R03 | Quartz | partial | thin spindly crystals (ref fat hex prisms); 3 not 5 | ⬜ | | | |
| R03 | Azurite | partial | rounded crystals; base dome in front; not splayed | ⬜ | | | |
| R03 | Amethyst | partial | boxy block shell with seams; few short crystals | ⬜ | | | |
| R03 | Amber | partial | smooth egg nodule; thin plank wood base | ⬜ | | | |
| R04 | IronMeteor | partial | single smooth dome (ref split faceted rocks); decal cracks, no glow | ⬜ | | | |
| R04 | EmberMeteor | partial | smooth orange blob core; crude spires; no glow bleed | ⬜ | | | |
| R04 | Stormglass | partial | blocky stepped rods; compact Y; no glass sheen | ⬜ | | | |
| R04 | Starstone | partial | two smooth wedges (ref faceted boulders); narrow core; stray dust VFX | ⬜ | | | |
| R05 | BerryShrub | mostly-done | small round clumps; thin Y trunk; oversized berry drop | ⬜ | | | |
| R05 | HealingHerb | partial | flat star leaves; short stalk; dark box root plug | ⬜ | | | |
| R05 | FiberShrub | partial | thin dark spiky leaves; small tucked fiber tufts | ⬜ | | | |
| R05 | ThornShrub | mostly-done | dense foliage, few limbs; long thin thorns | ⬜ | | | |
| R06 | SoftwoodLog | partial | boxy segmented tube, weak end rings; flat star sprouts | ⬜ | | | |
| R06 | HardwoodStump | partial | smooth cylinder (ref chunky buttress roots); flat cut face | ⬜ | | | |
| R06 | ResinNode | partial | straight log on plinth (ref curved forked branch on mound) | ⬜ | | | |
| R06 | RootCluster | partial | thin straight finger roots (ref big arching roots) | ⬜ | | | |
| R07 | ClayDeposit | partial | rounded blobs (ref flat-topped faceted lobes); smooth dome base | ⬜ | | | |
| R07 | ReedPatch | mostly-done | thin dark blades; small seed heads | ⬜ | | | |
| R07 | CaveMoss | partial | pillowy saturated moss; flat slab base | ⬜ | | | |
| R07 | CaveMushroom | mostly-done | no gill ring; slim stalks; pale flat base | ⬜ | | | |
| R08 | Emberbloom | mostly-done | short smooth pod; no ember glow/sparks; thin petals | ⬜ | | | |
| R08 | Mooncap | partial | small flat caps, oversized spots; thin stem; no spot glow | ⬜ | | | |
| R08 | AncientRoot | partial | blocky plank arch (ref twisting roots); smooth egg sapstone | ⬜ | | | |
| R08 | FrostShrub | mostly-done | short thick stem, few forks; big ice icosahedra | ⬜ | | | |
| V01 | CloverPatch | partial | few large flat leaves (ref dense mound of 3-leaf clusters); small flower heads | ⬜ | | | |
| V01 | FieldSedge | partial | few wide blades in a wedge (ref open fan); thin seed spikes | ⬜ | | | |
| V01 | BluegrassClump | partial | stiff straight spikes (ref arching folded blades); 2 small seedheads | ⬜ | | | |
| V01 | DandelionRosette | partial | smooth wedge leaves (ref deeply toothed); flat flower; plain puff | ⬜ | | | |
| V02 | RaspberryBush | partial | 3 thin sticks, sparse; no 3-leaf clusters; berries clumped | ⬜ | | | |
| V02 | ElderberryShrub | partial | flat umbrella of sheet leaves; one small berry clump | ⬜ | | | |
| V02 | HazelShrub | rough | hidden tiny nuts, no husks; oversized exploded nut | ⬜ | | | |
| V02 | RosehipScrub | partial | no thorns; sparse leaves; flat fan; oversized exploded hip | ⬜ | | | |
| V03 | BrackenFern | partial | round blob leaflets on stiff stalk (ref triangular fronds) | ⬜ | | | |
| V03 | StrapFern | partial | narrow upright V of 5 leaves (ref broad low rosette) | ⬜ | | | |
| V03 | HeartleafCreeper | partial | thin short vine, few blocky leaves | ⬜ | | | |
| V03 | TrumpetVine | partial | pasted-on flowers; leaves hide vine; variants alike | ⬜ | | | |
| V04 | CattailClump | mostly-done | thin seed heads; stiff spiky leaves; thin stems | ⬜ | | | |
| V04 | BulrushFan | partial | loose berry-like seed clusters; low flat fan | ⬜ | | | |
| V04 | WaterLily | partial | flat pads; blobby flower | ⬜ | | | |
| V04 | Pondweed | mostly-done | small uniform leaves; straight thin stems | ⬜ | | | |
| V05 | ChestnutMushroom | partial | rough caps; hidden stalks; button variant a cone | ⬜ | | | |
| V05 | AmberShelfFungus | partial | smooth log support; thin flat shelves | ⬜ | | | |
| V05 | Puffball | mostly-done | plain white spheres; no open pore | ⬜ | | | |
| V05 | CaveTrumpet | partial | flat plate funnels; straight tall stems; floating second trumpet | ⬜ | | | |
| V06 | Birch | partial | thin trunk, little forking; round blob clumps; tiny bark patches | ⬜ | | | |
| V06 | Willow | mostly-done | smooth thin trunk; stiff shard leaf curtains; narrow canopy | ⬜ | | | |
| V06 | Rowan | mostly-done | thin straight trunk; berries off the canopy edge | ⬜ | | | |
| V06 | Juniper | partial | short thin trunk hidden; messy spiky foliage; few berries | ⬜ | | | |
| V07 | Heather | partial | pink blobs on top (ref hanging bells); needle tufts | ⬜ | | | |
| V07 | AlpineCushion | partial | flat spiky dome; flush flowers | ⬜ | | | |
| V07 | DryTussock | partial | straight stiff blades (ref broad curled); small seed heads | ⬜ | | | |
| V07 | ThornScrub | mostly-done | spindly branches; small thorn specks | ⬜ | | | |
| V08 | FlaxPatch | partial | oversized pods on long stems; spiky leaves | ⬜ | | | |
| V08 | Silkleaf | partial | pale thin flat leaves; spiky thin tuft | ⬜ | | | |
| V08 | Redroot | partial | flat petal-like roots; floating buds | ⬜ | | | |
| V08 | SunpodShrub | partial | yellow blobs, no four-point husks; flat canopy | ⬜ | | | |
| V09 | SunburstBloom | partial | flat thin petals; spiky leaves; seed-removed not a cup | ⬜ | | | |
| V09 | MoonveilOrchid | partial | inner bell hidden; pale thin leaves; thin stalk; no glow | ⬜ | | | |
| V09 | Stormreed | partial | weak zigzag thin stems; small heads; little leaf mass | ⬜ | | | |
| V09 | HeartpodBramble | partial | blob pods at the base, scrap husks; sealed/open alike | ⬜ | | | |
| V10 | GoldencrownTree | partial | smooth cone trunk; lumpy two-tone crown; hollow not hollow | ⬜ | | | |
| V10 | SilverbarkTree | partial | grey column trunk; saturated teal blobs; tiny pods | ⬜ | | | |
| V10 | ResinheartStump | partial | ring of narrow spikes (ref chunky stump); small resin | ⬜ | | | |
| V10 | GiantCoilFern | partial | thin coil; flat disc fan leaves; small pedestal | ⬜ | | | |


## Numbered references (001–172)

From 2026-10-27 the work follows the `roblox-blender-model` skill (`.claude/skills/roblox-blender-model/SKILL.md`) on the single-model production studies in `art/blender/assets/references/NNN.png` (`INDEX.md` there maps numbers to the original names). One model at a time, in number order.

- **Where:** `FlintbornWorldKit.blend`, collection `Kit/M<NNN> <Name>`, objects tagged `kit_sheet = M<NNN>`; builder `art/blender/kit/mcp/m<NNN>.py`, shared tools `kit_models.py`.
- **Renders:** `art/blender/renders/models/M<NNN>/` (one PNG per reference view + `M<NNN>_views.png`), spec `M<NNN>_spec.md`.
- **Export:** `BLENDER_ARGS="art/blender/assets/kit/FlintbornWorldKit.blend --sheet M<NNN>" art/blender/run.sh scripts/export_kit_roblox.py` → `art/roblox/kit/M<NNN>/`.
- **Budgets:** under 4000 tris for a full asset, under 1000 for an accessory/small prop or part (skill); buildings and large trees up to 8000 (repo README).
- **Cleanup:** every mesh closed and manifold, the hero a boolean union of its parts (one shell, no interior faces), no n-gons, Smart-UV `UVMap`, flat shading.

Skill vs design doc / repo (design doc wins, reported):
1. **FBX/OBJ export** → the repo's GLB + palette + manifest export (WorldModeling.md: FBX is not a drop-in substitute). Meshes still carry a Smart-UV layer so an FBX/OBJ export works.
2. **UVs**: the GLB exporter replaces authored UVs with palette-cell UVs; the authored `UVMap` is kept for other uses.
3. **Specialist subagents per discipline** → the stages run in the main session (CLAUDE.md: only the main session drives Blender); subagents verify, using read-only MCP inspection while the main session waits.
4. **One mesh per asset** (repo) vs separate part objects (reference sheets): both are delivered — the assembled hero plus each labelled part as its own asset.

| # | Model | Series | Status | Tris (hero; parts) | Verifier | Manual review |
| --- | --- | --- | --- | --- | --- | --- |
| 001 | Flintborn Stone Model Study | World & resources | ✅ | 820; parts 356 / 212 / 212 | PASS 8/10, re-verified PASS 7.5/10 after the node rework | minors: left support a bit large, right support hidden in the front view; check palette brightness in Studio |
| 002 | Flintborn Flint_ Low-Poly Construction Study | World & resources | ✅ | 744; parts 466 / 24 / 24 / 24 / 144 | FAIL 4/10 → PASS 6.5/10 (round 2) | minors: shell faceting more regular than the sheet, inserts gem-like rather than wedge shards; check in Studio |
| 003 | Flintborn Iron model study | World & resources | ✅ | 988; parts 216 / 42 / 36 | PASS 6.5/10 (round 1), re-verified PASS 6.5/10 after denser host + gem-top chunks | verifiers split on chunk thickness (thin inlay vs thick slab): decide in review; steel sheen and metallic look need a Studio check |
| 004 | Obsidian Flintborn Model Study | World & resources | ✅ | 1380; parts 34×3 / 40×2 / 484 | PASS 6.5 → FAIL 6 (base off the ground) → PASS 6.5/10 (round 3) | minors: crystals leaner than the sheet's chunky ones; small front crystals partly hidden; glassy specular to check in Studio |
| 005 | Quartz Flintborn low-poly model study | World & resources | ✅ | 1216; parts 34 / 34 / 440 | PASS 6.5/10 (round 1) | minors: crystals regular/slim vs the sheet's chunky tapered ones; rock mound smaller and sparser at the rear |
| 006 | Copper Flintborn Construction Study | World & resources | ✅ | 1030; parts 464 / 32×3 / 36×2 | PASS 6/10 (round 1) | minors: inserts rounder than the sheet's angular nuggets; teal patches hard-edged; copper sheen to check in Studio |
| 007 | Flintborn Coal model study | World & resources | ✅ | 834; parts 60×3 / 50×3 | PASS 7/10 (round 1) | minors: chunks a little columnar vs the sheet's rounder egg shapes |
| 008 | Azurite Flintborn model study | World & resources | ✅ | 908; parts 48×2 / 40 / 44 | PASS 6.5/10 (round 1) | minors: rocks render dark from behind (studio light) |
| 009 | Iron Meteor_ Flintborn model study | World & resources | ✅ | 2278 (8 shells); parts 58 / 40 / 44 | PASS 6/10 (round 1) | minors: even-width cracks; shell piece is a plain wedge |
| 010 | Flintborn Gold model study | World & resources | ✅ | 710; parts 112 / 24×3 / 36 | PASS 6/10 (round 1) | minors: no visible recessed seats; host a touch pink |
| 011 | Amethyst Flintborn model study | World & resources | ✅ | 1122; parts 456 / 232 / 24 | PASS 6/10 (round 1); reworked 3× from user review | minors: rock a touch pink; rim roll is quite regular |
| 012 | Amber Flintborn model study | World & resources | ⬜ | | | |
| 013 | Sulfur Flintborn exploded model study | World & resources | ⬜ | | | |
| 014 | Starstone Low-Poly Construction Study | World & resources | ⬜ | | | |
| 015 | Ember Meteor model study | World & resources | ⬜ | | | |
| 016 | Stormglass Flintborn asset study | World & resources | ⬜ | | | |
| 017 | Flintborn Berry Bush Study | World & resources | ⬜ | | | |
| 018 | Flintborn healing herb study | World & resources | ⬜ | | | |
| 019 | Flintborn Resin Node study | World & resources | ⬜ | | | |
| 020 | Flintborn hardwood stump study | World & resources | ⬜ | | | |
| 021 | Flintborn Root Cluster Study | World & resources | ⬜ | | | |
| 022 | Flintborn Fiber Shrub Model Study | World & resources | ⬜ | | | |
| 023 | Flintborn Clay Deposit Model Study | World & resources | ⬜ | | | |
| 024 | Flintborn Thorn Shrub Study | World & resources | ⬜ | | | |
| 025 | Emberbloom Flintborn Model Study | World & resources | ⬜ | | | |
| 026 | Flintborn softwood log study | World & resources | ⬜ | | | |
| 027 | Flintborn reed patch study | World & resources | ⬜ | | | |
| 028 | Flintborn frost shrub model study | World & resources | ⬜ | | | |
| 029 | Ancient root model study | World & resources | ⬜ | | | |
| 030 | Mooncap Flintborn model study | World & resources | ⬜ | | | |
| 031 | Cave Mushroom Construction Study | World & resources | ⬜ | | | |
| 032 | Shoreline corner | World & resources | ⬜ | | | |
| 033 | Flintborn cave moss model study | World & resources | ⬜ | | | |
| 034 | Flintborn streambed model study | World & resources | ⬜ | | | |
| 035 | Flintborn boulder model study | World & resources | ⬜ | | | |
| 036 | Flintborn rock cluster model study | World & resources | ⬜ | | | |
| 037 | Flintborn Waterfall Module Study | World & resources | ⬜ | | | |
| 038 | Pebble scatter model study | World & resources | ⬜ | | | |
| 039 | Flintborn rock spire model study | World & resources | ⬜ | | | |
| 040 | Flintborn Cliff Wall Construction Study | World & resources | ⬜ | | | |
| 041 | Flintborn Shore Shelf Model Study | World & resources | ⬜ | | | |
| 042 | Young Fir Model Study | World & resources | ⬜ | | | |
| 043 | Flintborn terraced ledge model study | World & resources | ⬜ | | | |
| 044 | Flintborn Natural Ramp Study | World & resources | ⬜ | | | |
| 045 | Flintborn pine sapling model study | World & resources | ⬜ | | | |
| 046 | Flintborn Natural Arch Model Study | World & resources | ⬜ | | | |
| 047 | Old Pine Flintborn model study | World & resources | ⬜ | | | |
| 048 | Flintborn dock model study | World & resources | ⬜ | | | |
| 049 | Classic Pine construction study | World & resources | ⬜ | | | |
| 050 | Flintborn timber bridge model study | World & resources | ⬜ | | | |
| 051 | Flintborn rope crossing model study | World & resources | ⬜ | | | |
| 052 | Flintborn Boardwalk model study | World & resources | ⬜ | | | |
| 053 | Flintborn dead tree asset study | World & resources | ⬜ | | | |
| 054 | Flintborn broadleaf tree study | World & resources | ⬜ | | | |
| 055 | Fallen Log Model Study | World & resources | ⬜ | | | |
| 056 | Moss and Ivy model study | World & resources | ⬜ | | | |
| 057 | Flintborn Ancient Tree Model Study | World & resources | ⬜ | | | |
| 058 | Flintborn Low Bush Study | World & resources | ⬜ | | | |
| 059 | Flintborn grass tuft model study | World & resources | ⬜ | | | |
| 060 | Broadleaf Fern Model Study | World & resources | ⬜ | | | |
| 061 | Flintborn Meadow Herb Study | World & resources | ⬜ | | | |
| 062 | Flintborn Ground Scatter Study | World & resources | ⬜ | | | |
| 063 | Flintborn hanging vine model study | World & resources | ⬜ | | | |
| 064 | Flintborn A-frame tent study | World & resources | ⬜ | | | |
| 065 | Flintborn wildflowers model study | World & resources | ⬜ | | | |
| 066 | Canvas Shelter Model Study | World & resources | ⬜ | | | |
| 067 | Flintborn Table and Seating Study | World & resources | ⬜ | | | |
| 068 | Flintborn timber hut model study | World & resources | ⬜ | | | |
| 069 | Flintborn palisade wall study | World & resources | ⬜ | | | |
| 070 | Ruined lean-to model study | World & resources | ⬜ | | | |
| 071 | Flintborn Supply Crate Model Study | World & resources | ⬜ | | | |
| 072 | Flintborn Timber Gate Model Study | World & resources | ⬜ | | | |
| 073 | Flintborn Barricade Model Study | World & resources | ⬜ | | | |
| 074 | Flintborn fire and light station | World & resources | ⬜ | | | |
| 075 | Flintborn wall walk study | World & resources | ⬜ | | | |
| 076 | Flintborn watchtower model study | World & resources | ⬜ | | | |
| 077 | Flintborn Hunt Workshop Model Study | World & resources | ⬜ | | | |
| 078 | Flintborn craft rack study | World & resources | ⬜ | | | |
| 079 | Flintborn cave entrance model study | World & resources | ⬜ | | | |
| 080 | Flintborn Guard Lodge Model Study | World & resources | ⬜ | | | |
| 081 | Flintborn mine support frame study | World & resources | ⬜ | | | |
| 082 | Flintborn tunnel module breakdown | World & resources | ⬜ | | | |
| 083 | Flintborn Lookout Platform Study | World & resources | ⬜ | | | |
| 084 | Flintborn Mine Track Model Study | World & resources | ⬜ | | | |
| 085 | Flintborn cave column study | World & resources | ⬜ | | | |
| 086 | Flintborn Minecart Model Study | World & resources | ⬜ | | | |
| 087 | Flintborn Cave Shelf Model Study | World & resources | ⬜ | | | |
| 088 | Flintborn gantry and ore lift | World & resources | ⬜ | | | |
| 089 | Flintborn ruin block wall study | World & resources | ⬜ | | | |
| 090 | Flintborn Ruin Arch Study | World & resources | ⬜ | | | |
| 091 | Flintborn ruin column study | World & resources | ⬜ | | | |
| 092 | Hollow stump construction study | World & resources | ⬜ | | | |
| 093 | Flintborn courtyard floor and steps | World & resources | ⬜ | | | |
| 094 | Snow Pine model study | World & resources | ⬜ | | | |
| 095 | Mosswick Stump Hall Model Study | World & resources | ⬜ | | | |
| 096 | Snowy Cliff and Boulder Study | World & resources | ⬜ | | | |
| 097 | Flintborn alpine ground patch study | World & resources | ⬜ | | | |
| 098 | Root Arch Walkway Model Study | World & resources | ⬜ | | | |
| 099 | Flintborn ice pool model study | World & resources | ⬜ | | | |
| 100 | Lake ruin tower model study | World & resources | ⬜ | | | |
| 101 | Flintborn Giant Redcap Mushroom Study | World & resources | ⬜ | | | |
| 102 | Ruin Camp Shelter Model Study | World & resources | ⬜ | | | |
| 103 | Clover patch model study | Vegetation | ⬜ | | | |
| 104 | Field sedge construction study | Vegetation | ⬜ | | | |
| 105 | Low-poly bluegrass clump study | Vegetation | ⬜ | | | |
| 106 | Elderberry shrub modeling study | Vegetation | ⬜ | | | |
| 107 | Raspberry Bush Model Study | Vegetation | ⬜ | | | |
| 108 | Dandelion rosette model study | Vegetation | ⬜ | | | |
| 109 | Hazel shrub low-poly model study | Vegetation | ⬜ | | | |
| 110 | Strap Fern model study | Vegetation | ⬜ | | | |
| 111 | Rosehip Scrub Model Study | Vegetation | ⬜ | | | |
| 112 | Trumpet Vine Model Study | Vegetation | ⬜ | | | |
| 113 | Heartleaf Creeper model study | Vegetation | ⬜ | | | |
| 114 | Bracken fern 3D model study | Vegetation | ⬜ | | | |
| 115 | Bulrush Fan model study | Vegetation | ⬜ | | | |
| 116 | Pondweed Low-Poly Construction Study | Vegetation | ⬜ | | | |
| 117 | Cattail clump model study | Vegetation | ⬜ | | | |
| 118 | Water Lily Low-Poly Model Study | Vegetation | ⬜ | | | |
| 119 | Amber Shelf Fungus Model Study | Vegetation | ⬜ | | | |
| 120 | Chestnut Mushroom Construction Sheet | Vegetation | ⬜ | | | |
| 121 | Puffball Fungus Model Study | Vegetation | ⬜ | | | |
| 122 | Birch tree modeling study | Vegetation | ⬜ | | | |
| 123 | Willow low-poly modeling reference | Vegetation | ⬜ | | | |
| 124 | Cave Trumpet Fungus Model Study | Vegetation | ⬜ | | | |
| 125 | Juniper shrub construction study | Vegetation | ⬜ | | | |
| 126 | Dry tussock construction study | Vegetation | ⬜ | | | |
| 127 | Rowan tree assembly reference sheet | Vegetation | ⬜ | | | |
| 128 | Heather Low-Poly Construction Study | Vegetation | ⬜ | | | |
| 129 | Alpine Cushion Plant Study | Vegetation | ⬜ | | | |
| 130 | Flax patch construction study | Vegetation | ⬜ | | | |
| 131 | Thorn scrub model study | Vegetation | ⬜ | | | |
| 132 | Silkleaf Rosette Model Study | Vegetation | ⬜ | | | |
| 133 | Moonveil Orchid Model Study | Vegetation | ⬜ | | | |
| 134 | Redroot low-poly model study | Vegetation | ⬜ | | | |
| 135 | Stormreed rare plant model study | Vegetation | ⬜ | | | |
| 136 | Heartpod bramble construction study | Vegetation | ⬜ | | | |
| 137 | Sunpod shrub model study | Vegetation | ⬜ | | | |
| 138 | Goldencrown Tree Model Study | Vegetation | ⬜ | | | |
| 139 | Sunburst Bloom Model Study | Vegetation | ⬜ | | | |
| 140 | Silverbark tree rare concept study | Vegetation | ⬜ | | | |
| 141 | Giant Coil Fern Model Study | Vegetation | ⬜ | | | |
| 142 | Resinheart stump modeling reference | Vegetation | ⬜ | | | |
| 143 | Flintborn altar and cache plinth | Event & VFX | ⬜ | | | |
| 144 | Event cache model study | Event & VFX | ⬜ | | | |
| 145 | Keep Gate Monument Model Study | Event & VFX | ⬜ | | | |
| 146 | Banner and brazier arrangement model study | Event & VFX | ⬜ | | | |
| 147 | Temple Gateway Model Study | Event & VFX | ⬜ | | | |
| 148 | Flintborn rowboat model study | Event & VFX | ⬜ | | | |
| 149 | Flintborn Mooring Post Study | Event & VFX | ⬜ | | | |
| 150 | Flintborn courtyard ruin study | Event & VFX | ⬜ | | | |
| 151 | Flintborn log raft model study | Event & VFX | ⬜ | | | |
| 152 | Shore work rack model study | Event & VFX | ⬜ | | | |
| 153 | Flintborn mine stairs and ladder | Event & VFX | ⬜ | | | |
| 154 | Timber scaffold assembly study | Event & VFX | ⬜ | | | |
| 155 | Mine Sign and Lantern Study | Event & VFX | ⬜ | | | |
| 156 | Flame and embers VFX study | Event & VFX | ⬜ | | | |
| 157 | Wall catwalk assembly reference | Event & VFX | ⬜ | | | |
| 158 | Smoke plume VFX construction study | Event & VFX | ⬜ | | | |
| 159 | Waterfall flow and impact mist | Event & VFX | ⬜ | | | |
| 160 | River flow and foam VFX study | Event & VFX | ⬜ | | | |
| 161 | Shoreline wave and foam study | Event & VFX | ⬜ | | | |
| 162 | Crystal idle glint | Event & VFX | ⬜ | | | |
| 163 | Meteor descent trail construction study | Event & VFX | ⬜ | | | |
| 164 | Mining impact and rock fragments | Event & VFX | ⬜ | | | |
| 165 | Meteor impact burst VFX study | Event & VFX | ⬜ | | | |
| 166 | Rare flora bloom VFX study | Event & VFX | ⬜ | | | |
| 167 | Meteor cooling cracks and heat | Event & VFX | ⬜ | | | |
| 168 | Cache beacon and sparkles | Event & VFX | ⬜ | | | |
| 169 | Frost bloom and snow drift | Event & VFX | ⬜ | | | |
| 170 | Guardian awakening dust and runes | Event & VFX | ⬜ | | | |
| 171 | Resin drip and amber glint | Event & VFX | ⬜ | | | |
| 172 | Harvest Leaves and Pollen VFX Study | Event & VFX | ⬜ | | | |

## Log

- 2026-10-27: inventory written from four independent audit agents (one per sheet group). No model is marked done; every model needs work.
- 2026-10-27: W01 Boulder passed on verifier round 5 (8/10). Shared fixes made on the way: `hull_rock` no longer deletes a flat crown (open-topped rocks), kit studio background matches the floor, cells framed on vertices, 48 samples. New W01 builders: `moss_mounds`/`place_mounds` (leafy moss cap), `herb_bush` (clover clumps), `flower5`.
- 2026-10-27: W01 Rock Spire passed on verifier round 5 (7.5/10). New builders: `slabs`, `collar` (fused rim), `front_boulder`, `ledge_dressing`, bright clover mode.
- 2026-10-27: W01 Rock Cluster passed on verifier round 3 (7.5/10). Fixed a stray copy of the Boulder exploded-layout lines in the Cluster/Pebble rows.
- 2026-10-27: **Paused** after W01 Rock Cluster at the user's request, to start on the new numbered references in `art/blender/assets/references/` (001–172, see its INDEX.md). Next kit model when resumed: W01 Pebble Scatter (no edits made yet). W01 still needs its sheet export once Pebble Scatter passes.
- 2026-10-27: started the numbered references with the `roblox-blender-model` skill. 001 Stone passed on the first verifier round (8/10, all technical checks re-measured through MCP). Fixed `kit_mcp.sample` (it double-encoded sRGB, so earlier hex values read brighter than true). Numbered models are displayed in their own area of FlintbornWorldKit.blend (y = -200 southward, 10 per row, labels in `_Labels`).
- 2026-10-27: user asked for chunkier nodes: 001 and 002 footprints widened to near-round (depth ≈ 0.9 of width). 002 Flint passed on round 2. Its first build overwrote R01's `FlintInsertSmall` (same name); the original was restored from the committed blend, and `kit_models.mk` now appends the model code on a name clash (`FlintInsertSmallM002`).
- 2026-10-28: PR #72 (world kit W01, 001, 002) merged into v0.18. 003 Iron passed (6.5/10).
- 2026-10-28: PR #73 (003) merged into v0.18. 004 Obsidian passed on round 3 (fixed a crystal lean-angle bug and a floor cut that left the base above z = 0).
- 2026-10-28: PR #74 (004) merged into v0.18. 005 Quartz passed (6.5/10). `kit_models.repair_nonmanifold` now clears the grazing-contact slivers booleans leave.
- 2026-10-28: PR #75 (005) merged into v0.18. 006 Copper passed (6/10).
- 2026-10-28: 007 Coal passed (7/10).
- 2026-10-28: PR #75 (005, 006, 007) merged into v0.18. 008 Azurite passed (6.5/10); parts renamed AzuriteCrystalMain/Side and AzuriteRockBase/Side because R03 owns the plain names.
- 2026-10-28: PR #76 (008) merged into v0.18. 009 Iron Meteor passed (6/10): cracks carved by boolean difference with glowing (Neon) walls, heat_glow and embers sockets. Conflict: the sheet's grey "Metal Core" swatch vs its orange core in every view; orange used.
- 2026-10-28: 010 Gold passed (6/10). `kit_models.carve` (boolean difference with a cutter built in the asset's coordinates) shared from 009. PR #77 held: v0.18's own CI went red after another branch's batched-publishing merge (preflight tests: "Cloud task too large").
- 2026-10-28: PR #77 (009, 010) merged into v0.18 after v0.18 was fixed. 011 Amethyst passed (6/10): geode carved with `kit_models.carve`, crystals and lip joined in with `kit_models.merge_in`. `m004.floor_cut` takes an explicit ground height.
- 2026-10-28: 011 reworked from user review: the cave is bare stone inside (not a violet lining), with thick walls, a flat mouth cut and a thick rolled lip. `kit_models.drop_specks` removes boolean slivers.
