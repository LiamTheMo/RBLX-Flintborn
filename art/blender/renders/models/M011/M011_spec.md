# 011 Amethyst — spec

Remade from scratch at the user's request (2026-10-27): the previous model was judged "terrible".

Reference: `art/blender/assets/references/011.png` (AMETHYST, page 11). Builder: `art/blender/kit/mcp/m011.py` → `build()`.

Assets (collection `Kit/M011 Amethyst`):

- `Amethyst` (hero).
- `AmethystShellTop` (Top Shell).
- `AmethystShellBottom` (Bottom Shell).
- `AmethystShard` (Crystal, reusable).

The R03 kit sheet owns `AmethystTopShell`, `AmethystBottomShell` and `AmethystCrystal`, which is why the parts have these names.

## Study (2a)

- **Classification:** full asset (resource node / geode). Budget: hero 4000 tris, each part 1000.
- **Size:** about 11.8 W × 8.4–8.9 D × 9.5 H studs, roughly 1.7× the 5.5-stud character.
  - The sheet's front view is 1.17 W:H and its side view is 0.89 D:H; the model matches both: 1.24 and 0.93.
- **Silhouette:**
  - A broad, faceted stone egg that is hollow and open to the front.
  - The mouth is a large round arch, about 70 % of the width. The arch's top sits just below the dome top and overhangs slightly, as in the side view.
  - A fan of fat purple crystals fills the mouth. The tallest is in the middle and reaches about 80 % of the height. The two big side crystals lean outward and forward. A small one sits low in the crack between the front slabs.
  - A ring of chunky, flat-topped slabs runs across the front and round the base.
  - From the rear it reads as a plain faceted egg, with low lumps at the two bottom corners.
- **Parts (exploded view):**
  - **Top Shell:** a thick hood or cap. Its wall is about 1.35–1.4 studs all round, as the "shell thickness (underside)" close-up shows.
    - A thick rounded lip runs round the arch.
    - Its underside is open: the cave ceiling, in bare stone.
    - It sits on a flat contact ring.
  - **Bottom Shell:** a bowl of slabs.
    - Two low, rounded front slabs meet at a crack in the middle.
    - Two tall end blocks form the arch's legs.
    - A back wall rises to the contact plane (z 4.2).
    - Inside is the flat crystal seat (z 1.6).
  - **Crystal (×4 on the sheet):** a fat, doubly terminated six-sided crystal: a root point, a straight body and a pointed tip with a shoulder ring. The hero uses 7 copies: the sheet's front view shows 7, with the 4 exploded ones being size and lean variants.
- **Relationships:**
  - The top shell sits on the bottom shell's flat walls; both outlines meet exactly at z 4.2 ("shell contact surface (flat)").
  - The crystals stand on the flat seat inside the bowl ("crystal seat (flat surface)").
  - The inside of both shells is stone; only the crystals are purple.
- **Colours:** sheet swatches are crystal light #C097DD, mid #924EC3 and dark #5F3289, and rock #9E8F8B. The cave interior reads darker in shadow. This is stage 4's job.
- **Effects:** none drawn. The lighting and VFX stages decide; the crystals may justify a subtle sparkle.
- **View conflicts, and how they were resolved:**
  - In the top view the crystals look fully visible from above; the side view shows a hood overhanging them. I followed the side view and hero view, so the hood covers the back half.
  - The hero three-quarter reads wider than the front and side views allow. The front and side proportions are matched instead.
  - The exploded view has a tall bottom shell. Its end blocks became the arch's legs (contact plane at 4.2, not at the front-slab height of about 3).

## Stage 1 — Modelling (remake)

User feedback the remake answers:

- An empty dark hole with small crystals: the crystals are now fat and fill the mouth.
- The lip looked like pebbles: there are now two broad, rounded front slabs.
- Purple lining: the inside is now stone (`m011_cave`).
- A thin lip: the lip is now thick (about 1.4) and rounded, three facets across.

- **Top shell** (`top_shell`) is built directly, with no booleans.
  - Two faceted sheets, outside (superellipsoid 5.2 × 4.3 × 5.2, exponent 2.3) and inside (3.85 × 2.95 × 3.8), on one shared grid of 18 columns round an up-and-back pole.
  - The rim of each column is where it leaves the shell (the mouth plane, leaning 10° forward, or the contact plane).
  - Outside and inside are joined by a lip of 3 rows that rolls 0.55 forward of the mouth plane and fades flat at the arch's feet, and by a flat contact ring underneath.
  - Random diagonals and per-vertex wander give big irregular triangle facets rather than latitude bands.
- **Bottom shell** (`bottom_raw`, then `union_loose`, `carve(bottom_cutter)` and `_tidy`):
  - A stone core whose top ring uses exactly the top shell's own contact points, so the two are flush; below that it tucks in like an egg. It is clipped behind the mouth plane.
  - A base plate.
  - 9 slabs (`hull_rock`): two front slabs with a rounded bevel ring, the two end blocks (the legs) flush at the contact plane, two side slabs, a left corner lump and two back corner lumps.
  - A convex bowl cutter carves the inside. Its walls slope down to the flat seat, its top is the top shell's inner contact outline, and it stops at y −1.5 so the front slabs stay about 2 studs thick.
  - `_tidy` merges coplanar boolean slivers (0.5°).
- **Crystal** (`shard`): a convex hull of a root point, a body-foot ring, a body-top ring, a shoulder ring and the tip. r 1.25, root 1.1, body 2.6, tip 1.5.
- **Hero** (`hero`): pasted strictly from the three finished part meshes.
  - Each part records its offset into the shared build frame (`m011_offset`).
  - The top shell is sunk 0.04 into the bottom shell so the union sees an overlap rather than coincident faces; coincident faces gave a broken union.
  - The 7 crystals are scaled, leaned and turned copies of `AmethystShard`.
  - Then `union_loose`, `_tidy`, `finish`, and `_seal`, which closes a pinhole of a few hundredths of a stud on the seam.
