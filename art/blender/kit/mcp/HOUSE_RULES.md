# World-kit house rules

Standing answers to the questions every study used to raise (user decision, 2026-11-04). They come from the
main-session rulings on models 040–070. A model's brief lists only where it departs from these rules; anything the brief
doesn't mention follows them. STAGES.md still sets the quality bar.

## Scale

- 1 Blender unit = 1 stud. A player is an R6 figure 5 studs tall; size everything against that, not real metres.
- **Doors:** clear opening 3.60 wide × 7.00 tall.
- **Raised floors:** deck top at 2.60, reached by risers of at most 0.87 so a player walks up without jumping. Taller
  risers are a Studio check (Requires Manual Validation).
- **Furniture:** table tops 2.60, seats 1.50, crate 2.30, barrel 2.72. Props keep these sizes even when a sheet draws
  them bigger; record the difference as a miss.
- **Headroom:** at least 6.9 under any roof, canvas or beam a player walks under; 7.8 inside buildings.
- **Tall posts and poles:** 12.0, as M066.
- **Tiling modules:** a 16-stud pitch (M040's tile). Seams at ±8.000, nothing crosses them, and the end sections match.
- **Trees:** low limbs and leaves start at least 7.8 up, so players walk under the crown.

## Budget (triangles, whole hero)

| Class | Ceiling | Examples |
| --- | --- | --- |
| prop | 1,000 | pickups, small dressing, a single part |
| asset | 4,000 | plants, rocks, resource nodes, furniture sets, tiling walls |
| structure | 6,000 | open shelters, ruins, platforms, bridges |
| building | 8,000 | enterable buildings, large trees, landmarks |

Every exported part stays under 1,000. Plan about 10 % under the ceiling. If a model can't match its sheet within its
class, the brief says which details go; never exceed the ceiling silently.

## Reading the sheet

- The hero view (usually the front three-quarter) governs positions and layout.
- When other cells mirror it or disagree, the hero view wins and the other cells are recorded misses, not blockers.
  Verifiers compare a mirrored cell against a mirrored render.
- Side and top cells are judged for content (what is there), not exact placement.
- A rear three-quarter that is a redraw of the front is judged on content only.
- The drawing governs over the sheet's text notes when they disagree.

## Defaults

- **No ground:** no grass, ground scatter or soil patch in the hero. Ground scatter is placed in Studio.
- **Feet:** flat on z 0, never pointed stakes below ground.
- **Enterable buildings:** in the hero, the door leaf stands open inward about 95°. A DoorFrame part carries the closed
  leaf with its hinge stored. Walls, gables and floors are light-tight from inside: run the escape scan, and only the
  doorway may let rays out.
- **Windows:** read dark, as sheets draw them. Use a dark inner shutter or backing so square-on views don't see
  straight through.
- **Lights:** lantern glass is Neon at emission 1.0 with a `heat_glow` socket. A chimney gets a thin, pale
  `chimney_smoke` socket. No other light or VFX unless the sheet shows it.
- **Collision:**
  - hero `precise` when players walk on or into it, otherwise `hull`;
  - foliage, dressing and grass `none`;
  - tiling modules `box`.
- **Joints:** pieces seat 0.002–0.05 into what holds them. Nothing floats and nothing is buried deeper than 0.05.
- **Rope:** gold-tan lashings with real turns; at a peak, a saddle block may stand in for a lashing that would pierce
  the cover.

## Names

- Hero: PascalCase, descriptive, and not already used by any other model or by the W sheets. Grep the exports before
  choosing.
- Parts: `<Hero><Part>`.
- Material keys `mNNN_*`, collection `Kit/MNNN <Title>`.
- Parts are the pieces worth placing on their own, each under 1,000 tris; usually 4–12.

## Colour

- Base colours come from medians of the sheet's flat regions, calibrated with `K.calibrate`.
- Colour goes by position and role, never by face direction.
- Recorded, not scored:
  - differences from studio lighting (lit/mid/shade splits, a face in the studio's shadow);
  - ink outlines in dark-pixel shares;
  - lit cream canvas clipping toward white.

## Foliage and trees

- **The skeleton reads:** at least 1.5 studs of bare limb shows in the front, rear and hero views. Every arm tapers to
  half its base or less.
- **No balls or domes:**
  - no ball domes, spiky crowns or flat cards;
  - leaves are low "tent" leaves (`kit_parts`) or lobed solids with thickness.
- **The 5° sweep binds:** whole leaves edge-on stay at or under 10 % of leaf area at every step (STAGES).
- **Facings:** leaves face by growth or radially, never toward one camera.

## Remakes

When a sheet was remade (see `art/blender/assets/references/INDEX.md`), the remake governs. Reuse the earlier builder's
pieces where the design is unchanged, but check every dimension against the new sheet.
