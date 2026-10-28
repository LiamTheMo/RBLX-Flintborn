# FiberShrub (R05 row 3) goals

Status is updated after every build (MET / UNMET + evidence).

## ASSEMBLED / HERO
1. [must] Overall ~6 x 6 x 6 studs; iso silhouette a spiky fan, wider at the top than at the base. — MET (rev): 6.8x5.9x6.3; iso is a bushy fan with tall back leaves above the tufts and a narrow trunk base, like the ref.
2. [must] A ring of 8-11 long pointed creased lance leaves (~3.4-6.2 long x 1.7-2.1 wide), sharp tips, centre crease. — MET (rev): 11 broad creased spear leaves all round the trunk, big facets each side.
3. [must] Back/middle leaves stand tall (60-80 deg), front/side leaves angle outward low (~30 deg); the tallest leaf tips form the top of the silhouette. — MET: three back leaves stand ~70-80 deg and form the top of the silhouette; front-side leaves splay out low as in the ref.
4. [must] 3 golden tan star-shaped fibre tufts crown 3 stems: one tallest near centre (~top at 5), two flanking lower (~4); each 6-9 sharp narrow blades radiating up and out, ~1.8 wide x 2 tall. — MET: 3 tan star tufts, centre highest, two flanking lower, 8-9 blades each, ~1.8-2.3 across.
5. [should] Each tuft sits on a small green (r05_fiber_leaf) sepal cup at its base. — MET: small green sepal cup with 5 green sepals under each tuft (visible on the Fiber Tuft part and hero).
6. [must] 3-4 thick faceted brown stems rise from a central base, splaying and forking, clearly visible for the lower ~2.5 studs. — MET (rev): chunky trunk forks into 3 splaying brown stems plus a back stub, plainly visible at lower centre in hero and front cells.
7. [should] Faceted low-poly look: big flat facets, no smooth or noisy surfaces; tris <= 3000. — MET: flat facets throughout, 932/3000 tris.

## FRONT
8. [must] Front view: roughly as wide as tall, fan, brown stems visible centre bottom, tufts at mid-upper height. — MET (rev): front cell ~1.1x wider than tall, three thick stems exposed centre bottom, VFX puffs small and off the stems.

## SIDE
9. [should] Side view: narrower, upright fan with tall leaves; tufts visible poking out between leaves at mid height. — MET: side cell shows a narrow upright fan with a tuft poking out at mid height.

## TOP
10. [must] Top view: radial rosette of 8-9 pointed leaves around a centre with 2-3 tan star tufts near the middle. — MET: top cell is a rosette of ~9 pointed leaves with 3 tan stars clustered at the middle.

## PARTS
11. [must] Leaf part: one long faceted lance leaf ~4.5 x 1.6 x 1, deep green, pointed, creased. — MET (rev): 4.7x1.3x1.3, lies flat and low in the parts cell, pointed and creased.
12. [must] Fiber Tuft part: golden spiky star tuft on a tiny green cup, ~2 x 2 x 2. — MET: tan spiky star on a small green cup, 1.8x1.7x2.0.
13. [must] Stem Fork part: Y-shaped brown faceted stem ~3 x 1.5 x 3 with flat cut ends. — MET: chunky Y-shaped brown stem with flat cut ends, 2.7x1.3x3.1.

## DROPS / DEPLETED
14. [must] Fiber Bundle (x2): two small fan-shaped bundles of tan fibre spikes each bound at a small stub base, ~1.5 long, lying tilted; tan only; nothing below z=0; <= 300 tris. — MET: two tilted fans of tan spikes bound at small stubs in one mesh, 168/300 tris, origin at z=0 (render reads more yellow than ref because palette is fixed).
15. [must] Depleted (Trimmed): one short flat-cut brown stump (~1.2 dia x 1.2 tall) with 4-5 short leaves (~2.5 long) splaying low around it; ~5 wide x ~2 tall; no tufts. — MET: flat-cut brown stump with 5 short leaves splaying low, 5.1x4.5x1.5, no tufts.