- **Placeholder colour keys:** `m011_rock` (outside and lip), `m011_cave` (both shells' inner stone), `m011_crystal_mid` (crystals). `m011_crystal_light` and `m011_crystal_dark` are registered for stage 4.

### Measured (MCP audit, after the final build)

| Object | Tris | Shells | Non-manifold / boundary / wire | Size (studs) |
| --- | --- | --- | --- | --- |
| Amethyst | 1560 / 4000 | 1 | 0 / 0 / 0 | 11.76 × 8.86 × 9.48 |
| AmethystShellTop | 360 / 1000 | 1 | 0 / 0 / 0 | 10.50 × 6.23 × 5.32 |
| AmethystShellBottom | 662 / 1000 | 1 | 0 / 0 / 0 | 11.76 × 8.32 × 4.20 |
| AmethystShard | 36 / 1000 | 1 | 0 / 0 / 0 | 2.43 × 2.00 × 5.20 |

- Every object checks clean:
  - no n-gons, zero-area faces, duplicate vertices or loose vertices;
  - normals outward, no custom normals;
  - origin at the bottom centre, transforms applied, a UV map present.
- `K.check` reports no problems.

### Left for later stages

- **Stage 2:**
  - The hero's seam band (the 0.04 sink) leaves small sliver faces round the contact ring.
  - The flat contact ring of the top shell keeps 3 collinear lip rows (hidden quads). These could be dissolved.
- **Stage 4:**
  - All colour: crystal light/mid/dark facet regions, rock and cave tones, and the darker violet cast in the cave.
  - The parts carry a custom property `m011_offset` (their placement in the build frame). It is authoring data only.

### Stage 1 fixes (after verifier round 1)

Verifier round 1 failed the model (6/10). The user then gave the governing direction: "the geode should pretty much look
like a hollowed out stone/rock with amethyst in it". Where the two conflict, the user's direction wins.

The model now reads as **one faceted stone boulder, hollowed out**: a thick rounded lip round the opening, a low
rounded front lip, and the crystals growing in the hollow. There are no slabs, columns, tub or pebble blocks, and no
seam between the shells. The top and bottom shells stay the sheet's exploded pieces; in the hero they are one
continuous stone.

1. **Dome crown (finding 1).** There is no radial pole now.
   - The outer sheet's first row keeps every other column (a ring of 9), fanned from the second row.
   - Inside the ring, 3 crown verts (`CAP`, `CAP_F` 0.16) and one broad triangle between them close the dome.
   - Strongly bent quads now take the diagonal that keeps a ridge (`_split_pick`). A random diagonal had folded some
     into valleys, which showed as dark slits on the dome. The random pick remains only where a quad is within 0.04
     studs of flat.
   - Outer valleys of 25° or more on the top shell went from 7 (up to 78°) to 2 (31° and 28°).
   - The crown's random draws use their own stream, so the rest of the shell keeps its layout.
2. **Front (finding 2) and the front-left pebbles (finding 5).** All 9 slabs are gone, along with the base plate.
   - `bottom_raw` is now one convex rock, the lower half of the same egg.
   - Behind the mouth, its top ring is exactly the top shell's contact ring. Just below it the egg is near-vertical
     (no crease), then it tucks in towards the ground.
   - In front of the mouth it is the hollow's low front lip:
     - the lip's top (`FRONT_Z`) is at 3.3, about 35 % of the height, with an uneven ±0.2 top edge;
     - it is drawn in to 0.86 over a bevel ring, so the edge is rounded;
     - its shoulders rise over several facets to the arch's feet.
   - Five broad low bulges (`BULGES`) give the sheet's base lumps as big facets of the one rock.
3. **Hollow (finding 3).** `bottom_cutter` is a shallow rocky bowl.
   - The walls slope from the cave's own outline at the contact plane, through an irregular middle ring (0.86) at
     z 2.6, to a small flat seat (0.62) at z 1.6.
   - At the front the inside leans back further (y ≥ −1.0 / −1.65 / −2.3 by height), so the front lip is thick and its
     inside slopes.
   - The tub's vertical walls and the end blocks are gone. The "ends higher than the back" from the exploded sheet was
     not kept: a flat contact plane all round is the sheet's own rule, and the user's one-rock direction wins.
4. **Exploded view (finding 4).** `render_views` lays out four crystals: `AmethystShard` plus three temporary linked
   copies (chunky leaning, slim leaning and small; `EXPLODED_CRYSTALS`), removed after the shot.
   `AmethystShard` stays the one reusable part.
5. **Crystals.** The side crystals now lean out less, so they stay inside the rock's outline:
   - Left: (−0.4, −0.3);
   - Right: (0.38, −0.28);
   - FarRight: x 2.85, lean (0.3, −0.18);
   - the small Front crystal moved back to y −0.95, off the front lip.

The stage 2–6 code is unchanged and runs on the new shape: `_clean`/`_desliver`, `UV`, the stage 4 colour passes,
`STUDIO_LIGHT`, and the `_vfx` sockets.
- The cave light socket sits at hero-local (0.03, −0.02, 3.2). It is 0.96 studs clear of every surface (BVH check),
  outside the solid.
- The hero's footprint changed, so its offset changed. The light keeps its build-frame point in the cave.

**Measured (MCP audit after `m011.build()`, saved):**

| Object | Tris | Shells | Non-manifold / boundary / wire / loose | Zero-area / dup verts / n-gons | Normals | Size (studs) |
| --- | --- | --- | --- | --- | --- | --- |
| Amethyst | 812 / 4000 (was 1282) | 1 | 0 / 0 / 0 / 0 | 0 / 0 / 0 | outward | 10.40 × 8.91 × 9.45 |
| AmethystShellTop | 304 / 1000 | 1 | 0 / 0 / 0 / 0 | 0 / 0 / 0 | outward | 10.40 × 6.23 × 5.25 |
| AmethystShellBottom | 178 / 1000 (was 586) | 1 | 0 / 0 / 0 / 0 | 0 / 0 / 0 | outward | 10.40 × 8.91 × 4.20 |
| AmethystShard | 36 / 1000 | 1 | 0 / 0 / 0 / 0 | 0 / 0 / 0 | outward | 2.43 × 2.00 × 5.20 |

- Origins are at the bottom centre and transforms are applied.
- UVs: no overlaps, minimum gap 0.016.
- `K.check` reports no problems.
- The hero keeps its 4 VFX sockets.
- 28 orphaned M011 meshes were removed, and the .blend was saved through the MCP.
- **Sliver pass:** `_clean` left 4 slivers (< 5°) on the bottom shell and 9 on the hero, with 0 specks. They are thin
  strips where the crystals meet the seat; stage 2 can look at them.
- **Width:** the hero is now 10.4 wide, down from 11.8, because the slabs that stuck out past the egg are gone. W:H is
  1.10 (sheet front view 1.17) and D:H is 0.94 (sheet 0.89).

### Stage 1 fixes (after verifier round 2)

Verifier round 2 failed the model at 6.5/10 on shape alone; the technical checks passed and the colour was close.
These fixes keep the user's direction: one continuous rock, "a hollowed out stone/rock with amethyst in it". The
stage 2–6 code (`_clean`/`_desliver`/`_flip_free`, `_drop_unused`, UV, the colour passes, `STUDIO_LIGHT`, `_vfx`) runs
unchanged on the new shape.

1. **Mouth (findings 1 and 2).**
   - The opening now faces up as well as forward. `MOUTH_LEAN` goes from +10° (leaning forward) to −14° (leaning back),
     so it is tilted up 24°.
   - The opening is set back: the mouth passes the contact plane at y 1.4 (was 0.05), just behind the egg's widest
     section.
   - New `MOUTH_CURVE` (0.08 × x²): the mouth surface (`_mouth_d`) bends back at the sides, so the hood's sides are cut
     back and up.
   - The inner x radius is 4.1 (was 3.85), giving side walls of about 1.1 and an opening of about 80 % of the width.
   - **Rear three-quarter:** the crystals and the lip now show past the hood's cut-back flank.
   - **Top view:** the rim ring with the crystals inside.
   - All mouth tests (`_in_hood`, `_contact_ring`, `_clip_behind_mouth`, `_front_of_mouth`, the lip shoulders) go
     through `_mouth_d`.
   - The pole moved to (0, 0.6, 0.8), so it stays inside the smaller hood.
   - `COLS` is now 24 (was 18). The wider mouth took most of the 18 and left the back too coarse.
2. **Cave ceiling.** The cave pole fan became visible through the tilted-up mouth as a radial star. The inside sheet
   now closes with the same crown as the outside, via the new helper `_crown`: a ring of 12, 3 crown verts and one
   broad facet.
3. **Front lip (finding 3).** The lip is now a low crescent.
   - Its top (`_lip_z`) is 2.6 in the middle (29 % of the height in the front view, was about 44 %). It rises to 3.4 at
     the sides (power 1.6) and is lumpy (±0.1).
   - A V notch, cut in rock by a second hull in `bottom_cutter` (`NOTCH`), takes the middle down to 2.2.
   - The shoulders fall away fast from the arch's feet, so there is no flat ledge beside the cut-back hood.
   - The side and front crystals are longer, so their prism bodies show over the lip:
     - Left sz 1.02 → 1.25;
     - Right 0.96 → 1.2;
     - FarRight 0.84 → 1.05;
     - Front 0.5 → 0.78 (y −1.0, lean −0.5).
4. **Bottom-shell part (finding 4).** It is no longer a deep pot. The front drops to 2.2 at the notch and about 2.6
   beside it, with high ends rising to the contact plane at the back and the arch's feet.
5. **Exploded camera (finding 5).** The exploded shot is now taken from 30° elevation (was 14°), looking down on the
   top shell's dome.
   - The top shell is raised to z 11.6.
   - The four crystals float 1.2 higher, clear of the bowl.
6. **Rear feet (finding 6).** The two rear `BULGES` are now two-point lumps at radius scale 1.14–1.15 (was one point at
   1.06). The egg's lower half follows the dome's own superellipse (`EGG_LOW` 6.0), down to about 0.78 of the width at
   the ground. The lumps stand out at the rear corners, and the base reads as an egg, not a pot.
7. **No seam round the rear.** Three causes of a belt at the contact plane were removed:
   - The hood's bump noise now fades in as (1.6·d.z)² instead of 4·d.z.
   - The outside's row just above the rim gets the small rim jitter.
   - Each column's middle rows slide ±7 % along the surface (`ROW_SLIDE`), so no row runs round as one level line.

   Below the contact ring the bottom shell drops vertically for 0.6 first, then follows the egg curve.
8. **Thin faces.**
   - The bottom shell's hull is merged within 2° and re-split BEAUTY.
   - `_clean` now uses `CLEAN_MOVE` = 0.18 (was 0.1) on the bottom shell and the hero. The round-2 carve left needles
     with 0.28–0.35-stud short edges, which a 0.1 move can't collapse. 0.18 is still far below anything that reads on
     screen.

**Measured (MCP, after `m011.build()`, saved):**

| Object | Tris | Shells | Non-manifold / boundary / wire / loose | Faces < 3° / < 5° (min) | Size (studs) |
| --- | --- | --- | --- | --- | --- |
| Amethyst | 974 / 4000 | 1 | 0 / 0 / 0 / 0 | 0 / 5 (3.56°) | 10.38 × 8.81 × 9.11 |
| AmethystShellTop | 398 / 1000 | 1 | 0 / 0 / 0 / 0 | 0 / 1 (3.61°) | 8.87 × 3.07 × 4.91 |
| AmethystShellBottom | 212 / 1000 | 1 | 0 / 0 / 0 / 0 | 0 / 2 (3.56°) | 10.38 × 8.81 × 4.20 |
| AmethystShard | 36 / 1000 | 1 | 0 / 0 / 0 / 0 | 0 / 0 (21.1°) | 2.43 × 2.00 × 5.20 |

- No zero-area faces, duplicate vertices or n-gons. Normals outward, origins at the bottom centre, transforms applied.
- UVs: no overlaps, minimum gap 0.016. `K.check` reports no problems.
- Sockets: the `crystal_glow` light sits at hero-local (−0.01, 0.03, 3.2). It is outside the solid and 0.96 studs from
  the nearest surface. It now stands in the open bowl behind the main crystal rather than under a hood.
- The three `ore_glint` box centres are inside the crystal tips, as stage 6 designed.
- No temporary objects or orphaned meshes are left.

**Left for the other stages:**
- **Stage 4:** re-check the cave colour bands and the seat bleed on the new open shape. The cave is shallower, and
  more of the inside now shows from the front and top.
- **Stage 6:** the spec's socket table positions are stale.

#### Amended after the coordinator's review of round 2

The round-2 mouth overshot. Leaning it back 14° and cutting it back to y 1.4 turned the rock into a chair-back: a thin
back wall with the crystals out in the open. The sheet's side and front three-quarter views take priority, and the
user's direction governs. **Items 1, 7 and 8 above are superseded as follows; items 3–6 stand.**

- **Mouth faces the front again.**
  - `MOUTH_FOOT` y is 0.0 (was 1.4) and `MOUTH_LEAN` is +4°, a slight forward hood (was −14°).
  - `MOUTH_CURVE` is 0.022 (was 0.08). It bends the sides back just enough that a few crystal tips show past the
    hood in the rear three-quarter view, while the arch's feet stay in front of the egg's widest section. So the
    rear view has no notches.
  - `INNER` x is 3.95: the opening is about 75 % of the width, a tall round arch, with side walls about 1.25 thick.
  - **Side view:** the dome comes forward over the crystals.
- **Crystals inside the hollow.** The whole cluster moved 0.5 back (Main y −0.55), so the dome's top sits over its
  middle. FarRight leans out a little more (0.42, −0.3); it supplies the tips seen in the rear three-quarter view.
- **No seam, notch or valley on the rear and the dome.**
  - The bottom shell's first two rings below the contact plane (z 3.5 and 2.6) sit on the contact points' own
    azimuths, on the egg curve (`_egg_low`). A ring of other azimuths there made a sawtooth of shading that read as a
    seam.
  - `BUMP` is 0.035 (was 0.07). At 0.07 one crown vertex sank 0.35 below its neighbours, a 49° valley on top of the
    dome.
  - The crown's outer cap verts sit 2.5 % proud of the surface, and its ring strip takes the ridge diagonal
    (`_split_pick`).
- **Calm cave ceiling.**
  - The inside sheet's jitter is 0.03 (`JITTER_CAVE`, was 0.13).
  - Its lumps are 0.3 of the outside's (`INNER_BUMP`).
  - It is closed by the broad-facet crown (`_crown`).
- **Cave light re-placed.** The cluster's move left stage 5/6's point 0.41 stud from the main crystal.
  - `CAVE_LIGHT` is now the most open point of the cave (BVH search): build frame (0, 1.75, 4.8), hero-local
    (−0.02, 1.26, 4.8), 1.74 studs clear of every surface. `STUDIO_LIGHT.pos` was updated to match.
  - In Roblox axes that is (0.0, 4.8, −1.26). Colour, brightness, range and shadows are unchanged.
- **Kept from round 2:** the lumpy front lip with its V-dip, the longer side crystals with their bodies showing, the
  low-front bottom-shell part, the exploded camera at 30°, the rear foot lumps, `COLS` 24, the cave crown and
  `CLEAN_MOVE`.

**Measured (MCP, after `m011.build()`, saved):**

| Object | Tris | Shells | Non-manifold / boundary / wire / loose | Faces < 3° / < 5° (min) | Size (studs) |
| --- | --- | --- | --- | --- | --- |
| Amethyst | 968 / 4000 | 1 | 0 / 0 / 0 / 0 | 0 / 1 (4.05°) | 10.36 × 8.81 × 9.44 |
| AmethystShellTop | 398 → 386 / 1000 | 1 | 0 / 0 / 0 / 0 | 0 / 0 (11.6°) | 10.40 × 5.78 × 5.24 |
| AmethystShellBottom | 214 / 1000 | 1 | 0 / 0 / 0 / 0 | 0 / 0 (5.81°) | 10.40 × 8.81 × 4.20 |
| AmethystShard | 36 / 1000 | 1 | 0 / 0 / 0 / 0 | 0 / 0 (21.1°) | 2.43 × 2.00 × 5.20 |

- No zero-area faces, duplicate vertices or n-gons. Normals outward, origins at the bottom centre, transforms applied.
- UVs: no overlaps, minimum gap 0.016. `K.check` reports no problems. No temporary objects are left.
- Glint box centres sit inside the crystal tips, as stage 6 designed.

**Views against the sheet:**
- **Side:** a hood over the crystals, as on the sheet.
- **Front three-quarter:** a hollowed boulder with a thick rounded lip and crystals in the hollow over the lumpy front
  lip.
- **Front:** a tall round arch, the V-dip, and the side crystals' bodies showing.
- **Rear three-quarter:** a big rounded boulder with a few crystal tips past the hood edge.
- **Rear:** one faceted egg with corner lumps, no notches and no crease.
- **Top:** the dome, with the crystals showing at the front. The sheet's top view conflicts with its side view; the
  side view wins.
- **Exploded:** the top shell seen from above, four crystals floating clear, and a low-front bowl.

### Stage 1 fixes (after verifier round 3)

Verifier round 3 failed the model at 6.5/10. The front, front three-quarter and side views already read as "a
hollowed-out stone with amethyst in it"; the blockers were shape. The round-3 mouth stays: it faces the front, and the
dome comes over the crystals in the side view. The user's direction still governs. Stage 2–6 code runs unchanged on
the new shape (stage 4's palette, stage 6's glints, the light).

1. **Rear three-quarter shows the cluster.**
   - The mouth now bends back more the higher it goes (`MOUTH_CURVE_UP` 0.07, full from 3 studs above the contact
     plane; see `_mouth_d`). The hood's upper flanks are cut back, while the arch's feet and the dome's centre stay
     where they were, so the rear view gains no notches and the side view keeps its hood.
   - The right pair of crystals lean further out and forward (Right (0.46, −0.32); FarRight (0.55, −0.38), now 0.88 ×
     1.2).
   - Measured along the rear three-quarter camera's screen-left direction, the crystals now reach up to 2.2 studs past
     the stone between z 3 and 6 (was about 0.9). In the 152° render the cluster shows clearly past the hood's flank,
     and the lip's right end shows at its foot.
   - The hero is 11.05 wide now (was 10.36), because FarRight leans out past the rock.
2. **Rear foot lumps.**
   - Two broad, low foot lumps (`FootL`/`FootR`, 3.6 × 3.2 × 1.8–1.9) are unioned into the egg at the rear corners.
     Each has a real concave crease above it, where the union meets the egg.
   - The egg tapers in harder at the base (`EGG_LOW` 5.2, about 0.66 of the width at the ground), so the base reads
     as the egg standing on two feet.
   - The old rear `BULGES` hull points are gone.
3. **Front lip: lumpy rock, not pebbles.**
   - Four broad, chunky bulges (`LipL`, `LipCL`, `LipCR`, `LipR`, each 3.3–3.6 wide, 2.75–3.05 high) are unioned
     into the egg. They overlap each other and are buried in the egg, so only their fronts stand a few tenths proud.
     The creases between them are real seams, and the lip reads as one lumpy rock.
   - The V-dip sits between the middle two.
   - The lip is about 30 % of the height.
   - A first try with smaller, prouder lumps read as the rejected "row of pebbles", so the lumps were made bigger and
     buried deeper.
   - The egg's own lip under them is lowered to 2.5, so the bulges carry the silhouette.
4. **Bottom-shell part.**
   - The hollow is now a long, low trough: the seat is drawn out sideways (0.8 × 0.55 of the cave) and so is the
     middle ring (0.95 × 0.8). The back is raised (contact plane) and the front is open and low (2.75–3.05, V-dip 2.2).
   - The V notch now runs right through into the hollow (`NOTCH`, back to y 1.0). Stopping at y −1.2 it had left a
     thin slit.
   - **Horns not adopted.** Horn lumps at the trough's ends, rising past the contact plane, were tried. In the hero's
     side view they stood as a columnar block under the crystals, the round-1 fault. So the ends are the egg's own
     shoulders, rising to the arch's feet.
5. **Light socket.** The hero's footprint grew to the right, so its offset moved. The light keeps its build-frame point
   in the cave: hero-local (−0.36, 1.21, 4.8), still 1.74 studs clear of every surface (BVH). Stage 5's documented
   `STUDIO_LIGHT.pos` (0.0, 1.26, 4.8) is therefore about 0.36 off in x. The built socket is authoritative.

**Measured (MCP, after `m011.build()`, saved):**

| Object | Tris | Shells | Non-manifold / boundary / wire / loose | Faces < 3° / < 5° (min) | Size (studs) |
| --- | --- | --- | --- | --- | --- |
| Amethyst | 1334 / 4000 | 1 | 0 / 0 / 0 / 0 | 0 / 3 (3.9°) | 11.05 × 8.72 × 9.43 |
| AmethystShellTop | 386 / 1000 | 1 | 0 / 0 / 0 / 0 | 0 / 2 (4.91°) | 10.38 × 5.78 × 5.23 |
| AmethystShellBottom | 594 / 1000 | 1 | 0 / 0 / 0 / 0 | 0 / 1 (3.9°) | 10.38 × 8.72 × 4.20 |
| AmethystShard | 36 / 1000 | 1 | 0 / 0 / 0 / 0 | 0 / 0 (21.1°) | 2.43 × 2.00 × 5.20 |

- No zero-area faces, duplicate vertices or n-gons. Normals outward, origins at the bottom centre, transforms applied.
- UVs: no overlaps, minimum gap 0.016. `K.check` reports no problems. No temporary objects are left.
- All five sockets are present. The glint box centres sit inside the crystal tips, as stage 6 designed.

**Views against the sheet:**
- **Front three-quarter:** a hollowed boulder with a thick rounded lip and the crystal fan in the hollow. The front
  lip is lumpy rock with creases, not separate stones.
- **Front:** a tall round arch; four broad bulges with the V-dip under the small front crystal; the side crystals'
  bodies show.
- **Side:** the dome comes forward over the crystals. The crystals and the lip stand forward of the hood's foot.
- **Rear three-quarter:** a big rounded boulder with the crystal cluster clearly past its left flank.
- **Rear:** one faceted egg on two creased foot lumps, tapering in between them. No notches.
- **Top:** the dome, with the crystals at the front (the sheet conflict, as before).
- **Exploded:** the top shell from above, four floating crystals, and a long low trough.
- **Left for later:**
  - stage 4 may want to check the foot lumps' weathering (one renders as a cool-grey patch);
  - stage 5/6 may want to refresh the documented light position.

## Stage 2 — Optimisation and cleanup

All changes are in `m011.py`, rebuilt through the MCP with `m011.build()`. This section was redone on stage 1's
one-rock reshape (after verifier round 1); the slab-era numbers it replaces are gone.

### What stage 2 put in place (still in the builder)

- **The arch's feet sit flat (`_put_down`, `FOOT = 0.5`).** The two arch-foot columns leave the hood just above the
  contact plane; their rim points slide down the mouth plane onto z 4.2, and `_contact` uses the same rule, so the
  hood's whole ring sits on the bottom shell with no wedge-shaped crack (the crack's tip was a non-manifold pinch).
