# Flintborn maps

Map design documents for Flintborn's two places, the lobby and the play world (GDD Q163). [`GDD.md`](../design/GDD.md) is the source of truth for gameplay intent. When a map document disagrees with it, the GDD wins.

| Map | Place | Document | Status |
| --- | --- | --- | --- |
| Lobby hub | Lobby (`ROBLOX_LOBBY_PLACE_ID`) | [lobby-hub.md](lobby-hub.md) | Built from the owner's reference (`art/reference/lobby_map.png`, layout in `art/blender/lobby/LAYOUT.md`) and placed by the lobby-map workflow; station prompt parts still to come |
| Shattered Crater | Play world (`ROBLOX_MAIN_PLACE_ID`) | Not started | Layout and scale set by the owner (GDD §54). A generated placeholder island ships today (`src/shared/World/IslandLayout.luau`, built by `WorldBuildService` and `src/server/WorldBuild/`) |

## Shared conventions

- **Units:** studs. Travel times assume Roblox's default walk speed of **16 studs/s** until movement tuning changes it.
- **Scale (GDD §54, replacing Q165's ~2,400 studs):** the island is **4,096 studs across** in a 6,144-stud ocean (`BiomeCatalog.ISLAND_SIZE`, `WORLD_SIZE`). That is about 128 s of walking from the edge to the centre and about 256 s across. The lobby hub is deliberately small (~160 studs across, Proposed).
- **Tags over coordinates:** gameplay finds spawn points, stations, portals and zones through CollectionService tags, never hard-coded positions. Each map document lists its tags.
- **Authoring:** the script release ships scripts only ([DEPLOYMENT.md](../ops/DEPLOYMENT.md)). Large geometry is built in Studio and published from Studio to its place, except the lobby map, which the manual lobby-map workflow uploads and places (its place-saving modes run only from `main`; [DEPLOYMENT.md → Manual asset workflows](../ops/DEPLOYMENT.md#manual-asset-workflows)). Map models synced through Rojo live under `src/maps/<MapName>/`, which maps to `ServerStorage.Maps`.
- **Owner questions** use the GDD's running numbering. Answers are recorded in the GDD first, then copied into the map document.