## PALETTE
16. [must] Leaves use one key r05_fiber_leaf #2E7A24 (deep saturated green), on all leaves and sepals; render reads as a saturated green, not grey. — MET: all leaves and sepals one key r05_fiber_leaf #2E7A24; renders saturated green (somewhat deeper than the ref's lighter green, palette fixed by the sheet).
17. [must] Stems/stumps use one key r05_bark #7A5030 (warm brown). — MET: stems, forks and stump all r05_bark #7A5030, warm brown in render.
18. [must] Tufts and bundles use one key r05_fiber (now #E2B878 golden cream tan) and read clearly lighter than the leaves. — MET (rev): tufts render pale golden tan against the deep green leaves; bundles one key, render a little yellower in their cell.

## VFX
19. [must] Hero has harvest_hit at (0,-1.5,3.5) coloured tan/green and harvest_deplete at (0,0,0.4). — MET: hero harvest_hit (0,-1.5,3.5) scale 0.7 tan/green; harvest_deplete (0,0,0.4) scale 0.5.

## Iteration log
- Build 1: custom lance_leaf/blade/segment/fiber_tuft helpers; leaves too narrow (grass-like), tufts thin, socket smoke covered the depleted cell.
- Build 2: widened leaves 1.35->2.0 and thicker, wider tuft blades, thicker stems, wider bundle spikes; removed socket from depleted (cell now clear).
- Build 3: broader lens leaf profile, bigger tufts (1.3/1.15), chunkier stem fork.
- Build 4: rolled each leaf so its broad face turns to the front (side leaves were edge-on), taller back leaves (6.3) so they rise above the tufts, scaled the hero VFX previews down so they hide less of the stems. Hero now reads like the ref fan.

## REVISION 1 (verifier failed build 4; goals 1, 6, 8, 18 re-opened as UNMET)
20. [must] HERO: tall upright fan of 8-10 broad creased lance leaves (~1.7-1.8 wide) spread round the full 360 deg; back ones 60-80 deg, front-side ones ~30 deg outward; dense bushy mass ~6w x 6d x 6h (KITSTAT within 5.5-6.8 on every axis), leaves overlapping with no big gaps. — MET: 6.8x5.9x6.3, leaves round the full ring (top cell is a full rosette), tall overlapping back leaves make a dense fan like the ref.
21. [must] HERO: 3-4 thick forked brown stems (trunk ~0.9 radius at base, forking ~1.2 up into 3-4 branches) clearly visible at the bottom centre between the leaves, ~2 studs of stem exposed in front and iso views, comparable in prominence to the reference. — MET: trunk r0.95 forks at ~1.1 into 3 thick stems; ~2 studs of brown stem exposed in iso and front cells, as prominent as the ref.
22. [should] HERO: tufts read as pale golden cream-tan (r05_fiber ~#E6C48A), clearly lighter than the leaves, not saturated yellow; bundles the same. — MET for tufts (pale tan, not saturated yellow); bundles render slightly lighter yellow-cream than the ref bundles.
23. [must] FRONT: fan roughly as wide as tall, stems visible at the bottom centre, not covered by VFX previews. — MET: front fan about as wide as tall, stems clear at bottom centre, deplete puff shrunk to 0.3.
24. [should] SCALE: hero about 6 x 6 x 6 studs. — MET: 6.8 x 5.9 x 6.3 studs.
25. [should] PARTS cell: leaf, tuft and fork are separate and readable, leaf lying flatter (z ~1.0-1.5, ~4.5 long), no overlap. — UNMET (partly): leaf now lies flat on its own; the auto-layout still puts the tuft against the fork base, which the module cannot place.
- Rev build 1: thick trunk (r0.95) forking at 1.1 into 3 stems + back stub; 9 leaves round 360 deg, none straight in front; r05_fiber -> #E6C48A; leaf part laid flat; VFX previews smaller. Stems now clear, but tufts topped the silhouette and tan too pale.
- Rev build 2: back leaves to 5.8-6.3 plus 2 mid uprights (11 leaves), tufts/stems lowered, fibre warmed to #E2B878. Tall leaves now rise above tufts.
- Rev build 3: broader upright leaves (2.0-2.1), shorter side/front leaves (width 7.6 -> 6.8), bigger tufts (1.4/1.25). Dense bushy fan close to ref; all musts MET.