- **Flat contact ring dissolved.** The collinear lip vertices in the middle of the hidden contact ring are dissolved
  (one quad per column), and the two end gaps are fanned by `_fan` with no zero-area triangles.
- **No sink: an exact coplanar join (`hero`, `_self_union`).** The top shell is pasted at its true height and its ring
  vertices snapped onto their twins in the bottom shell. Contact faces with identical corners on both shells cancel
  and are deleted as pairs; one exact boolean union with self-intersection then joins the shells and all 7 crystals.
- **Sliver pass `_clean` / `_desliver`** (bottom shell after its carve, hero after its union): dissolve two-edge
  crease points, triangulate every quad and n-gon (BEAUTY), then remove thin faces with no vertex moving more than
  0.1 stud and no neighbour flipping or folding; the ground and contact planes stay flat and the contact ring points
  never move.

### Changed in this pass

- **`_flip_free` (new, in `_desliver`).** The thin faces left on the new shape were not needles or shallow caps but
  long facets and strips on flat faces, which the old paths skip. Such a face now flips whichever of its edges gives
  the best pair of triangles when:
  - the flip moves the surface by at most 0.02 stud (the distance between the old and new diagonal, 0 on a flat face);
  - both new triangles face the same way;
  - the worse triangle gets better;
  - not all four corners are pinned contact-ring points.
  - Result: hero faces under 5° went from 9 to 4, and bottom-shell faces from 4 to 2.
