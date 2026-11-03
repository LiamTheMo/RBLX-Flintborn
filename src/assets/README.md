# Assets

Everything under `src/assets` is synced 1:1 into `ReplicatedStorage.Assets`
via `default.project.json`, so folder names here are instance names in
Studio too — keep them PascalCase.

Models, images and other assets placed here reach the live game through Studio
(Rojo sync, then publish from Studio), like everything else. The lobby map, the
player character and the UI sprites are imported or uploaded in Studio instead
([docs/ops/DEPLOYMENT.md](../../docs/ops/DEPLOYMENT.md#art-and-images)).

## Models

3D assets (primitive tools, weapons, armor, structures, creatures) live under
`Models/`, grouped by category: `Models/3D` holds meshes, and `Models/2D` is
kept empty for flat art used by models. Item icon source art is not here: it
lives in `art/ui/items/source/` (docs/ui/ITEM_ART.md).

## Images

2D art lives under `Images/`, split by purpose:

- `Images/Homepage` — store page / marketing renders (icon, thumbnails).
- `Images/UI` — in-game UI icons/art.

## Maps

World layouts (the Shattered Crater island, lobby) live in `src/maps`, which
Rojo maps to `ServerStorage.Maps`.
