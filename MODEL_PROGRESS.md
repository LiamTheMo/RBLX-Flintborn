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
| 009 | Iron Meteor_ Flintborn model study | World & resources | ✅ | 3028 (3 shells); parts 386 / 76 / 44 | reworked via stage agents; PASS 7.5/10 (round 2) | minors: side/top cracks at limbs (sheet conflict); crack B no hot floor |
| 010 | Flintborn Gold model study | World & resources | ✅ | 710; parts 112 / 24×3 / 36 | PASS 6/10 (round 1) | minors: no visible recessed seats; host a touch pink |
| 011 | Amethyst Flintborn model study | World & resources | ✅ | 1334; parts 386 / 594 / 36 | remade through stage agents; verifier R3 6.5/10, final fixes applied (2-round cap) | top view shows dome (sheet conflict, side view wins); trough has no end horns |
| 012 | Amber Flintborn model study | World & resources | ✅ | 3364; parts 882 / 626 / 892 / 602 / 378 | remade via stage agents; PASS 7/10 (round 2) | minors: rear uprights post-like; rear amber share low; top nodule forward |
| 013 | Sulfur Flintborn exploded model study | World & resources | ✅ | 1510; parts 50 / 314 / 302 / 42 | stage agents; R1 6 FAIL, R2 7 (self-intersection fixed, confirmed) | minors: front34 narrower; sulfur sits a little high; top view paler |
| 014 | Starstone Low-Poly Construction Study | World & resources | ✅ | 910; parts 16 / 40 / 84 / 46 | stage agents; R1 6.5, R2 6.5 FAIL; final kite-crystal fix checked by main session | minors: blunt shell tops; rock lacks two-tone contrast; side crystal pale |
| 015 | Ember Meteor model study | World & resources | ✅ | 3862; parts 682 / 442 / 796 / 58 / 58 | stage agents; R1 6 FAIL, R2 PASS 7 | minors: one dome rather than four boulders; BR crack edge-on from the rear; side glow mostly the pillar's flat Neon wall; no hot core facet from the rear |
| 016 | Stormglass Flintborn asset study | World & resources | ✅ | 1780; parts 452 / 190 / 482 / 60 | modeller + fresh verifier; R1 PASS 7 | minors: arms flatter than the sheet; far arm high in side view; rocks read as teeth from the side; crystal clips near-white from above; sprig ~10 % small |
| 017 | Flintborn Berry Bush Study | World & resources | ✅ | 2596; parts 206 / 330 / 96 | modeller + fresh verifiers; R1 FAIL 6 (round lobes, dark hidden stems), R2 7 (one berry blocker, fixed by main session) | minors: f34 shows 5 of the sheet's 6 berries; front skirt lobes end high; upper stems dark in front under the canopy shadow; side/rear darker from the studio fill |
| 018 | Flintborn healing herb study | World & resources | ✅ | 840; parts 30 / 32 / 32 / 80 | modeller + fresh verifiers; R1 FAIL 5, R2 FAIL 6, R3 FAIL 6 (numbers pass; look still off) — committed by main session | leftovers (polish pass, in priority order): rosette reads as a cone, not the sheet's low wide mound (B1); top-view leaves too blunt (B2); short bud hidden in r34 (B3); bud lit side clips lemon |
| 019 | Flintborn Resin Node study | World & resources | ✅ | 2334; parts 786 / 120 / 70 / 54 / 154 | modeller + fresh verifiers; R1 FAIL 6 (hooked A_up), R2 PASS 7 | minors: A_up's oblique cut reads as a chisel from the side/rear (layout-forced); stubs read as several sticks, bark share −5.7; join pads hidden in the hero; resin highlight facets lost |
| 020 | Flintborn hardwood stump study | World & resources | ✅ | 1808; parts 798 / 210 / 124 / 174 | modeller + fresh verifiers; R1 FAIL 5 (smooth cone trunk, tulip clumps, boulder root), R2 PASS 7 | minors: bark light patches still read as faint slabs from the back; rim notches crack-like rather than scalloped; BL clump high and BR low in f34; top-view leaf share +6 |
| 021 | Flintborn Root Cluster Study | World & resources | ✅ | 2816; parts 700 / 500 / 600 / 314 | modeller + fresh verifiers; R1 FAIL 6 (rock-pile mound, flat rosettes, bowtie verts), R2 PASS 7.5 | minors: mound flatter on top than the sheet; A's left leg high at the far left; leaf clumps squatter; 3 tiny buried hero faces (invisible, manifold); stones a little light |
| 022 | Flintborn Fiber Shrub Model Study | World & resources | ✅ | 1708; parts 278 / 40 / 376 | modeller + fresh verifiers; R1 FAIL 6 (ball tufts, low upper tier, rear wall), R2 7 (back half grass-like; main session applied the verifier's LEAVES fix) | minors: rear shares now leaves +9 / wood −8 (stems hidden from behind); side view still has one tall blade; V notch high; stub ends read as sawn logs |
| 023 | Flintborn Clay Deposit Model Study | World & resources | ✅ | 1198; parts 232 / 80 / 80 / 36 | modeller + fresh verifiers; R1 FAIL 6.5 (soccer-ball lobes), R2 PASS 7.5 | minors: squat lobes squarer than the sheet's; soil base smoother than the sheet's chunky slab; lit contrast from the studio light; rear lobe layout and rock share (accepted) |
| 024 | Flintborn Thorn Shrub Study | World & resources | ✅ | 2596; parts 232 / 214 / 38 | modeller + fresh verifiers; R1 FAIL 5.5 (splayed nest skeleton, narrow silhouette), R2 PASS 7 | minors: top view reads as a ring with limbs showing; upper outline boxier than the sheet's dome; side view wide with TD dominant; low lobes dark and rounded; thorns wash out from above; h .35 wood row 2 runs against 4 |
| 025 | Emberbloom Flintborn Model Study | World & resources | ✅ | 1470; parts 144 / 100 / 866 | modeller + fresh verifiers; R1 FAIL 6.5 (flame-tongue seed, dull red leaves), R2 PASS 7.5 | minors: leaf medians 30–38 lighter than the sheet's harder shade in front/rear (lighting trade-off); top-view rock share low (6 leaves + crossed front pair); seed's lower cone shows at diagonals; side seed bands deep-heavy |
| 026 | Flintborn softwood log study | World & resources | ✅ | 2266; parts 956 / 124 / 162 / 108 / 198 | modeller + fresh verifiers; R1 FAIL 6.5 (hidden stub top, dull small end, flat clump), R2 PASS 7.5 | minors: ground clumps hover 0.2 above the floor (lowering them split the hero); plate seams visible from the rear; slits long; small stub end chisel-shaped; f34 W:H 1.61 (stub height decision); Studio check on the cut_top / face keys |
| 027 | Flintborn reed patch study | World & resources | ✅ | 2140; parts 140 / 32 / 122 / 158 / 34 | modeller + fresh verifiers; R1 FAIL 6.5 (plank-and-studs rear, leaf tips), R2 PASS 8 | minors: LA tip ~44 dark in the hero (studio-lighting miss, accepted — it faces the key light); LA thin from r34; side view two heads on top; 5 green runs at h .55 vs 6; contact shadows darker |
| 028 | Flintborn frost shrub model study | World & resources | ✅ | 1644; parts 404 / 60 / 46 / 944 | modeller + fresh verifier; R1 PASS 7.5 | minors: right ice nodule small in front; rear V of two prongs missing (accepted conflict); tall limb's pale cut top not visible from front; top-view shares off (sheet inconsistent); base gems pair up from rear/side |
| 029 | Ancient root model study | World & resources | ✅ | 2566; parts 502 / 42 / 80 / 442 / 498 / 414 | modeller + fresh verifiers; R1 FAIL 6 (open arch, spiky fans), R2 PASS 8 | minors: R's hump weak at the upper left; right fan .01 short; r34 W:H 1.17 (sheet drawn from ~-22°, model matches there); egg slightly slim; crest underside band dark (studio shadow) |
| 030 | Mooncap Flintborn model study | World & resources | ✅ | 2880; parts 452 / 48 / 160 / 112 / 154 / 928 | modeller + fresh verifier; R1 PASS 8 | minors: big stem's upper half dark in front under the drooping cap (studio shadow; Studio check); side view off (decided −X droop); rear profile ends; front boulders in a straight line; leaves 12–22 dark |
| 031 | Cave Mushroom Construction Study | World & resources | ✅ | 1648; parts 108 / 94 / 112 / 870 | modeller + fresh verifiers; R1 FAIL 6.5 (bright underside, mauve rocks, slab rocks), R2 PASS 7.5 | minors: drum and upper stalk olive in the cap's shadow in front (Studio check under cave light); Underside part a thick puck; side rocks dark (light direction); top-view cap share high (decision) |
| 032 | Shoreline corner | World & resources | ✅ | 3614; parts 942 / 196 / 550 / 416 / 336 | modeller + fresh verifiers; R1 FAIL 6 (turf slab didn't cap the columns), R2 PASS 7 | minors: plateau deeper and smoother than the sheet (grass over, rim caps hidden); water low on screen; rock median beige; pine share low; 3 foam sockets inside boulders; water preview pale (Studio check) |
| 033 | Flintborn cave moss model study | World & resources | ✅ | 1164; parts 56 / 54 / 268 / 170 / 62 | modeller + fresh verifier; R1 PASS | minors: base share 61 % against decision 4's 70 % (sheet ≈ 67 %, accepted); side clumps rounder than the sheet's ovoids; rock a little beige; lit moss 10–15 dull; thin fold on the base's back |
| 034 | Flintborn streambed model study | World & resources | ✅ | 3782; parts 676 / 430 / 96 / 46 / 88 / 28 | modeller + fresh verifiers; R1 FAIL 6 (egg boulders, outline foam; decision 2 amended), R2 PASS 8 | minors: blue ring between in-water rocks and foam collars; B1 a little upright; f34 rock share high; top view reads as a basin; RockLarge facets plain; Studio checks on water tone and transparency |
| 035 | Flintborn boulder model study | World & resources | ✅ | 3844; parts 210 / 848 / 38 / 246 | modeller + fresh verifiers; R1 FAIL 6.5 (floating, sparse tall foliage), R2 PASS 7.5 | minors: F6 reads as stacked tufts; F5a/b narrow columns; lit foliage dark and less lime; rock boxy at rear/side (wide foot); cap reads as star cones |
| 036 | Flintborn rock cluster model study | World & resources | ✅ | 3898; parts 314 / 320 / 150 / 64 / 120 / 260 | modeller + fresh verifiers; R1 FAIL 6.5 (floating, sparse, pointed foliage), R2 PASS 7.5 | minors: foliage reads as big-leaf ivy mounds, not small clover rosettes; width 13.01 at the edge; A's olive smear a hard facet; 15 leaves cut into rock at hidden joints; back greens dark |
| 037 | Flintborn Waterfall Module Study | World & resources | ✅ | 3920; parts 120 / 884 / 328 / 164 / 84 / 220 / 546 / 46 / 38 / 22 | modeller + fresh verifier; R1 PASS 7 | minors: foam too sparse (pool and front); curtain lacks white streaks; rock share high; columns smooth octagons; rock parts egg-shaped; splash spikes read as ice; back-seam water inset 0.25 (main session moved the rock key off mauve) |
| 038 | Pebble scatter model study | World & resources | ✅ | 3398; parts 330 / 206 / 472 / 56 / 36 / 236 | modeller + fresh verifier; R1 PASS 7.5 | minors: leaf clusters read as cupped lettuce heads (top view too green); pad MC not yellow enough; greens slightly grey; flowers small; B/D facet stats under target; slab top one tone |
| 039 | Flintborn rock spire model study | World & resources | ✅ | 3984; parts 54 / 154 / 184 / 30 / 98 | modeller + fresh verifiers; R1 FAIL 6.5 (spiky rosettes), R2 PASS 7.5 | minors: low front leaves edge-on at the 20° cameras; leaf shade halves olive; foot rock sides steep; front profile mean 0.070; budget at 3984 |
| 040 | Flintborn Cliff Wall Construction Study | World & resources | ✅ | 3202; parts 558 / 984 / 116 | modeller + fresh verifier; R1 PASS 7 | minors: lip reads as a table-top slab (no scalloped rim); dark bushes read as palm stars; lip underside flat; front tabs hidden; lawn patch triangles in top view; pivot offset to note in export (main session fixed the connector key, B > R) |
| 041 | Flintborn Shore Shelf Model Study | World & resources | ✅ | 3858; parts 648 / 496 / 58 / 98 / 34 / 436 / 412 | modeller + fresh verifier; R1 PASS 8 | minors: foam faint and plain, collars stand off the rocks; cap plants sparse; water two-tone from the kit texture; side rocks barrel-like; Studio check of water |
| 042 | Young Fir Model Study | World & resources | ✅ | 2714; parts 256 / 316 / 368 / 784 / 990 | modeller + fresh verifier; R1 PASS 7 | minors: canopy sparser and spikier than the sheet, crown waist wide; lime flap tips read as scales; too much sand; ground plants olive and spiky; rear canopy dark (studio light) |
| 043 | Flintborn terraced ledge model study | World & resources | ✅ | 3916; parts 720 / 988 / 994 / 36 / 148 | modeller + fresh verifier; R1 PASS 8 | minors: side W:H wide (foot dressing); lower-step seam ring differs 0.16; filler reads as a box pillar; lime bush skirts flare like legs; faint lawn triangles; back grooves regular; few flowers; pivot offset to note in export |
| 044 | Flintborn Natural Ramp Study | World & resources | ✅ | 3868; parts 484 / 108 / 332 / 332 / 976 / 960 | modeller + fresh verifiers; R1 FAIL 6 (inward wedge face, star bushes, unbevelled tiles, wide tip strip), R2 PASS 8 | must fix: cliff tip paint partly by normal.z (facing); minors: crown-leaf tip folds; front/top shares (perspective); rock median low; few flowers; small pebbles |
| 045 | Flintborn pine sapling model study | World & resources | ✅ | 3012; parts 470 / 576 / 576 / 348 / 162 / 44 / 44 | modeller + fresh verifiers; R1 FAIL 6 (tiers merged, long plates, rosettes like 042's), R2 PASS 8 | minors: f34 middle hem narrow; crown waist wide; side-on plates read as sticks; lime tip band reads as scales; sand share high; two edge-on GroundFoliage leaves |
| 046 | Flintborn Natural Arch Model Study | World & resources | ✅ | 3960; parts 986 / 872 / 808 / 184 | modeller + fresh verifiers; R1 FAIL 6.5 (foot bushes buried in rock), R2 PASS 7.5 | minors: foot greenery sparse; flowers invisible; no emerald in bushes; crown leaves edge-on from the front; ledge pads read as shelves; rim-bush row widens the top; lawn edge sawtooth |
| 047 | Old Pine Flintborn model study | World & resources | ✅ | 3590; parts 960 / 410 / 280 / 328 / 992 | modeller + fresh verifiers; R1 FAIL 6.5 (skeleton, ball pads), R2 FAIL 7.5 (buried plants), targeted R3 fix | minors: few twigs under L/R in f34; bark share high in front/rear; plants lean yellow; top W:D 1.354; knot a slot; straight trunk column |
| 048 | Flintborn dock model study | World & resources | ✅ | 3860; parts 432 / 416 / 12 / 12 / 12 / 222 | modeller + fresh verifier; R1 PASS 8 | minors: coils read as faceted collars (twist only in colour); 5-sided swags (accepted); f34 gold +2.7 (rope); legs dark in side light; knot boxy; bolt blocks faint from the front |
| 049 | Classic Pine construction study | World & resources | ✅ | 3532; parts 254 / 484 / 546 / 626 / 704 / 918 | modeller + fresh verifiers; R1 FAIL 6 (merged tiers, shield blades, round top), R2 PASS 7.5 | minors: hems spikier than the sheet's fans, crown a tuft; parts read as steep bells; crown light; f34 sub-step a shoulder; T2 hem high; sand share 7.1 % |
| 050 | Flintborn timber bridge model study | World & resources | ✅ | 3860; parts 286 / 12 / 12 / 12 / 12 / 224 | modeller + fresh verifier; R1 PASS 8 | minors: rope wraps read faceted close up; deck reads as one slab in f34 (hairline gaps); pegs close to rope colour; light deck field invisible; Plank part keeps yaw/jitter |
| 051 | Flintborn rope crossing model study | World & resources | ✅ | 3896; parts 68 / 12 / 24 / 44 / 154 / 68 / 130 | modeller + fresh verifier; R1 PASS 8 | minors: coils read as jagged faceted bands; coils and diagonal feet sink slightly deep; foot rocks small shards; stone cool band hard-edged; PegBlock part simplified; no rope across the ends (decided) |
| 052 | Flintborn Boardwalk model study | World & resources | ✅ | 2484; parts 102 / 62 / 12 / 12 / 176 / 12 / 24 | modeller + fresh verifier; R1 PASS 8 | Studio check: 1.12 stair risers walkable; minors: deck smoother than the sheet (edge bands); gold share low; post middle band dark; caps blow out; Brace part stubby |
| 053 | Flintborn dead tree asset study | World & resources | ✅ | 3562; parts 880 / 216 / 172 / 152 / 120 / 104 / 120 | modeller + fresh verifier; R1 PASS 7 | minors: knot hidden at the f34; crown chunkier and less branched (taper, Y-fork tips); lit wood low; moss olive in shade; hero 17 deep; top view tangled |
| 054 | Flintborn broadleaf tree study | World & resources | ⬜ | | | |
| 055 | Fallen Log Model Study | World & resources | ✅ | 3558; parts 956 / 410 / 112 / 260 / 30 / 72 | modeller + fresh verifier; R1 PASS 8 | minors: f34 fill low (dressing past the log ends); f34 bore reads brown; branch fork barely reads; +X flank dark (studio light); cap grain ring missing (main session fixed the rock_dark key, B ≤ G + 4) |
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
- 2026-10-28: PR #78 (011) merged into v0.18. 012 Amber passed (6/10).
- 2026-10-28: user review: 011 Amethyst "looks terrible" (full remake), 012 Amber colour/texture and wood off (full remake), 009 Iron Meteor cracks lack depth (rework). Colours must be sampled from the master, calibrated and blended into neighbours. From now on each model goes through STAGES.md stage agents on Opus 5.5 high.
- 2026-10-28: 011 Amethyst remade through the STAGES.md stage agents (Opus, high): a hollowed-out stone geode with calibrated, blended colour, a stone cave, a crystal_glow cave light and 4 ore_glint sockets. Verifier rounds 6 / 6.5 / 6.5; the last round's fixes applied and committed under the new 2-round cap. Studio gained a rear fill light (build_kit FILL_ENERGY 2.5); renders now restore FB_Ground and hide it in the viewport.
- 2026-10-28: PR #79 (011) merged into v0.18. 012 Amber remade through the stage agents (study, model, cleanup+UV, colour, lighting+VFX): chamfered split-timber wood, faceted amber with glowing seams and inclusions, an amber crystal_glow light and 3 glints. Verifier R1 5/10 FAIL, R2 PASS 7/10. Studies written ahead for 009 (rework), 013, 014, 015 (016 in progress).
- 2026-10-28: PR #80 (012) merged into v0.18. 009 Iron Meteor reworked through the stage agents: a thick shell split by real seam gaps (dark lip → deep red → orange → hot floor, Neon depth bands), a lobe step, a seam light, heat shimmer and embers. Verifier R1 6.5 FAIL (crack B hidden), R2 PASS 7.5. Studies written ahead for 016, 017 and 018; side-view direction correction added to the 013–015 specs.
- 2026-10-28: PR #81 (009) merged into v0.18. 013 Sulfur built through the stage agents: three grooved rock strata with a thick top slab and a tilted terrace, chamfered lemon sulfur blocks graded to an olive shadow by position. R1 FAIL 6 (shape), R2 7 with a self-intersection blocker fixed and confirmed.
- 2026-10-28: PR #82 (013) merged into v0.18. 014 Starstone built through the stage agents: a kite cyan gem between two rock shells and foot rocks, 2 Neon cap facets, a crystal_glow light, a new generic crystal_halo VFX kind, and 3 glints. R1 and R2 both failed at 6.5; a final targeted crystal fix was committed under the 2-round cap.
- 2026-10-28: 015 Ember Meteor built through the stage agents: a cracked dark dome around a faceted Neon core, with real-depth cracks graded dark lip → ember wall → hot, a rock ring, 2 heat_glow lights and 4 ember sockets. R1 FAIL 6, R2 PASS 7. The setup changed to three modellers at once, each in its own background Blender (bgmcp.py), with a fresh verifier per model and the main session as hub; PRs are batched every 3–5 models.
- 2026-10-28: 016 Stormglass built by one modeller in a background Blender: a faceted cyan crystal tree with octagonal fan caps, set in a real hex socket pit in a sand mound ringed by rocks, with 3 ore_glint sockets. Verifier R1 PASS 7. The main session lifted the glint boxes clear of the tilted caps (272 → 1 spawn points inside).
- 2026-10-28: 017 Berry Bush built by parallel modellers: a forked five-stem trunk under 15 faceted, peaked leaf lobes in 5 clumps, with 8 glossy berries. R1 FAIL 6, R2 7 with one cheap blocker (two berries hidden behind the right lobes). The main session moved B5 and B6 forward: the f34 now shows 5 berries (sheet 6) and the rear shows 3.
- 2026-10-28: 020 Hardwood Stump built by parallel modellers: a fluted, 8-lobed trunk with a notched bark rim around a ringed cut face, four wedge roots and four flat star leaf clumps. R1 FAIL 5, R2 PASS 7. The main session gave the bark light patches 25 %/50 % edge rings, so they blend (hard edges 80 → 14). PR #84 (015–017) merged into v0.18.
- 2026-10-28: 019 Resin Node built by parallel modellers: a forked log X with ringed oblique cut ends, two broad-faceted resin lumps graded by hue, five leaf clumps and 2 ore_glint sockets. R1 FAIL 6, R2 PASS 7. The main session blunted A_low's end (END_TURN −45 → −15) to remove a bark spike under the large lump.
- 2026-10-28: 018 Healing Herb committed after three fix rounds: broad lens leaves on a two-part midline (hidden stalk, then a falling board), a hidden root plug and two cream buds graded by height. Round 3 met every numeric target (profiles, rear width, plug share) but the verifier still judged the rosette a cone rather than the sheet's mound. The main session committed it with B1–B3 recorded for a later polish pass instead of a fourth round.
- 2026-10-28: 023 Clay Deposit built by parallel modellers: five broad-based faceted clay domes (convex hulls of jittered rings plus crown points) on a 14-sided soil pad with 11 sunk rocks. R1 FAIL 6.5, R2 PASS 7.5. The main session pulled the main lobe's upper rings and crown in, so it reads as a dome.
- 2026-10-28: 022 Fiber Shrub built by parallel modellers: nine thick lens leaves in two tiers on a six-stem fork, with three open tan fiber crowns on brown collars. R1 FAIL 6, R2 7: the front half matched, but the back half read as grass. The main session applied the verifier's four-row LEAVES fix (LG face-on to the rear; LH / LI steeper, longer and side-facing; LC / LD faces turned out). The side and rear now read as broad leaves, at the cost of rear wood share.
- 2026-10-28: 021 Root Cluster built by parallel modellers: a lumpy faceted dome mound with three bedded stones and three foot boulders, three thick roots lying on it and sinking in, pale cut tips, and three upright leaf stars. R1 FAIL 6, R2 PASS 7.5. The main session lowered the crown module (CLUMP_FLOAT 0.35 → 0.15) so its bark stalk no longer reads as a stick from the rear. The kit audit now counts bowtie verts; 019 and 020 were repaired with M.fix_bowties.
- 2026-10-28: 024 Thorn Shrub built by parallel modellers: an 8-sided trunk column splitting at z 1.2 into crossing front limbs and a back Y, 30 pointed gem lobes in fanned clusters, and five cream thorns on the diagonals. R1 FAIL 5.5 (nest skeleton, narrow), R2 PASS 7.
- 2026-10-28: 026 Softwood Log built by parallel modellers: an 11-sided log with stepped bark plates, 9 carved slits, ledges and a knot hole, a flush ringed cut face with chamfer and rim, a domed far end, two stubs with pale broken tops, and four flat star leaf clumps. R1 FAIL 6.5, R2 PASS 7.5. The main session tried the verifier's ground-clump drop (GROUND_HUB −0.05), but it split the hero into 3 shells, so it was reverted and recorded.
- 2026-10-28: 025 Emberbloom built by parallel modellers: a diamond-faceted Neon seed gem (deep / mid / hot) in a cup of six thick double-pointed red crystal leaves, on a 14-sided slab with 10 boulders and an underside recess. Sockets: crystal_glow light, crystal_halo and yellow spark embers. R1 FAIL 6.5, R2 PASS 7.5. The main session gave the Pod part its own band thresholds (more mid orange, as the sheet's part).
- 2026-10-29: 027 Reed Patch built by parallel modellers: three faceted cattail heads on six-sided stalks over a fan of nine broad keeled leaves that never read edge-on, on a lumpy oval mud mound with five rocks bedded on its rim. R1 FAIL 6.5, R2 PASS 8. LA's dark tip was ruled a studio-lighting miss (no colouring by facing).
- 2026-10-29: 028 Frost Shrub built by a parallel modeller: an 8-sided trunk column forking into a tall cut limb and a right branch, three dark-blue hexagonal shard leaves, pale faceted ice gems, and a snowy rock ring open at the front. R1 PASS 7.5 on the first round. The main session moved the two rock keys to the sheet's warm and grey-brown hues (the cool key had read mauve).
- 2026-10-29: 030 Mooncap built by a parallel modeller: two violet faceted caps drooping along X over fat pear stems, 11 Neon cyan gems in carved pockets and bezels, a dirt slab with 12 boulders, two leaf clumps and one crystal_glow light. R1 PASS 8 on the first round.
- 2026-10-29: 031 Cave Mushroom built by parallel modellers: three faceted rust dome caps (10 sectors, 4 facet rows, crown polygon) with dark lips and tan undersides on fat cream bell stalks, the small two leaning out, in a ring of squat warm-grey boulder domes. R1 FAIL 6.5, R2 PASS 7.5.
- 2026-10-29: 029 Ancient Root built by parallel modellers: two gnarled bark roots arching over and gripping a faceted green sapstone egg, on a lipped stone slab with nine boulders, with two upright four-blade leaf fans. R1 FAIL 6, R2 PASS 8.
- 2026-10-29: 033 Cave Moss built by a parallel modeller: a lobed faceted warm-grey boulder under three squat moss clumps (the centre highest), a lime sprout in the bare front face and a taller one at the back-right, with pebbles and side rocks fused round the foot into one closed shell. R1 PASS on the first round.
- 2026-10-29: 032 Shoreline Corner built by parallel modellers: a 45° grassy ridge capping 17 faceted basalt-like columns, a beach at the cliff foot, see-through water with a separate foam ribbon and boulder rings, pines, bushes and flowers on the turf. R1 FAIL 6, R2 PASS 7.
- 2026-10-29: 034 Streambed Section built by parallel modellers: a 32-stud stream tile with a broad see-through channel between thin sand banks, chunky flat-crowned boulders standing in the water with lobed foam collars, segmented bank foam, and flow and foam sockets, keeping the X −7…+7 seam contract. R1 FAIL 6, R2 PASS 8.
- 2026-10-29: 035 Boulder built by parallel modellers: a big faceted warm stone with a real V cleft, a lobed lime moss cap fused on its crown, and dense rounded clover mounds with white flowers ringing the base, every leaf seated by contact. R1 FAIL 6.5, R2 PASS 7.5.
- 2026-10-29: 036 Rock Cluster built by parallel modellers: a tall faceted warm stone with a flat moss mat, two shorter mossy rocks and small stones in a cluster, ringed by contact-seated clover mounds with white flowers. R1 FAIL 6.5, R2 PASS 7.5.
- 2026-10-29: 038 Pebble Scatter built by a parallel modeller: five separate faceted warm stones round open ground, an extruded flat slab, two moss pads, contact-seated leaf rosettes and a flower clump. R1 PASS 7.5 on the first round.
- 2026-10-29: 037 Waterfall Module built by a parallel modeller: a grassy column cliff tile split by a channel, a three-lobe see-through curtain falling from a notch into a white splash and a full-width pool with boulders in foam rings, pines and ferns on top, and flow, curtain, mist and foam sockets. R1 PASS 7 on the first round.
- 2026-10-29: 040 Cliff Wall built by a parallel modeller: a 16 × 8 modular cliff tile of five tall faceted columns with shards and flat-topped foot boulders, a grass lip fully capping the column tops at 10.4, contact-seated bushes, and a tabbed back connector plate on the +X end. Seams tile cleanly. R1 PASS 7 on the first round.
- 2026-10-29: 039 Rock Spire built by parallel modellers: a seven-sided warm-stone obelisk with a diamond facet, a flat-topped pillar and a leaning side rock, a faceted foot rock, a ring of rocks, and rounded oval-leaf rosettes with dome buds seated by contact in every crevice. R1 FAIL 6.5, R2 PASS 7.5.
- 2026-10-29: 041 Shore Shelf built by a parallel modeller: a 32 × 28 octagonal water tile with a pale sand shelf, a column sea stack capped by a grass cap of ferns and daisies at 10.4, six flat-crowned side rocks, lobed foam rings and 13 foam sockets. R1 PASS 8 on the first round.
- 2026-10-29: 042 Young Fir built by a parallel modeller: a 16-stud tiered fir of three stacked tiers of drooping kite flaps in two shingled rows on core-and-hub shells, an octagonal planked orange trunk with six kinked roots, and a sand patch with rocks and plant clumps, all seated by contact. R1 PASS 7 on the first round.
- 2026-10-29: 043 Terraced Ledge built by a parallel modeller: a 20 × 14 tile of pale column rock stepping up in two lime lawns at 5.6 and 10.4, rims stepping per column with a pale bevel band, column tops fully capped, rounded dome bushes with flowers, a corner filler and a slotted +X connector plate. Seams tile cleanly. R1 PASS 8 on the first round.
- 2026-10-29: 044 Natural Ramp built by parallel modellers: a 16 × 20 flagstone ramp climbing 29.9° from ground to the 10.4 plateau, bevelled 2-across tiles on a stone wedge, stepped column cliffs with peaked tips in a thin outer strip, draped lime borders with round dome bushes and flowers; walkable and flush with M040. R1 FAIL 6, R2 PASS 8.
- 2026-10-29: 045 Pine Sapling built by parallel modellers: a 10-stud pine of three distinct tiers of thick 0.20 chisel-tipped paddle slabs in two visible rings, peg-and-recess joints, a smooth flared orange trunk with blunt root flares, and upright oval-leaf rosettes with pale rocks; clearly distinct from M042. R1 FAIL 6, R2 PASS 8.
- 2026-10-29: 048 Dock built by a parallel modeller: the kit's first timber piece, a raised two-bay pier on six square posts with chunky cross boards at 5.6, side beams, crossbeams, knee and X braces, brass bolts, rope coils on every post and twisted swags along three sides, open walk-on end. R1 PASS 8 on the first round.
- 2026-10-29: 046 Natural Arch built by parallel modellers: a squat column-rock arch 24 × 12 with a 7 × 9 walk-through tunnel, a lumped span seated on flat ledges with no see-through joints, a lime lawn dome capping every rock top at 14, dome bushes and a sand flagstone floor. R1 FAIL 6.5, R2 PASS 7.5.
- 2026-10-29: 047 Old Pine built by parallel modellers: a squat 20-stud gnarled pine with a leaning planked trunk forking into five elbowed limbs plugged into hex sockets, twigs carrying five separate domed cloud pads, seven buttress roots, dark hollows, and a sand base with angular rocks, a dome bush and broad-leaf tufts. R1 FAIL 6.5, R2 FAIL 7.5, targeted R3 fix.
- 2026-10-29: 050 Timber Bridge built by a parallel modeller: a 32-stud level timber footbridge on eight posts over three bays, 14 crisp L-notched boards at 5.6, stringers on the post lines with pegged stubs, knee and end X braces, wooden pegs, geometrically twisted rope wraps and six side swags, both ends open. R1 PASS 8 on the first round.
- 2026-10-29: 049 Classic Pine built by parallel modellers: a 22-stud tall pine of four distinct rings (crown, Tier 2, Tier 1 upper and lower) of long parallel cut-tip blades with the inner row on top, a lime five-ridge crown star, peg-and-sleeve joints, a planked trunk with seven built-in buttress roots, and a sand base with rocks, bush mounds and upright clusters. R1 FAIL 6, R2 PASS 7.5.
- 2026-10-29: 051 Rope Crossing built by a parallel modeller: a sagging 10-plank rope footbridge between four faceted anchor stones under timber posts with twisted rope coils, red cloth wraps and backstays, main ropes with hangers, diagonals and links, a low end sill and open walk-on ends; walkable within 17° and 0.08 steps. R1 PASS 8 on the first round.
- 2026-10-29: 052 Boardwalk built by a parallel modeller: a 32 × 9.5 timber walkway at deck 5.6 on square posts, 17 gapped planks notched round the posts, a back and +X end rail, open front for joins, 4-tread stairs to the ground, symmetric braces, brass hex bolts and a twisted rope tie. R1 PASS 8 on the first round.
- 2026-10-30: 053 Dead Tree built by a parallel modeller: an 18-stud bare twisted snag of six rope strands with "/" grooves, six plug-in kinked limb modules with blunt square-cut tines, six split-toe roots, about 50 bore pits, a ringed knot hole and a snapped limb, with pale rocks, lime tufts and moss at the foot. R1 PASS 7 on the first round.
- 2026-10-30: 055 Fallen Log built by a parallel modeller: a Ø 5 × 14 hollow log of 12 planked staves with V grooves, an open broken end of staggered blocks round a round black bore, a cracked cut-end cap, a Y branch stub, 63 flat lobed moss leaves in rosettes and chains, neutral faceted rocks and lime tufts; climbable and walkable along the top. R1 PASS 8 on the first round.
