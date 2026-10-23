# Assets

Everything under `src/assets` is synced 1:1 into `ReplicatedStorage.Assets`
via `default.project.json`, so folder names here are instance names in
Studio too — keep them PascalCase.

The automated release only ships scripts. Models, images and other assets
placed here reach the live game through Studio (Rojo sync, then publish from
Studio), never through GitHub Actions.

## Models

3D assets (primitive tools, weapons, armor, structures, creatures) live under
`Models/`, grouped by category. `Models/2D` holds flat art used by models;
`Models/3D` holds meshes.

## Images

2D art lives under `Images/`, split by purpose:

- `Images/Homepage` — store page / marketing renders (icon, thumbnails).
- `Images/UI` — in-game UI icons/art.

## Maps

World layouts (the Shattered Crater island, lobby) live in `src/maps`, which
Rojo maps to `ServerStorage.Maps`.
