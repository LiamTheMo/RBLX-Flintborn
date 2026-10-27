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

## Log

- 2026-10-27: inventory written from four independent audit agents (one per sheet group). No model is marked done; every model needs work.
- 2026-10-27: W01 Boulder passed on verifier round 5 (8/10). Shared fixes made on the way: `hull_rock` no longer deletes a flat crown (open-topped rocks), kit studio background matches the floor, cells framed on vertices, 48 samples. New W01 builders: `moss_mounds`/`place_mounds` (leafy moss cap), `herb_bush` (clover clumps), `flower5`.
- 2026-10-27: W01 Rock Spire passed on verifier round 5 (7.5/10). New builders: `slabs`, `collar` (fused rim), `front_boulder`, `ledge_dressing`, bright clover mode.
- 2026-10-27: W01 Rock Cluster passed on verifier round 3 (7.5/10). Fixed a stray copy of the Boulder exploded-layout lines in the Cluster/Pebble rows.
- 2026-10-27: **Paused** after W01 Rock Cluster at the user's request, to start on the new numbered references in `art/blender/assets/references/` (001–172, see its INDEX.md). Next kit model when resumed: W01 Pebble Scatter (no edits made yet). W01 still needs its sheet export once Pebble Scatter passes.
