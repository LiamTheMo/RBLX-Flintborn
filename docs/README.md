# Flintborn documents

Every document in the repository, one line each.

- **Current**: describes the game, code or pipeline as it is; keep it up to date.
- **Design record**: the measured or proposed design something was built from; read it for intent, and check the code (or the named current document) for what shipped.
- **History**: kept for the record only; the named document is the current replacement.

When documents disagree, the [GDD](design/GDD.md) wins on gameplay intent and the code wins on behaviour.

## Project

| Document | Status | What it is |
| --- | --- | --- |
| [README.md](../README.md) | Current | Overview, repository layout, tools, the checks CI runs, branches |
| [AGENTS.md](../AGENTS.md) | Current | Working rules: code changes and releasing, shell commands, the Blender wrapper |
| [design/GDD.md](design/GDD.md) | Current | Game Design Document: the source of truth for gameplay, owner decisions and change log |
| [design/ITEM_CATALOG.md](design/ITEM_CATALOG.md) | Current | Item and material tables behind GDD §51 |
| [phases/README.md](phases/README.md) | Current | Phase index (`v0.01`–`v0.19`) and the branch and release model |
| [release/RELEASE_CHECKLIST.md](release/RELEASE_CHECKLIST.md) | Current | What remains before the permanent `v1.00` branch |
| [release/MANUAL_VALIDATION.md](release/MANUAL_VALIDATION.md) | Current | Studio and live checks per shipped phase, with their placeholder values |
| [ops/DEPLOYMENT.md](ops/DEPLOYMENT.md) | Current | Releasing through VS Code → Rojo → Studio, the place IDs, importing art, the script mapping |
| [maps/README.md](maps/README.md) | Current | Map documents and shared map conventions (scale, tags, authoring) |
| [maps/lobby-hub.md](maps/lobby-hub.md) | Design record | The lobby hub's station list, flow and tags; the built layout is in [art/blender/lobby/LAYOUT.md](../art/blender/lobby/LAYOUT.md) |

## Art

| Document | Status | What it is |
| --- | --- | --- |
| [art/visuals.md](art/visuals.md) | Current | Approved art direction: environment, models, materials, lighting, readability |
| [art/Modeling.md](art/Modeling.md) | Current | Character and creature modeling guide |
| [art/WorldModeling.md](art/WorldModeling.md) | Current | World and vegetation modeling guide for Blender |
| [art/MODEL_PROGRESS.md](art/MODEL_PROGRESS.md) | Current | World-kit rebuild tracker: the status of every numbered model |
| [art/ASSET_LIST.md](art/ASSET_LIST.md) | Current | Everything the game needs modelled, taken from the game's data |
| [art/reference_prompts/README.md](art/reference_prompts/README.md) | Current | Image-generator prompts for new reference sheets ([01 world](art/reference_prompts/01_world.md), [02 creatures](art/reference_prompts/02_creatures.md), [03 gear](art/reference_prompts/03_gear.md), [04 VFX](art/reference_prompts/04_vfx.md)) |
| [../art/blender/README.md](../art/blender/README.md) | Current | The Blender pipeline: sheet scripts, libraries, the world kit, lobby export |
| [../art/blender/kit/mcp/STAGES.md](../art/blender/kit/mcp/STAGES.md) | Current | The stage procedure every numbered model follows |
| [../art/blender/skills/roblox-blender-model/SKILL.md](../art/blender/skills/roblox-blender-model/SKILL.md) | Current | The modelling skill the stage agents load |
| [../art/blender/assets/references/INDEX.md](../art/blender/assets/references/INDEX.md) | Current | Index of the numbered model reference sheets |
| `art/blender/renders/models/M<NNN>/M<NNN>_spec.md` | Current | Per-model spec and stage records (70 files) |
| [../art/blender/kit/BUILDER_GUIDE.md](../art/blender/kit/BUILDER_GUIDE.md) | Current (budgets) | Module contract and triangle budgets; its wave workflow (`kit-wave.js`) belongs to the 2026-10-26 pilot, see [MODEL_PROGRESS](art/MODEL_PROGRESS.md) and [STAGES](../art/blender/kit/mcp/STAGES.md) for how models are built now |
| [../art/blender/lobby/LAYOUT.md](../art/blender/lobby/LAYOUT.md) | Current | The lobby map layout the lobby build follows |
| [../art/vfx/README.md](../art/vfx/README.md) | Current | VFX textures, emitter specs and sockets |
| [history/world-kit-orchestration-2026-10-26.md](history/world-kit-orchestration-2026-10-26.md) | History | The 2026-10-26 world-kit pilot handoff; now [MODEL_PROGRESS](art/MODEL_PROGRESS.md) and [STAGES](../art/blender/kit/mcp/STAGES.md) |
| [../art/reference/kit/CHECKLIST.md](../art/reference/kit/CHECKLIST.md) | History | The pilot's per-sheet checklist (written by `kit_watch.py`); now [MODEL_PROGRESS](art/MODEL_PROGRESS.md) |
| `art/blender/renders/kit/<SHEET>/*_goals.md` | History | The pilot's per-model goals (103 files, read by `kit-wave.js`); now [MODEL_PROGRESS](art/MODEL_PROGRESS.md) and the `M<NNN>_spec.md` files |

