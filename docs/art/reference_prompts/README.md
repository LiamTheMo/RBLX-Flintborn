# Reference-sheet prompts

Four copy-paste prompts for an image generator. Each one makes production reference sheets in the same style as the 172 numbered sheets in [`art/blender/assets/references/`](../../../art/blender/assets/references/INDEX.md), so new sheets go straight into the Blender modelling pipeline.

| Prompt | Covers | New sheets |
| --- | --- | --- |
| [01_world.md](01_world.md) | Resource nodes, depleted nodes, event set-pieces, building pieces, extraction sites, landmarks, lobby stations | 173–212 (40) |
| [02_creatures.md](02_creatures.md) | Wildlife, event creatures, undead, bosses, lobby NPCs | 213–245 (33) |
| [03_gear.md](03_gear.md) | Weapons and tools by family and tier, Guardian's Fang, armor, ammo, throwables, consumables, drops | 246–270 (25) |
| [04_vfx.md](04_vfx.md) | Rarity, combat, survival, building and raids, gathering, extraction, events and bosses | 271–301 (31) |

## How to use

1. Open a **new chat** for each prompt, and paste everything inside the box.
2. It makes the first sheet. Type `next` for the following sheet, or `redo: <what to fix>` to remake the current one.
3. Save each image as its page number (`173.png`, `174.png` and so on) in `art/blender/assets/references/`, then add a row to `INDEX.md` and `docs/art/MODEL_PROGRESS.md`.
4. Check every sheet before saving it. It should show the same model in every view, the whole model in frame, solid colours with no texture, the parchment background, and the right page number. Generated sheets are visual targets, not exact drawings (see `WorldModeling.md` §1.1).

Each prompt carries the same house style: the palette, tier colours, rarity colours and sheet layout, taken from `WorldModeling.md` §1.2 and §5, `Modeling.md` §2, §6 and §11, `GearModels.luau` and `Rarity.luau`. Every prompt also tells the generator what is already finished and what already has a reference, so it matches them instead of redrawing them.

## Where everything stands

| | Finished (modelled or live) | Has a reference, not modelled yet | No reference (these prompts) |
| --- | --- | --- | --- |
| World | 001–067, 069, plus the live lobby set | 068, 070–155, 157 (88 sheets; 068 and 070 are in progress) | 173–212 |
| Creatures and NPCs | The R6 player survivor | None | 213–245 |
| Gear | 16 lobby display weapons and tools (sheet 04) | None | 246–270 |
| VFX | The lobby's fire, waterfall, dust and rune effects | 156, 158–172 | 271–301 |

The full per-asset status is in [`../ASSET_LIST.md`](../ASSET_LIST.md).
