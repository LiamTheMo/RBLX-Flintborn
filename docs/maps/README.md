# Flintborn maps

Map design documents for Flintborn's two places, the lobby and the play world (GDD Q163). [`GDD.md`](../../GDD.md) is the source of truth for gameplay intent. When a map document disagrees with it, the GDD wins.

| Map | Place | Document | Status |
| --- | --- | --- | --- |
| Lobby hub | Lobby (`ROBLOX_LOBBY_PLACE_ID`) | [lobby-hub.md](lobby-hub.md) | Draft: station list and flow; geometry waits on the owner's reference image |
| Shattered Crater | Play world (`ROBLOX_MAIN_PLACE_ID`) | Not started | Scale confirmed (Q165). A generated placeholder island ships today (`src/shared/World/IslandLayout.luau`) |

## Shared conventions

- **Units:** studs. Travel times assume Roblox's default walk speed of **16 studs/s** until movement tuning changes it.
- **Scale (Q165):** the Shattered Crater island is about **2,400 studs across** (`BiomeCatalog.MAP_RADIUS = 1200`). That is about 75 s of walking from the edge to the centre and about 150 s across. The lobby hub is deliberately small (~160 studs across, Proposed).
- **Tags over coordinates:** gameplay finds spawn points, stations, portals and zones through CollectionService tags, never hard-coded positions. Each map document lists its tags.
- **Authoring:** large geometry is built in Studio and published from Studio to its place. The GitHub release ships scripts only ([roblox-live-deployment.md](../roblox-live-deployment.md)). Map models synced through Rojo live under `src/maps/<MapName>/`, which maps to `ServerStorage.Maps`.
- **Owner questions** use the GDD's running numbering. Answers are recorded in the GDD first, then copied into the map document.