## UI

| Document | Status | What it is |
| --- | --- | --- |
| [ui/STYLE_GUIDE.md](ui/STYLE_GUIDE.md) | Current | The entry point for any UI work: look, tokens, components, art pipeline, QA |
| [ui/KIT.md](ui/KIT.md) | Current | API reference of the UI kit (`src/client/Hud/Kit`) |
| [ui/ARCHITECTURE.md](ui/ARCHITECTURE.md) | Current | The UI contract and its §12 decisions; §8 (file ownership) and §10 (build plan) are history of the finished rebuild |
| [ui/ITEM_ART.md](ui/ITEM_ART.md) | Current | How every item's icon is built, packed and drawn |
| [ui/UI_PROGRESS.md](ui/UI_PROGRESS.md) | Current | UI rebuild tracker: per-screen status, verification, open findings |
| [ui/HudScreen.md](ui/HudScreen.md) | Current | In-world HUD spec |
| [ui/ListWindows.md](ui/ListWindows.md) | Current | Market, Trade, Progress and World Map windows |
| [ui/CraftingScreen.md](ui/CraftingScreen.md) | Current | Field crafting mode of the recipe window |
| [ui/LobbyScreen.md](ui/LobbyScreen.md) | Design record | Measured spec of the lobby HUD (mockup 01) |
| [ui/InventoryScreen.md](ui/InventoryScreen.md) | Design record | Measured spec of the Inventory and Vault window (mockup 02) |
| [ui/SettingsScreen.md](ui/SettingsScreen.md) | Design record | Measured spec of the Settings window (mockup 03) |
| [ui/PartyScreen.md](ui/PartyScreen.md) | Design record | Measured spec of the Party window (mockup 04) |
| [ui/PlayScreen.md](ui/PlayScreen.md) | Design record | Measured spec of the Play window (mockup 05) |
| [ui/ForgeScreen.md](ui/ForgeScreen.md) | Design record | Measured spec of the Ancestral Forge window (mockup 06) |
| [ui/JournalScreen.md](ui/JournalScreen.md) | Design record | Measured spec of the Quest Journal (mockup 07) |
| [../art/reference/ui/lobby/README.md](../art/reference/ui/lobby/README.md) | Current | Index of the UI mockups and kit sheets |
| [../art/ui/kit/CATALOG.md](../art/ui/kit/CATALOG.md) | Current | Generated catalog of the `lk_*` kit sprites (rebuilt by `art/ui/slice_lobby_kit.py`) |
| [../art/ui/verify/visual/REPORT.md](../art/ui/verify/visual/REPORT.md), [responsive](../art/ui/verify/responsive/REPORT.md), [code](../art/ui/verify/code/REPORT.md) | History | Round-1 UI verification reports; now [UI_PROGRESS](ui/UI_PROGRESS.md) |
