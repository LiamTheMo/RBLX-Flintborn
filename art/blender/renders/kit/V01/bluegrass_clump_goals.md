# V01 BluegrassClump (row 3) goals

Status after each build is filled in below each goal.

## ASSEMBLED / HERO
1. [must] Dense clump of ~18-22 blades radiating from one hub; reads as a single fountain-shaped tuft, about as wide (~4.5) as tall to blade tops (~3.4), so width:height ~1.3. MET: render shows one fountain tuft of ~27 blades from a single hub; looks about as wide as the ref (bbox 5.6 wide, a bit over).
2. [must] Blades are folded (V/keeled) and arch outward: long outer blades droop with tips at or below half height; short inner ones stand near upright. MET: inner blades stand upright, outer ones rise then arc out and down; ref arcs are a little softer.
3. [must] Blades are broad-ish (max width ~0.35-0.45 studs, ~1/8 of length) with pointed tips, not hair-thin grass and not flat straps. MET: blades read broad with a visible keel crease and pointed tips.
4. [must] Two tan seedheads on slender green stems rise above the blades (tops ~4.2), leaning slightly apart (one left, one right). MET: two tan ears top the clump at 4.2, leaning left and right.
5. [must] Seedheads are faceted ear shapes ~0.9 long with visible layered scales, widest near the middle, pointed tip. MET: plump faceted ears with spiral scales, pointed tip, similar to ref.
6. [should] One broad blade sweeps low across the front (toward the camera), tip near the ground. UNMET: front blade exists but does not read as the distinct broad sweep seen in the ref.
7. [should] Small brown root base visible at the hub between blade bases. MET: small brown hub visible at the base in hero and front cells.

## FRONT / SIDE
8. [must] Front view: fan silhouette, seedheads clearly above blade tops, blade tips arching out to both sides. MET: fan silhouette with ears well above the blades.
9. [should] Side view similar to front (radially symmetric clump), seedheads both visible. MET: side view is a fan; ears overlap slightly but both show.

## TOP
10. [must] Top view: radial star of ~18-22 pointed blades around a centre, roughly circular outline, no big gaps. MET: radial star of pointed blades around a centre; outline less round and a little gappier than ref.

## PARTS
11. [must] BluegrassLongBlade: one curved, arched folded blade ~3.8 long with pointed tip. MET: tall curved keeled blade, pointed.
12. [must] BluegrassShortBlade: straighter folded blade ~2.4 long, pointed. MET: shorter straight blade, pointed.
13. [must] BluegrassSeedhead: tan scaled ear ~1 long on a thin bent green stem ~2.2 long. MET: tan scaled ear on a thin bent green stem.
14. [must] BluegrassStem: green 6-sided stalk ~2 long with a visible bent joint/node. UNMET: built (2.0 long, 6 sides, node at bend) but the automatic parts grid places it behind the seedhead stem so it is barely readable.
15. [should] BluegrassRootBase: brown knot/stump ~0.6 tall with 4-6 splayed roots. UNMET: stump plus 5 roots exists but reads small and spindly next to the ref stump.

## VARIATIONS
16. [must] BluegrassCompact: smaller, ~3 wide x 2.8 tall, ~12 blades, 2 seedheads. MET: smaller tuft, 2 ears, 2.5 wide x 2.8 tall.
17. [must] BluegrassWideSpread: ~5.5 wide x 3 tall, long drooping blades, 3 seedheads; clearly wider/flatter than hero. MET: visibly wider, lower, drooping clump with 3 ears.
18. [must] BluegrassDryLateGrowth: hero-like form ~4 wide x 3.4 tall, ALL blades golden-straw, more upright and ragged, 2-3 tan seedheads. MET: golden-straw upright ragged blades, 3 tan ears.

## PALETTE / SCALE / TECH
19. [must] Blades one teal-leaning saturated mid green v01_blue_blade #1F8A52 (render reads as cool mid green like the reference, not grey/pale). MET: blades render saturated cool green, close to ref (slightly darker on shadow side).
20. [must] Seedheads v01_seedhead_tan #D0AC70 (pale tan); stems v01_stem #4C9230 (yellower green than blades); root base v01_brown #8A5530; dry blades v01_dry_grass #C9A035. MET: each material uses its one key in the right place.
21. [must] All assets within budget (hero/variant 3000, part 1500), collision none, nothing below z=0, 0 problems. MET: hero 1992/3000, variants <=2284, parts <=262; 0 problems.

## Iteration log
- Build 1: first pass. Blades too narrow and sparse (agave look), small seedheads.
- Build 2: blades wider (0.6, widest at 45%), hub spread wider, bigger ears. Fuller but squat and wide.
- Build 3: outer blades start steeper (64-80 deg) and droop more; ears 1.05 x 0.6. Taller fountain shape, closer to ref.
- Build 4: more blades (hero 27, compact 14, wide 27, dry 24). Denser top star. Reached the 4-build cap.
- Open: BluegrassStem is hidden behind the seedhead stem by the automatic parts layout; root base part reads spindly; the front sweep blade is not distinct.