- **`_drop_unused` (new, end of `build()`).** Every rebuild orphans the previous meshes and leaves the colour pass's
  unused mix keys at zero users. The builder now removes those itself and names each mesh after its object.
  - This build dropped 8 meshes and 4 materials: `FB_m011_crystal_dark_x_crystal_mid_75` and
    `FB_m011_rock_x_seat_glow_75` (the verifier's two), plus `FB_m011_cave_deep_x_seat_glow_25` and
    `FB_m011_rock_x_seat_glow_50`.
  - Afterwards no M011 material has zero users and no M011 mesh is orphaned. Materials are created on demand (`flintkit.material`), so a key that comes back into use is recreated.
- **`m011_offset` stays.** `export_kit_roblox.py` exports each piece from a fresh bmesh object with
  `export_extras=False`, and its manifest reads only `kit_*`, `tris` and VFX keys; `export_lobby_roblox.py` also has
  extras off and `build_lobby.py` copies only socket keys. So the property never leaks, and the hero assembly and
  `render_views` need it.

### Measured (MCP audit of the saved file)

| | Amethyst (hero) | AmethystShellTop | AmethystShellBottom | AmethystShard |
| --- | --- | --- | --- | --- |
| Tris / budget | 812 / 4000 | 304 / 1000 | 178 / 1000 | 36 / 1000 |
| Faces / verts | 812 / 408 | 304 / 154 | 178 / 91 | 36 / 20 |
| Quads / n-gons | 0 / 0 | 0 / 0 | 0 / 0 | 0 / 0 |
| Shells | 1 | 1 | 1 | 1 |
| Non-manifold / boundary / wire / loose | 0 / 0 / 0 / 0 | 0 / 0 / 0 / 0 | 0 / 0 / 0 / 0 | 0 / 0 / 0 / 0 |
| Zero-area faces / min face area (sq studs) | 0 / 0.0027 | 0 / 0.168 | 0 / 0.135 | 0 / 0.203 |
| Min angle | 3.59° | 8.89° | 3.63° (was 3.55°) | 21.1° |
| Triangles < 3° / < 5° | 0 / 4 (was 0 / 9) | 0 / 0 | 0 / 2 (was 0 / 4) | 0 / 0 |
| Interior or inward tris (winding test) | 0 | 0 | 0 | 0 |
| Self-intersections | 0 | 0 | 0 | 0 |
| Signed volume | +352.72 | +108.24 | +204.04 | +11.84 |
| Duplicate verts (1e-4) / custom normals / smooth faces | 0 / no / 0 | 0 / no / 0 | 0 / no / 0 | 0 / no / 0 |
| Origin offset (bottom centre) | 0, 0, 0 | 0, 0, 0 | 0, 0, 0 | 0, 0, 0 |
| Rotation / scale | 0 / 1 | 0 / 1 | 0 / 1 | 0 / 1 |
| Size (studs) | 10.40 × 8.91 × 9.45 | 10.40 × 6.23 × 5.25 | 10.40 × 8.91 × 4.20 | 2.43 × 2.00 × 5.20 |
| Material slots (all used) | 26 | 8 | 9 | 6 |
| Modifiers / UV map / `tris` property | 0 / UVMap / matches | 0 / UVMap / matches | 0 / UVMap / matches | 0 / UVMap / matches |

- `K.check` reports no problems. The hero keeps its 4 VFX sockets (see stage 6).
- **What the winding test checks:** a point just in front of every triangle has winding number 0, and one just behind
  it has 1. That rules out interior or hidden faces left by the unions, and inward normals.
- **Silhouette unchanged.** Surface deviation from the build before this pass: hero ≤ 0.0066 stud; parts 0. The flips
  bend the surface by at most 0.02 stud by construction. Sizes are identical, and the renders match view for view.

### Thin faces left (none under 3°)

| Object | Where | Min angle | Why it stays |
| --- | --- | --- | --- |
| Hero | rock at the front-right lip shoulder, where the hood's foot meets the lip | 3.59° | flipping gives 0.85°; collapsing needs a move over 0.1 |
| Hero | a crystal face cut by another crystal (front) | 3.82° | the cut line has collinear points; flipping gives 0° |
| Hero | a crystal body face across a crystal edge (front right) | 4.62° | the flip would bend the surface 0.07 stud across a 38° edge |
| Hero | the seat round the crystal feet | 4.95° | flat, but every flip makes the pair worse |
| Bottom | two flat contact-plane strips near the left foot | 3.63°, 4.82° | flipping makes them worse; their corners are pinned ring points |

All have areas of 0.07 sq stud or more: these are long thin facets, not degenerate slivers.

### Left for later stages

- Stage 4's colour re-measure table (§6) and its tint-cluster counts (§7) were taken on the slab model. They name
  slab regions that no longer exist; stage 4 or the verifier should re-measure them on the one-rock shape.
- Mesh data is clean after every build (`_drop_unused`). The `T_Calib*` orphans in the file are calibration meshes,
  not M011's. They have no users and aren't saved.

## Stage 3 — UV

Changes are in `kit_models.py` (generic) and `m011.py`. The rebuild ran through the MCP with `m011.build(render=False)`: UVs don't show in the renders, so stage 2's renders still stand.

### What was wrong (stage 2 build: Smart UV at 66°, `island_margin` 0.008)

| | Amethyst | ShellTop | ShellBottom | Shard |
| --- | --- | --- | --- | --- |
| Islands | 130 | 20 | 44 | 5 |
| Overlapping triangle pairs (all inside one island: folds) | 14 | 0 | 31 | 0 |
| Min gap between islands | 0.0109 | 0.0053 | 0.0069 | 0.0027 |
| Texel density per island, min / median / max (× mesh average) | 0.48 / 0.99 / 1.17 | 0.68 / 0.91 / 1.13 | 0.59 / 0.95 / 1.14 | 0.90 / 1.03 / 1.13 |
| Worst conformal stretch (σmax/σmin) | 2.42 | 1.73 | 2.12 | 2.26 |
| Worst area stretch | 2.07 | 1.51 | 1.87 | 1.76 |
| Worst corner-angle change | 48.9° | 22.9° | 35.1° | 41.2° |

- Smart UV only projects: a face up to 66° off its island's axis is squashed by up to 1/cos 66° ≈ 2.5.
- On the bottom shell's slabs and the hero's crevices, it also folded islands over themselves.
- `island_margin` is not an absolute gap in Blender 5.2's default (SCALED) margin method. Gaps came out from 0.0027 to 0.011, three of the four under the 0.008 target.

### What changed

- **`kit_models.smart_uv`:**
  - It packs with `margin_method="FRACTION"`, so the margin is exact: `margin` round each island. The gap between islands is 2 × margin (0.016), and the gap to the 0–1 border is the margin (0.008). This is a generic fix: the docstring always promised this gap.
  - New optional `method` (`"ANGLE_BASED"`, `"CONFORMAL"` or `"MINIMUM_STRETCH"`):
    - Smart UV's island borders become seams (`seams_from_islands`), and each island is re-unwrapped by that method.
    - The unwrap's own pack gives every island the same texel density.
    - If an unwrap folds an island, the angle drops by 10° (not below 25°) and it runs again.
  - The default (no `method`) is still plain Smart UV at 66°, so other models only gain the exact margin.
  - `smart_uv` now returns `uv_stats`.
- **`kit_models.uv_stats(o)`:** a new generic measurement that stage 3 and stage 7 can use. It reports:
  - islands;
  - overlapping triangle pairs (and how many cross islands);
  - flipped triangles;
  - the minimum gap between islands' boundary edges, and the margin to the border;
  - texel density per island, as min / median / max of (UV area ÷ 3D area) against the mesh average;
  - worst and 95th-percentile conformal stretch (the singular-value ratio of the 3D → UV map), worst area stretch, and the worst corner-angle change.
- **`kit_models.finish(o, uv=…)`:**
  - `uv` takes `True` (the defaults), a dict of `smart_uv` arguments, or `False`.
  - The audit carries the result under `"uv"`.
- **`m011.py`:** `UV = dict(angle=45.0, method="ANGLE_BASED", margin=0.008)` is passed to `finish` for the three parts and the hero. 45° with angle-based unwrapping was chosen from a sweep on copies of each object.

| Sweep (worst conformal stretch / overlap pairs / islands) | Amethyst | ShellTop | ShellBottom | Shard |
| --- | --- | --- | --- | --- |
| Smart 66° (old) | 2.42 / 14 / 130 | 1.73 / 0 / 20 | 2.12 / 31 / 44 | 2.26 / 0 / 5 |
| Smart 66° + angle-based | — | 1.15 / 0 / 20 | 1.43 / 21 / 44 | 1.17 / 0 / 5 |
| Smart 66° + minimum stretch | — | 1.54 / 0 / 20 | — | 1.19 / 0 / 5 |
| Smart 55° + angle-based | 1.18 / 7 / 163 | 1.08 / 0 / 30 | 1.17 / 0 / 89 | 1.00 / 0 / 8 |
| **Smart 45° + angle-based (chosen)** | **1.08 / 0 / 270** | **1.08 / 0 / 40** | **1.04 / 0 / 99** | **1.00 / 0 / 9** |
| Smart 35° + angle-based | 1.06 / 0 / 278 | 1.05 / 0 / 71 | 1.02 / 0 / 122 | 1.00 / 0 / 16 |

- At 45°, every object is overlap-free. Going to 35° gains at most 0.03 of stretch for up to 1.8× the islands.
- Minimum-stretch (SLIM) was worse than angle-based on every part.
- Seams (`use_seam`) are marked on the island borders of all four meshes. On the current one-rock shape (re-measured
  after stage 2's redo): hero 460, top 153, bottom 96, shard 27 edges. The sweep above was run on the slab model.

### Measured (MCP, `M.uv_stats`; re-measured on the one-rock shape after stage 2's redo, saved file)

| | Amethyst (hero) | AmethystShellTop | AmethystShellBottom | AmethystShard |
| --- | --- | --- | --- | --- |
| UV layer | UVMap | UVMap | UVMap | UVMap |
| Islands | 118 | 36 | 22 | 9 |
| Overlapping tri pairs (cross-island) | 0 (0) | 0 (0) | 0 (0) | 0 (0) |
| Flipped tris | 0 | 0 | 0 | 0 |
| Min gap between islands | 0.016 | 0.016 | 0.016 | 0.016 |
| Margin to the 0–1 border | 0.008 | 0.008 | 0.008 | 0.008 |
| Texel density per island, min / median / max | 1.000 / 1.000 / 1.000 | 1.000 / 1.000 / 1.000 | 1.000 / 1.000 / 1.000 | 1.000 / 1.000 / 1.000 |
| Texels per stud at 1024² | 26.3 | 43.7 | 37.5 | 131.9 |
| UV space used | 33.5 % | 36.0 % | 36.0 % | 48.4 % |
| Worst / p95 conformal stretch | 1.066 / 1.038 | 1.081 / 1.036 | 1.063 / 1.031 | 1.000 / 1.000 |
| Worst area stretch | 1.079 | 1.092 | 1.052 | 1.000 |
| Worst corner-angle change | 3.4° | 3.1° | 2.9° | 0.0° |

- **Geometry is unchanged:**
  - The vertex, face and material-index hashes of all four meshes are identical before and after.
  - The Tint hashes are identical.
  - Tris, sizes, shells and locations are unchanged.
  - `K.check` reports no problems.
- **Housekeeping:**
  - The rebuild's 14 orphaned M011 meshes were removed, and the mesh datablocks renamed back to their objects' names.
  - The .blend was saved through the MCP.
  - (Since stage 2's redo, `build()` drops zero-user M011 materials and orphaned meshes itself: `_drop_unused`.)

### Which UVs reach Roblox

- `export_kit_roblox.py` does not export this UV layer.
- For each asset it re-reads the triangles (positions, material slot and per-corner `Tint`) and builds a fresh bmesh for each piece, with a new `UVMap`.
- **Solid faces:** every corner of a triangle gets the same UV, the centre of that face's `palette.png` cell (`cell_uv(row, level, height)`).
  - The row is the material's colour, from `flintkit_key`/`flintkit_hex`.
  - The column is the nearest of up to 32 Tint levels to the triangle's mean Tint.
  - Cells are 16 px, so each triangle samples one flat texel, and seams or margins in the authored UVs can't bleed into it.
- **Glow faces** (emission ≥ 1) become Neon parts that carry `color`. **Water** gets box-projected UVs. M011 has neither.
- **So colours survive.**
  - They come only from the three materials' `flintkit_hex` (rock #9E8F8B, cave #857774, crystal mid #924EC3, all placeholders until stage 4) and the Tint attribute. Both carry through unchanged.
  - The `UVMap` authored here is for FBX/OBJ export and any future texture or bake work: clean, no overlaps, even density.

### Left for later stages

- **Stage 4:** the Tint/colour work doesn't depend on these UVs, and changing colours needs no re-unwrap.
- **Geometry changes:** a stage that changes the geometry re-runs this unwrap automatically through `finish(uv=UV)`. Re-check with `M.uv_stats`.
- **Other models:** `smart_uv`'s new exact margin applies to them the next time they are rebuilt. Their default stays plain Smart UV at 66°. Passing `uv=dict(angle=45, method="ANGLE_BASED")` would remove the same 1.7–2.4× projection stretch there.

## Stage 4 — Materials, colour and texture

All colour work is in `m011.py`: `palette()` and the "stage 4" section (`_Paint`, `_grade`, `_mottle`,
`_stone_colour`, `_crystal_light`, `colour_part`). It runs on the **finished** part meshes (after cleanup and UVs)
and on the hero after its finish. It edits only material indices and the `Tint` attribute.

Geometry and UVs are unchanged from stage 3. The vertex count, face count, vertex-position sum and UV sum of all four
meshes are identical. (Counts now, on the one-rock shape, re-measured after stage 2's redo: hero 408 v / 812 f,
top 154 / 304, bottom 91 / 178, shard 20 / 36; 23 palette keys in use across the four objects after the round-1 fixes, none emissive.)

### 1. Sampled targets (master sheet `references/011.png`)

Swatches (`M.raw_sample`, flat): light #BF97DD, mid #924EC3, dark #5F328A, rock #9E8F8B.

The rendered sheet is far more saturated than the crystal swatches, so the targets are the rendered regions:
- stone: `M.sample`'s mask (sat < 0.25);
- vivid: the `K.sample` vivid mask (sat > 0.35);
- paper pixels dropped in both.

Boxes are in sheet pixels (x0, y0, x1, y1).

| Region | Box | Kind | Median | Lit (top 25 %) | Shade (low 25 %) |
| --- | --- | --- | --- | --- | --- |
| Rock, front three-quarter view, all | 40,130,490,470 | stone | #9F8C89 | #CAB1A6 | #736869 |
| Rock, rear three-quarter dome (warm, lit) | 720,150,940,420 | stone | #A99188 | #C9AEA1 | #887369 |
| Rock, hood's left side (cool grey) | 60,165,155,340 | stone | #948888 | #B39892 | #756B6D |
| Rock, front slab tops | 100,345,280,400 | stone | #B69E97 | | |
| Rock, slab foot by the ground | 100,410,280,460 | stone | #8B7770 | | |
| Rock, rear view upper / lower band | 560,560,740,640 / 560,690,740,735 | stone | #AA958F / #84716B | | |
| Cave interior (f34, ceiling + right wall) | 240,150,420,250 | cave* | #3E2839 | #65415E | #2B1C28 |
| Cave interior (front view, top) | 100,560,240,600 | cave* | #482D42 | | |
| Crystal, main, tip | 265,185,330,240 | vivid | #C064F7 | | |
| Crystal, main, body | 255,245,335,330 | vivid | #943ACA | | |
| Crystal, main, lower body | 260,330,330,385 | vivid | #6925A7 | | |
| Crystal, small back one (deep in the cave) | 338,262,372,300 | vivid | #682B87 | | |
| Crystals, f34 all | 40,130,490,470 | vivid | #7F37BA | #C666F6 | #3C203F |
| Violet bleed on the stone at the crystal seat (close-up) | 683,885,843,935 | tinged** | #976D88 | #AF8799 | #6D4664 |
| Exploded top shell: outside | 100,830,400,880 | stone | #C1AA9D | | |
| Underside view: inside | 650,1030,860,1100 | stone | #6E5C55 | | |
| Exploded bottom shell | 60,1140,430,1300 | stone | #8C7872 | | |

\* cave mask: max < 150, sat < 0.6.
\** tinged mask: 0.12 ≤ sat < 0.5, blue > green + 8, 90 < max < 215.

What the sheet shows:
- **Rock:** lit rock is warm pinkish-beige and its shade cool grey. The rock is darker and browner at the foot.
- **Parts:** the exploded parts (top shell, bottom shell, its underside) are **bare stone with no violet**; the inside
  is just in shadow.
- **Violet:** the violet in the cave and at the crystal seat appears only in the assembled views, so it is the
  crystals' light.
- **Crystals:** a pale lavender-pink tip, a saturated violet body and a dark blue-violet base. The back crystals read
  darker.

### 2. Regions and keys

*(First round. Where "Fixes after verifier round 1" below differs — parts plain stone, no foot band, the hero cave and bleed — it wins.)*

| Key | Hex | Rough | Where |
| --- | --- | --- | --- |
| `m011_crystal_light` | #9C4ED9 | 0.35 | crystal tip |
| `m011_crystal_mid` | #8235BE | 0.35 | crystal body |
| `m011_crystal_dark` | #571E95 | 0.35 | crystal root / foot |
| `m011_rock` | #978987 | 0.92 | outside stone, warm |
| `m011_rock_cool` | #878185 | 0.92 | cool grey weathering patches |
| `m011_rock_dark` | #796D6C | 0.94 | darker foot by the ground |
| `m011_cave` | #857470 | 0.94 | bare cave stone just inside the rim (all of each part's inside) |
| `m011_cave_deep` | #7A4E75 | 0.94 | hero only: deep violet cave |
| `m011_seat_glow` | #7E5C74 | 0.85 | hero only: violet bleed on the stone round the crystal roots |

`K.mix_key` adds the in-between keys at 25/50/75 % (e.g. `m011_rock_x_cool_50`, `m011_cave_x_deep_75`,
`m011_crystal_mid_x_crystal_light_50`). 26 keys are in use in total on the current shape (re-measured after stage 2's
redo; 28 on the slab model), each a palette material with `flintkit_hex`.

Finish:
- **Crystals:** glossy, roughness 0.35. (At 0.3 the back crystals threw large white glints.)
- **Stone:** matte, roughness 0.92–0.94.
- **Metal:** 0 everywhere.

### 3. Calibration

`K.calibrate` (faceted test dome, kit studio, hero camera), with two adjustments:
- **Stone keys:** the sampler was switched to `M.sample`'s stone mask. `K.sample`'s own stone mask (sat < 0.18) keeps
  only about 450 edge pixels of a warm stone dome.
- **Crystal light key:** it started too pale for the vivid mask, which returned no pixels until the key was re-seeded
  at #A050E0.

| Key | Target (dome median) | Calibrated | Dome got |
| --- | --- | --- | --- |
| rock | #A99188 | #867775 | #A79086 |
| rock_cool | #948888 | #767076 | #938788 |
| rock_dark | #86726B | #6B5F5D | #85726A |
| crystal_light | #C064F7 | #9C57D9 | #C065FC |
| crystal_mid | #943ACA | #7832AF | #913CC9 |
| crystal_dark | #6925A7 | #571E95 | #682AA9 |
| seat_glow | #976D88 | #775A76 | #956D88 |

The dome is fully lit and the model is not (cave, slab crevices, hood shadow). So the hero renders were re-measured
with the same boxes, and the keys corrected in linear light:
- rock ×1.3–1.38, and a little cooler;
- crystal mid ×1.1, crystal light a little more saturated;
- glow a little warmer.

The cave keys can only be judged in the hero, because their targets are occluded colours. They were set from the
re-measures.

### 4. Blending (no colour by facing)

*(First round. Where "Fixes after verifier round 1" below differs — parts plain stone, no foot band, the hero cave and bleed — it wins.)*

`_grade` is `K.blend(mode="blend", steps=3)` over an explicit face list. (K.blend picks faces by verts, which can't
keep the rock and cave classes apart.) Faces below the band keep k1, faces above it get k2, and faces in between get
the 25/50/75 % mixes.

Every field is a position in the shared build frame (part mesh + `m011_offset`), so the top and bottom shells'
patterns run on across their junction.

- **Rock weathering** (all rock faces): field `K.noise_field(scale 0.22)` minus 0.04·x, so the left is a little cooler,
  as on the sheet. rock → rock_cool, level 0.25, width 0.55. The patches are broad, several studs across.
- **Foot** (rock faces with centre below z 2.0): rock → rock_dark by 0.9 − z + 0.6·noise, width 1.1. The darker band
  has a wandering top edge.
- **Rim → cave:** signed distance from the rock/cave boundary, rock → cave over −0.75..+0.75 studs, so the lip blends
  into the cave stone. The boundary is the mouth's rim and the front slabs' inner edges; the hidden contact plane is
  left out.
- **Hero only, `_crystal_light`:**
  - Cave stone → deep violet by distance from those rim points, from 0.6 to 2.4 studs in.
  - Then the seat bleed, by distance to each crystal's lower body (`_bleed_field`: its axis segment from the foot up
    1 stud, minus its radius), only between z 1.3 and 3.2. Deep cave → seat_glow within 0.9 studs; rock → seat_glow
    within 0.15 (the slab edges right at the crystal feet).
  - The union splits the seat round the roots into small faces, so the bleed is finer on the hero than any part
    could carry.
- **Crystal** (the shard; all seven hero copies carry it), along the crystal's own axis (mesh z / height: root 0,
  tip 1):
  - dark → mid over 0.18..0.58, mid → light over 0.54..0.9;
  - result: root faces dark, the body's lower triangles 50 % dark-mid, upper triangles mid, the shoulder 50–75 %
    light, the tip light.
- **`mode="hard"` is used nowhere.** Crystal and stone are separate keys that never mix, so that edge is hard by
  construction.

### 5. Texture (Tint)

*(First round. Where "Fixes after verifier round 1" below differs — parts plain stone, no foot band, the hero cave and bleed — it wins.)*

- **Per piece:** `Asset` `tint_var` 0.05 (the mk default) gives each built piece (each slab hull, the shell) one random
  brightness.
- **Mottling:** `_mottle` (K.texture in the build frame). Broad and visible, not confetti.
  - Stone: amp 0.07, patches about 2 studs across (scale 0.45), ±1.5 % per-face jitter.
  - Crystal: amp 0.035, scale 0.9, ±1 %.
- **Back crystals:** the hero's BackLeft and BackRight are pasted at Tint ×0.84. Deeper in the cave they read a step
  darker (sheet: back crystal #682B87 vs body #943ACA).
- **Tint ranges:** stone 0.89–1.07, crystals 0.81–1.01.

### 6. Re-measure

Superseded. The first round's table was measured on the slab model in the old studio. The current target-vs-got
tables are in "Fixes after verifier round 1" below.

### 7. Reaching Roblox

Superseded; see "Fixes after verifier round 1", item 8.

### Fixes after verifier round 1

Stage 7 failed the model at 6/10. Since this stage's first pass, two things have changed:
- **Shape:** Stage 1 rebuilt the model as one hollowed-out boulder (hero 812 tris, top 304, bottom 178, shard 36).
  There are no slabs, so the old "slab top" and "slab foot" regions no longer exist.
- **Studio:** a shadowless rear fill light (`FILL_ENERGY` 2.5) now lights the rear and side views.

§1 (sheet targets) still holds. §2–§5 are replaced by the changes below.

#### What changed in `m011.py`

1. **Parts are plain stone, outside and in.** The sheet's exploded and underside views show the parts' insides as the
   same stone in shadow.
   - `_stone_colour` no longer gives the parts a cave key or a rim → cave blend. Their builders' `CAVE` faces are
     painted as stone, with the same warm ↔ cool weathering as the outside.
   - Before repainting, it records those faces for the hero's pass: the rim points (`_RIM`) and their build-frame
     polygons (`_CAVE_TRIS`).
   - The parts now carry only `m011_rock`, `m011_rock_cool` and their mixes.
2. **No painted foot band.** `ROCK_DARK` and `BASE_BAND` are removed. The new shape has no slab foot, and the
   verifier read the band as painted shadow. The sheet's darker lower stone is lighting: the rear view's lower band
   now renders like the sheet's with plain rock.
   - Waivers: the bottom shell's `kit_shading_ok` is gone, and its baked-shading score is 0. Only the crystals' axis
     zoning stays waived (shard 0.93, hero 0.63).
3. **Hero cave (`_crystal_light`) is now classed by position.** A hero face counts as cave when it lies on one of the
   shells' cave polygons (BVH nearest < 0.001). The union splits faces, but every piece stays on its polygon.
   - Depth = distance in from the rim + 0.5 × broad noise (`CAVE_NOISE`, so the bands wander).
   - Over depth 0–0.8: rock → `m011_cave`, a dusky mauve stone #A07896 that is lighter near the rim.
   - Over 0.8–3.6: → `m011_cave_deep` #5B4254, a dark, low-saturation violet (was a saturated plum, #7A4E75).
   - Past 2.2 studs in, the deep cave's Tint falls to 0.78 by 4.2 (`CAVE_BACK`), so the back wall is darkest. This
     is by position, not facing.
4. **Seat bleed made lighter and more vivid.** `m011_seat_glow` is #B06AAA (was #7E5C74). Its reach on the rock round
   the crystal roots is now 0.35 studs (was 0.15); the cave reach stays 0.9.
5. **Rock retuned** to the sheet's lit tops: `m011_rock` is #90817F (was #978987).
6. **Crystals:**
   - Bands: dark → mid over 0.18–0.58 of the height; mid → light over 0.58–0.90, so the tip is full light and the
     shoulder 50 %.
   - The back crystals' Tint is ×0.9 (was 0.84), which lifts the front view.
7. **Geometry and UVs are untouched.** Stage 2's counts are unchanged: 812 / 304 / 178 / 36 tris.

#### Palette after round 1 (superseded below)

| Key | Hex | Rough | Where |
| --- | --- | --- | --- |
| `m011_crystal_light` | #9C4ED9 | 0.35 | crystal tip |
| `m011_crystal_mid` | #8235BE | 0.35 | crystal body |
| `m011_crystal_dark` | #571E95 | 0.35 | crystal root / lower body |
| `m011_rock` | #90817F | 0.92 | all stone (parts outside and in; hero outside) |
| `m011_rock_cool` | #878185 | 0.92 | cool grey weathering (noise field, a little cooler on the left) |
| `m011_cave` | #A07896 | 0.94 | hero only: the cave stone just inside the rim |
| `m011_cave_deep` | #5B4254 | 0.94 | hero only: deep cave |
| `m011_seat_glow` | #B06AAA | 0.85 | hero only: violet bleed on the stone round the crystal roots |

Metal is 0 everywhere. With the 25/50/75 % `K.mix_key` mixes, 23 keys are in use.

#### Target vs got (round 1; superseded by round 2's table below)

Masks as in §1, with the new studio floor colours dropped too. Box pairs are sheet → our render (480×400 cells).

| Region | Sheet | Ours |
| --- | --- | --- |
| Rock lit tops: f34 slab tops → f34 front-lip top | #B69E97 | #B79E95 |
| Rock, front three-quarter, all (median) | #9F8C89 | #AB958C |
| Rock, front view | #A99289 | #A38E89 |
| Rock, top view | #A89289 | #A79993 |
| Rock, rear view | #97837E | #91817D |
| Rock, rear three-quarter | #A48F87 | #938381 |
| Rock, side view | #A18A82 | #817472 |
| Cave, f34 (sheet ceiling + right wall → our ceiling): median / darkest 10 % / lightest 10 % | #3E2839 / #291B26 / #735166 | #3D283D / #2F1D30 / #806E71 |
| Cave, front view: median / darkest 10 % / lightest 10 % | #482D42 / #261923 / #907B76 | #4D334A / #311F32 / #806F71 |
| Seat bleed (tinged mask: sheet close-up → hero f34 / front) | #97698D | #976A8E / #8D668F |
| Seat bleed (vivid violet mask: sat 0.3–0.5, B > G + 40) | #956391 | #9362AA (f34) |
| Crystals, f34: median / lit | #7F37BA / #C666F6 | #813AB5 / #C25EFE |
| Main crystal tip / body / lower body (f34) | #C064F7 / #943ACA / #6925A7 | #BA57F5 / #933ACE / #7D32B1 |
| Crystals, front view | #8336C0 | #7D33B1 |
| Crystals, top view | #8736C4 | #AE53E6 |
| Loose crystal (part_shard vs exploded crystals) | #9342D5 | #8D38C6 |
| Exploded top shell outside → part_top | #C1AA9D | #A6978F |
| Exploded bottom shell → part_bottom (all / outer wall only) | #8C7872 / #8D7871 | #B39C93 / #AB958C |
| Top shell inside, underside view (620,1010,880,1140) → part_top_under | #88766E | #4D4341 |

Reading the table:
- **Matching:** the hero view (front three-quarter lit tops, front view, top view and rear view rock; the cave
  median and grade; the bleed; the crystals in f34) matches within a few points. The cave now runs from dark at the
  back to a lighter mauve near the rim; its lightest end is the rim stone, a little greyer than the sheet's.
- **Same paint, different lighting:** the parts use exactly the paint of the hero's rock, whose front view matches.
  Yet the sheet's exploded top shell renders lighter than ours (−27) and its exploded bottom shell darker (+30). The
  sheet lit those cells differently; darkening one part and lightening the other would break "the parts carry the
  hero's colours" and paint view lighting in.
- **Studio:** the side and rear three-quarter views and the underside cell are still darker than the sheet's. The
  fill light only partly reaches them, and nothing lights the underside view from below. The underside is the plain
  rock key now, with no cave key and no painted shading. This is for stage 5 / the studio, not paint.
- **Crystals, top view:** they read lighter than the sheet's, because the studio's overhead key falls straight on the
  light-key tips. In f34 the same tips match (#BA57F5 vs #C064F7). Darkening the tips would pull f34 off.
- **Main crystal lower body:** a little light in f34 (#7D32B1 vs #6925A7). The front view is a little dark (#7D33B1
  vs #8336C0). These pull in opposite directions, so the bands are left between them.

#### 8. Reaching Roblox (checked against `export_kit_roblox.py`'s logic; nothing exported)

- **Palette keys:** all 23 keys on the four objects are flintkit palette materials (`flintkit_key` + `flintkit_hex`
  equal to `KIT_PALETTE`). None is emissive or water.
- **Tint levels:** every key fits the 32 columns unquantised (at most 31 levels), except `m011_rock`. It has 57
  clusters and is quantised to 32 quantile levels, worst error 0.013; the exporter warns only above 0.05.
- **Tint range:** 0.72 (the deepest cave) to 1.06.
- **Problems:** `K.check` reports none.
- **Saved:** the .blend was saved through the MCP.

### Fixes after verifier round 2

Round 2 failed at 6.5/10. Since then the shape has been redone twice (see "Stage 1 fixes (after verifier round 2)" and
its "Amended…" block):
- a front-facing mouth with the dome over the crystals;
- an arch about 75 % of the width;
- a lumpy front lip with a V-dip;
- the crystal cluster 0.5 further back, with longer side crystals;
- a calm cave ceiling;
- the cave light at hero-local (−0.02, 1.26, 4.8).

The hero is now 968 tris. The colour passes are unchanged in method: parts plain stone, hero cave by depth from the
rim, the seat bleed, the crystal axis zoning. Only keys and the bleed band changed. Geometry and UVs are untouched.

#### What changed

1. **Seat bleed: wider, darker, more violet, still graded.**
   - `m011_seat_glow` is #8A3FB0 (was #B06AAA), roughness 0.92 like the stone (was 0.85), so it reads as stone with
     a violet tint.
   - `BLEED` reach is cave 1.3 / rock 0.7 studs (was 0.9 / 0.35), with band width 1.6 (was 0.8). On the rock, the
     faces at a crystal's foot take 50 %, fading through 25 % to stone. In the cave they take 75–100 % at the roots,
     fading to deep cave.
   - Width 1.2 was tried first. The big faces on the lip's inner slope then went fully violet, a flat lavender sheet.
     That was the "pink, translucent smear": the old pale-pink glow mixes (#987B8A–#A8709F) on the lit inner slope.
     With the new key and band, that slope shows a graded violet tint on matte stone (front three-quarter and front
     views).
2. **Crystals:**
   - `m011_crystal_dark` is #5F2A9C (was #571E95), as asked.
   - `m011_crystal_light` is #A253DD. #B060EC was tried first, but under the new cave light the tips went over the
     sheet's (median #D46CFF vs #C064F7; lit #F68DFF vs #DE81FB), so it was brought back between.
   - `m011_crystal_mid` is #7A31B3 (was #8235BE), to keep the main crystal's median on the sheet's once the cave light
     reached the cluster.
   - Calibration was done against the hero renders. The dome (`K.calibrate`, iters 0, as a check) renders
     light / mid / dark as #D468FF / #9E41DA / #7A3ABD. It is fully lit, so it reads brighter than the sheet's
     targets (#C064F7 / #943ACA / #6925A7).
3. **Cave keys re-tuned for the shallower, lit cave.** The `crystal_glow` light in the studio render now reaches the
   cave and adds violet, so the paint was made less violet:
   - `m011_cave` is #86606F (was #A07896);
   - `m011_cave_deep` is #4A3C3C (was #5B4254).

   The bands (`CAVE_BANDS` 0–0.8 / 0.8–3.6 studs in from the rim) and the Tint fall to 0.78 at the back
   (`CAVE_BACK`) are unchanged. On the new cave they read lighter mauve near the rim and dark at the back.
4. **Rock side view: lighting, not paint.** The same `m011_rock` matches the sheet in the front three-quarter lit tops,
   front, top and rear views. The side view's flank faces sit at a grazing angle to the key light; the rear fill
   doesn't reach them. Rock paint is left as it was.
5. **Housekeeping:**
   - The `T_Calib*` orphan meshes (17, from calibration runs) were purged.
   - `FB_m011_crystal_mid_x_crystal_light_75` no longer exists: the current bands give the shoulder 50 % and the tip
     full light. `_drop_unused` removes unused M011 mixes on every build.
   - No M011 orphans remain. The .blend was saved through the MCP and is clean (not dirty).

#### Palette now

| Key | Hex | Rough | Where |
| --- | --- | --- | --- |
| `m011_crystal_light` | #A253DD | 0.35 | crystal tip |
| `m011_crystal_mid` | #7A31B3 | 0.35 | crystal body |
| `m011_crystal_dark` | #5F2A9C | 0.35 | crystal root / lower body |
| `m011_rock` | #90817F | 0.92 | all stone |
| `m011_rock_cool` | #878185 | 0.92 | cool grey weathering |
| `m011_cave` | #86606F | 0.94 | hero: cave stone just inside the rim |
| `m011_cave_deep` | #4A3C3C | 0.94 | hero: deep cave (the cave light makes it violet) |
| `m011_seat_glow` | #8A3FB0 | 0.92 | hero: violet bleed round the crystal roots |

Metal is 0 everywhere. With the 25/50/75 % mixes, 25 keys are in use.

#### Target vs got (renders after the final `m011.build()`, saved)

Box pairs are sheet → our render, re-placed for the new layout.
- **Crystal-only:** sat > 0.55, so the cave doesn't pollute the shade facets.
- **Bleed:** 0.3 ≤ sat < 0.62, B > G + 30, 70 < max < 215. Sheet box: the assembly close-up (600,860,860,965). Ours:
  the lip's inner edge.
- **Cave:** max < 150, sat < 0.6; median / darkest 10 % / lightest 10 %.

| Region | Sheet | Ours |
| --- | --- | --- |
| Rock lit tops (sheet slab tops → our front-lip top) | #B69E97 | #B79597 |
| Rock, front three-quarter, all | #9F8C89 | #A98F8D |
| Rock, front view | #A99289 | #A48D87 |
| Rock, top view | #A89289 | #A89994 |
| Rock, rear view | #97837E | #90807D |
| Rock, rear three-quarter | #A48F87 | #938481 |
| Rock, side view | #A18A82 | #81726E (lighting; see item 4) |
| Cave, f34 (median / darkest / lightest) | #3E2839 / #291B26 / #735166 | #432943 / #322034 / #6F5B63 |
| Cave, front (median / darkest / lightest) | #482D42 / #261923 / #907B76 | #4F3248 / #362235 / #85736D |
| Seat bleed, f34 (median / lit / shade) | #855480 / #9D6998 / #4E2E54 | #603A7E / #6E4390 / #543071 |
| Seat bleed, front (median / lit / shade) | #855480 / #9D6998 / #4E2E54 | #5D407A / #AB72B5 / #4A2F63 |
| Main crystal f34, crystal-only (median / shade / lit) | #8935C5 / #531C87 / #BD5BF0 | #8B37C2 / #772FA7 / #C25DFA |
| Main crystal tip f34 (median / lit) | #C064F7 / #DE81FB | #C25DFA / #E37FFF |
| Main crystal body f34 | #943ACA | #8A36C2 |
| Crystals f34, crystal-only (median / shade / lit) | #8936C2 / #4D1B78 / #BA58ED | #9242CD / #732EA2 / #C462FD |
| Crystals front, crystal-only (median / shade / lit) | #8736C8 / #511C7B / #B858ED | #8138B2 / #49236E / #C460FC |
| Main crystal, front | #8E3CD5 | #8439B6 |
| Crystals, top view | #8736C4 | #AB56E3 |
| Loose crystal (part_shard) | #9342D5 | #8434B9 |
| Exploded top shell outside → part_top | #C1AA9D | #9B867E |
| Exploded bottom shell → part_bottom | #8C7872 | #B59F95 |
| Top shell inside, underside → part_top_under | #88766E | #4D4341 |

Reading the table:
- **Crystals:**
  - The medians and tips match. Measured on crystal pixels only, the shade facets are not near-black: f34 #772FA7
    (lighter than the sheet's #531C87), front #49236E (sheet #511C7B).
  - Round 2's #311E34 was cave pixels caught by the vivid mask.
  - The top view stays lighter: the studio's overhead key lands on the light-key tips.
- **Bleed:**
  - The rendered bleed runs from dark violet in the shaded seat (#543071) to lit lavender-violet on the lip
    (#AB72B5), round the sheet's #855480.
  - The paint values are #8A3FB0 at the roots and #8C50A4 / #8D6098 / #8E708B for the 75/50/25 % rock mixes, round
    round 2's target #9744AC.
- **Cave:** within about 7 levels of the sheet in median and spread.
- **Studio, not paint** (same as round 1): the side-view rock, the exploded top and bottom shells (the sheet lit those
  cells differently; the same paint matches in the hero views), and the underside cell.

#### Reaching Roblox (checked against `export_kit_roblox.py`'s logic; nothing exported)

- **Palette keys:** all 25 keys are palette materials with a matching `flintkit_hex`. None is emissive or water.
- **Tint levels:** every key fits the 32 columns (at most 31 levels) except three, which are quantised to 32 quantile
  levels: `m011_rock` (59 clusters), `m011_rock_x_cool_25` (34) and `m011_rock_x_cool_75` (34). The worst error is
  0.017; the exporter warns only above 0.05.
- **Tint range:** 0.71–1.07.
- **Baked shading:** 0.91 on the shard and 0.61 on the hero, both from the crystals' axis zoning, both waived in
  `SHADING_OK`. 0 on both shells.
- **`K.check`:** no problems.

### Final fix after verifier round 3

- **Rock bleed limited to the crystal feet.** It now uses `_foot_field`, within `BLEED["rock"]` 0.4 studs of each
  crystal's base, graded over 0.6 (75 % → 25 % → stone). The lip's top and outer face read as plain stone in the
  front, front three-quarter and side views. The cave-side bleed is unchanged.
- **Weathering made subtler.** `WEATHER` is now level 0.45, width 1.4, so almost all faces take at most a 50 %
  cool-grey mix; only 7 faces on the left reach 75 %. The two rear foot lumps read as the same stone.
- Rebuilt on the round-3 shape (hero 1334 tris). `K.check` is clean, and the .blend was saved through the MCP.

### Shared-tool fix

`K.drop_unused_slots` remapped the face indices and then cleared the slots. Clearing the slots zeroes every face's
material index, so any mesh whose unused slot was not the last came out all one colour. Here that hit the bottom
shell and the hero as soon as the colour passes added slots.

It now writes the remapped indices after rebuilding the slots. `_Paint.done` compacts its own slots the same way.

### Left for later stages

- **Stage 5:** the studio lights only the front, while the sheet lights every view. Rear-side stone renders about
  #6D625F against the sheet's #A48F87. In game, Roblox's own lighting decides this.
- **Stage 6:** the sheet's crystal-seat glow and bright crystal tips suggest a soft violet sparkle or glow socket at the
  crystal cluster. The colour here does not depend on it.
- **Front view:** the crystals and their lower bodies render a little darker than the sheet (#73329E vs #8336C0),
  because they sit in the studio's shade. The front three-quarter and top views match.

## Stage 5 — Lighting

Decision: **no emissive faces; one soft violet Studio PointLight in the cave**, documented here and as `STUDIO_LIGHT`
in `m011.py` (a constant; nothing is built from it). No geometry, colour, Tint or material changed.

### What the sheet shows (checked on crops of `references/011.png`)

- **Crystals: lit, not luminous.** Every crystal has a lit side (pale lavender, #C064F7 at the tip) and a shaded side
  that goes dark blue-violet (f34 shade #3C203F). A self-lit crystal would keep its shaded facets bright. The loose
  crystals in the exploded view shade the same way. So no crystal key is emissive.
- **Light from the crystals on the stone.** The "crystal seat" close-up shows a soft violet halo on the seat round the
  crystal's foot that fades out across several stone facets. The assembled views show a violet cast in the cave. The
  exploded parts show no violet (see stage 4). So the crystals do light their surroundings, but softly. There is no
  bright core, rim or seam.
- **WorldModeling.md:** §5.2 says crystals must read without transparency, bloom or emission. §1.2 rules out "an
  ordinary asset recolored neon with a glow halo". §12.5 says no bloom should be needed to read the form.

### Why no emission (emission ≥ 1.0 → Neon)

- `export_kit_roblox.py` turns faces with emission ≥ `GLOW_EMISSION` (1.0) into a separate Neon part per key, in one
  flat colour that ignores Tint.
- On the crystals, that would flatten the light/mid/dark facet zoning and the back crystals' ×0.84 Tint into a few
  glowing slabs. Neon also blooms. Both go against the sheet's crisp, shaded crystals.
- On the seat, the bleed is a soft fade. A Neon disc there would read as a hard glowing patch, which is wrong. Stage 4
  already paints the bleed (`m011_seat_glow`) and the violet cave (`m011_cave_deep`) as solid colours, which export
  unchanged.
- An emission between 0 and 1 doesn't glow in Roblox. It only makes the exporter drop Tint (the mottling and the back
  crystals' darkening), so it was not used either.

### Why a PointLight

In Roblox the cave is mostly closed off from the sky. Its painted violet (#7A4E75 deep cave) is lit only by ambient,
so in game it would sink toward black. A small light inside keeps the cave and seat reading violet: the sheet's "light
from the crystals". It also gives a faint violet spill out of the mouth onto the ground in front, which helps the
resource read at a distance and at night.

### VFX socket?

No. `art/blender/lib/vfx.py` has these light-bearing kinds, and none fits a violet crystal glow:

- `torch_fire`, `campfire`, `brazier_fire`, `forge_fire`: orange, flickering.
- `heat_glow`, `glyph_glow`: orange.
- `rune_glow`: pale blue, with a rune-mote texture.

Overriding a kind's light and emitters would make it a different effect under a wrong name. Stage 6 owns sockets: if
it adds a crystal kind (e.g. `crystal_glow` with a sparse violet `spark_diamond` glint), it should carry this light as
its `light` entry, and the Studio light below then comes with the socket.

### Studio-side setup (one per placed Amethyst)

| Property | Value |
| --- | --- |
| Instance | `Attachment` named `CrystalLight` in the Amethyst MeshPart, with a `PointLight` inside it |
| Attachment position (Roblox, studs from the asset origin = bottom centre of the footprint) | `Vector3.new(0.032, 3.2, 0.021)` |
| Same point in Blender (hero-local, x right, y back, z up) | (0.032, −0.021, 3.2) |
| `Color` | `#B06AF5` = `Color3.fromRGB(176, 106, 245)`: the crystal tip's hue, lighter |
| `Brightness` | 1.0 |
| `Range` | 10 studs, times the placed model's scale |
| `Shadows` | true: the shell's own walls keep the light inside the cave and out of the ground behind and beside it |
| Animation | none (no flicker or pulse; the sheet shows a steady glow) |

- **Where the point is.** In the cave, behind the main crystal, between the two back crystals, 1.6 above the seat
  (seat z 1.6). It is about 0.96 stud clear of every surface, so it is not inside a crystal, whose mesh would shadow
  it.
  - Measured on the hero mesh (re-measured after stage 2's redo): winding number 0 there (outside the solid), and the
    nearest surface is 0.962 away.
  - Crystal feet in hero-local studs: Main (0.02, −1.81), BackLeft (−1.50, −0.46), BackRight (1.60, −0.41), all at z
    1.72.
- **Brightness check.** A scratch preview, not saved to the model renders: Blender point light at `vfx.LIGHT_WATTS` ×
  brightness × range² = 140 W, shadows on, front view.
  - The cave pixels the light reaches go from #4B3544 to #533753 at brightness 1.0: a visible violet lift, still in
    the sheet's dark-violet family (sheet cave #482D42).
  - At 2.0 they go to #5C3D61, which is too bright, and the dark cave stops reading as a cave.
  - Roblox's light falloff differs from Blender's, so check this in Studio (see below).
- **Performance.** One PointLight per node. Where many geodes stand close together (a crystal cave biome), set
  `Shadows` false on all but the nearest few, or drop `Range` to 7, rather than adding more lights.
- **Harvest.** When the node is depleted and its crystals are removed, disable the light or remove the attachment
  with them.

### Studio render note (from stage 4; not the model)

The rear, rear three-quarter, side and underside renders come out dark. Rear stone renders about #6D625F against the
sheet's #A48F87.

The cause is the kit studio (`build_kit.kit_studio`): one sun key (`KEY_DIR` above and front-left, `KIT_KEY` 4.5)
plus a weak neutral ambient (`KIT_AMBIENT` 0.45). The back of any model sees only the ambient, while the sheet lights
every view on its own.

The paint is right: the same keys read #A9958C in the lit front three-quarter view. In game, Roblox's sun and ambient
decide this. `build_kit.py` was not changed. A fix belongs to the studio (for example a rear fill or a per-view key),
for all models at once.

### Rebuild and checks

- `m011.build()` was re-run through the MCP after the edit. Hashes of vertices, per-face palette keys and Tint are
  identical before and after for all four objects: hero 1282 tris, top 318, bottom 586, shard 36 on the slab model
  (now, on the one-rock shape: hero 812, top 304, bottom 178, shard 36), each one shell.
- `K.check` reports no problems. No material has emission (`flintkit_spec[2]` is 0 on all 28 keys then; on all 26
  keys now), and at that point the M011 objects had no sockets (stage 6 added 4 to the hero).
- The renders are unchanged from stage 4.
- 252 orphaned M011 mesh datablocks left by rebuilds were removed, and the mesh datablocks renamed back to their
  objects' names. The .blend was saved through the MCP.

### Left for later stages

- **Stage 6 (VFX):** the sparkle the sheet implies (bright crystal tips). If it adds a crystal glint kind to `vfx.py`,
  give it this PointLight as its `light` entry and place the socket at hero-local (0.032, −0.021, 3.2) (done in
  stage 6; was (0.1, 0.0, 3.2) on the slab model).
- **Stage 7 / Studio:** Requires Manual Validation. Check in Studio, under the game's own Lighting (Future), that the
  cave reads violet, not black, and that the light doesn't wash it out. Tune `Brightness` between 0.7 and 1.3 if
  needed.

## Stage 6 — VFX

Decision: **five sockets on the hero `Amethyst`**: one `crystal_glow` (stage 5's cave PointLight, now built) and four
`ore_glint` (sparse violet twinkles on the lit crystal tips). The parts carry none: the sheet shows the effect only
on the assembled geode. Stage 6 changes no geometry, UVs, materials or colours.

Current state: the follow-up of 2026-10-28, on the front-mouth, dome-over-crystals hero (968 tris; parts 386 / 214 /
36), after stage 1 moved the cave light. It answers verifier round 2: "glints twinkle in empty air above the
crystals".

### What the sheet shows or implies

- Nothing is drawn as an effect (no motes, sparks or glow halos).
- The crystal tips carry bright, almost white-lavender facets (#C064F7 rendered, light swatch #C097DD). That is the
  "subtle sparkle" stage 1 and stage 4 noted: a few short twinkles on the tips, never a cloud of particles.
- The violet cast in the cave and at the seat is the crystals' light (stages 4 and 5). Stage 5 specified the light;
  here it becomes a socket so it travels with the asset into the manifest.

### Sockets (children of `Amethyst`, collection `M011 Amethyst`)

They are built in `m011.py` through `M.mk(..., fx=_vfx())`. Locations are given in the shared build frame. `mk` and
`finish` carry them through the hero's re-centring, so they end up hero-local exactly like the mesh.

| Socket | Kind | Hero-local (Blender x, y, z) | Manifest position (Roblox x, y, z) | Settings |
| --- | --- | --- | --- | --- |
| `VFX_Amethyst_crystal_glow_1` | `crystal_glow` | (−0.0204, 1.2552, 4.8) | (−0.0204, 4.8, −1.2552) | PointLight `#B06AF5`, brightness 1.0, range 10, `shadows` true, no flicker or pulse; no emitters |
| `VFX_Amethyst_ore_glint_1` | `ore_glint` | (0.0056, −1.8938, 7.135) | (0.0056, 7.135, 1.8938) | Main crystal tip: box 1.18 × 0.90 × 1.02 (Roblox x, y, z), rate 0.5/s, size 0 → 0.6 → 0 |
| `VFX_Amethyst_ore_glint_2` | `ore_glint` | (−4.0534, −2.7288, 5.924) | (−4.0534, 5.924, 2.7288) | Left tip: box 1.06 × 0.91 × 1.03, rate 0.35/s, size 0 → 0.45 → 0 |
| `VFX_Amethyst_ore_glint_3` | `ore_glint` | (3.8596, −2.4848, 5.786) | (3.8596, 5.786, 2.4848) | Right tip: box 0.88 × 0.85 × 0.94, rate 0.25/s, size 0 → 0.45 → 0 |
| `VFX_Amethyst_ore_glint_4` | `ore_glint` | (4.7426, −1.7848, 5.231) | (4.7426, 5.231, 1.7848) | FarRight tip: box 0.70 × 0.75 × 0.77, rate 0.15/s, size 0 → 0.35 → 0 |

All values were measured through the MCP on the saved build. Positions are each socket's location. The boxes,
rates, sizes and light were read back from its `roblox` JSON. The Roblox column is the exporter's `to_rbx(x, z, −y)`.

All five: `vfx_scale` 1.0, no `trigger`, identity parent inverse.

The four glints share one emitter (`GLINT` in `m011.py`, passed as an `emitters` override):
- texture `spark_diamond`;
- colour `#F6EAFF` → `#C064F7` (white-lavender flash fading to the tip violet);
- transparency 0.1 → 1.0, lifetime 0.5–0.8 s;
- speed 0, spread 0 (they twinkle in place);
- light emission 1.0, rotation 0–90°.

**Where the glints are.**
- **The fit (`_glint_fx`).** Each box is fitted to the top of one crystal's tip pyramid: its point, plus the
  shoulder ring moved `GLINT_TIP` = 0.5 of the way up to the point. That runs through `_crystal_matrix`, padded by
  `GLINT_PAD` = 0.05.
- **History.**
  - The first boxes ran from the body-top ring up, padded 0.2. The second ran from the shoulder ring up, padded
    0.2, with one box over Right and FarRight.
  - Verifier round 2 saw both twinkle in empty air above and between the crystals.
  - A box over two crystals is mostly air, so Right and FarRight now have one socket each.
- **Which crystals.** The back crystals sit in the cave's shade and the small front one is low in the crack, so they
  get none.
- **Rate.** About 1.25 twinkles a second in all, at 0.5–0.8 s each: under one on screen at a time.
- **Measured with BVHs** (1000 random points per box, on the saved hero):
  - "Outside" uses the nearest-face normal test.
  - "Unoccluded" casts a ray toward the front three-quarter camera.
  - "From a crystal" is the distance from each outside spawn point to the nearest crystal face. It is measured on
    a BVH of the crystal faces only.

  | Box | Outside the solid | Unoccluded (front three-quarter) | From a crystal: 95th pct / max |
  | --- | --- | --- | --- |
  | Main | 74 % | 65 % | 0.46 / 0.61 |
  | Left | 60 % | 56 % | 0.38 / 0.49 |
  | Right | 61 % | 51 % | 0.34 / 0.49 |
  | FarRight | 64 % | 30 % (behind Right from that side) | 0.29 / 0.42 |

  - No twinkle can spawn more than 0.61 stud from a crystal face, about one particle's own peak size. A twinkle
    therefore always touches its tip.
  - With the old boxes, the tip-region boxes reached 0.85–1.14 from a crystal, and the two-crystal box 0.9–1.1.
  - Each socket point itself lies just inside its crystal's tip, 0.13–0.20 from the surface. The rest of the box
    falls inside the tips and is hidden.

**Where the light is.**
- It is stage 1's re-placed cave light (`STUDIO_LIGHT` pos (0.0, 1.26, 4.8)): under the dome, behind the cluster, at
  the most open point of the cave.
- The socket measures (−0.0204, 1.2552, 4.8). `CAVE_LIGHT` in the build frame is (0.0, 1.75, 4.8), and the hero's
  build-frame offset is (0.0204, 0.4948, 0).
- BVH: it is outside the solid, and the nearest surface is 1.742 studs away.
- It lights the cluster from behind and above. Unblocked rays from the light reach 75 of the 326 crystal faces: the
  backs and tops of the cluster, which face it. It also reaches the cave walls and the seat. The crystal fronts face
  away from it and take the sun.

### `vfx.py` change (generic)

- **New kind `crystal_glow`.** A steady soft light from a crystal cluster or geode cave, with no emitters.
  - Its light is `{"color": "#B06AF5", "brightness": 1.0, "range": 10, "flicker": False, "shadows": True}`.
  - Other crystal models override `light` with their own colour, brightness and range. A whole-dict override is
    `add()`'s convention for top-level keys.
  - Their sparkle is a separate `ore_glint` socket.
- **Why a new kind.** No existing kind carries a steady violet light. Stage 5 lists them: orange fire, heat and
  glyph, and pale-blue pulsing rune. Overriding one of them would ship a crystal light under a fire or rune name.
- **New optional light key `shadows`** (PointLight.Shadows, default false).
  - `realize()` now honours it: `ld.use_shadow = light.get("shadows", LIGHT_SHADOWS)`. Every existing kind leaves
    it out, so their previews are unchanged.
  - With shadows on, the shell holds the light in the cave in the preview too, as it will in Studio. The rear, side
    and ground renders show no violet leak.
  - The module docstring and `catalog()` notes describe the key. `art/vfx/README.md`'s kinds table has a
    `crystal_glow` row.
- **Textures.** `ore_glint` needs `spark_diamond.png`, which already exists in `art/vfx/textures/`.
  `crystal_glow` needs none.

### Previews (`render_views`, `M.views(vfx=True)` realizes the sockets)

- **Glints.** Small white-violet diamond stand-ins sit right at the crystal points in the front three-quarter,
  front, side, top and underside views. None floats in the open cave or between crystals. They are subtle: a few
  per view, none mistaken for a crystal.
- **Light.** The cave behind the crystals reads lit violet.
  - Cave median, same mask as stage 4 (max < 150, sat < 0.6, blue > green): front three-quarter #3C2640 against
    the sheet's #3E2839; front #462B43 against #482D42.
  - This mask also catches some dark crystal facets.
- **No leaks.** The rear, rear three-quarter and side views show no violet on the outside or on the ground.
- **The parts** (exploded, part_*) have no sockets and render unchanged.
- **Scratch objects.** No `VFXPreview_*` objects or lights are left in the file after rendering.

### What the exporter writes (read from `export_kit_roblox.py`; no export was run)

- `sockets(obj)` walks the hero's `children_recursive` with a `vfx_kind`. Each socket becomes `{name, kind, position
  (Roblox, from the asset origin), vfx_scale, trigger, spec}` under the asset's `vfx` list. `spec` is the socket's
  `roblox` JSON verbatim: the light dict with `shadows`, and the glint emitters with their boxes.
- None of them is a beam kind, so there are no `end`, `axis` or `normal` keys.
- The STATS line for the M011 sheet should report **5 vfx sockets** (`vfxSockets` counts the asset's `vfx` list).
  All are on `Amethyst`; the parts have none.

### Studio-side result (per placed Amethyst)

- **`crystal_glow`:** an Attachment at (−0.0204, 4.8, −1.2552) from the asset origin with a PointLight inside it:
  `Color` #B06AF5, `Brightness` 1.0, `Range` 10 × the model's scale, `Shadows` true, steady.
  - This replaces stage 5's hand-made `CrystalLight`; don't add both.
  - The tuning range is unchanged: brightness 0.7–1.3.
  - Where many geodes stand together, turn shadows off on the far ones or drop the range to 7.
- **`ore_glint` ×4:** at each position, an invisible, non-colliding box Part of the `shape` size, with a
  ParticleEmitter (`spark_diamond`, the values above) in it.
  - `size` is a 3-key NumberSequence: 0, then the peak, then 0.
  - `rotation` is a NumberRange.
- **On depletion:** disable the five sockets' emitters and light with the crystals.
- **Lobby script.** `scripts/roblox_lobby_map.py` hard-sets `light.Shadows = false` on every socket light. That is
  fine for the lobby, but kit placement code should read `spec.light.shadows`.

### Left for later

- **Stage 7 / Studio (Requires Manual Validation):**
  - under Future lighting, the cave reads violet, not black and not washed out;
  - the twinkles read as sparse tip glints, not fireflies;
  - shadows from the shell keep the light off the ground behind the geode.
- **`art/vfx/vfx_catalog.json` was not regenerated.** It is written by `build_08_vfx.py` (`vfx.catalog()`). Re-run
  that (or just its catalog dump) so `kinds` gains `crystal_glow` and the notes gain the light line.
- **Existing gap, not changed.** A top-level `color=` override in `vfx.add()` is stored as `spec["color"]`, but
  nothing reads it: not `realize()`, not the lobby script, not the exporter's consumers. Emitters keep their own
  colours. The legacy R02/R03 node scripts (for example `gold_node.py`'s `ore_glint` with `color=GLINT`) rely on it.
  M011 avoids it by overriding `emitters`.
- **Rebuild noise (stage 4, not VFX).** Two back-to-back `build()` runs of the same code give identical vertex
  positions, face centres and palette keys on `Amethyst` and `AmethystShellBottom`. Their per-face Tint differs by
  up to 0.028 (mean 0.002 / 0.007), and their vertex order differs.
  - The likely cause: the boolean output's face order changes from run to run, and `_mottle` draws its ±1.5 %
    per-face jitter in face order.
  - So whole-mesh hashes don't match between builds even with no change. Compare order-independently.
  - Seeding the jitter by face position would make the build repeatable.
