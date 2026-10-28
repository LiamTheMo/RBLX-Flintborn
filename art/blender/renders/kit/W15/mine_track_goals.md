# W15 Row 2 MineTrack goals

Convention: track runs along Y, front -Y, origin bottom centre. Hero/variants use HERO_AZIMUTH 202 (rear-left) and HERO_ELEVATION 38, so the track runs lower-left to upper-right with the buffer (+Y end) nearest, as in the reference.

## ASSEMBLED / HERO
1. [must] Two blue-grey iron rails on top of the ties, ~0.6 wide x 0.7 tall, parallel, gauge ~3 studs. -- MET - two slate rails sit on the tie tops, parallel, ~3 stud clear gauge.
2. [must] 7 chunky orange-brown timber ties (~6 x 1 x 0.7) crossing under both rails and sticking out past each rail. -- MET - 7 orange ties, ends clearly outside both rails.
3. [must] Small bracket plates with bolt heads at every rail/tie crossing (not chunky blocks). -- MET - small slate side plates with bolt dots at each crossing, rail stays visible above them.
4. [must] (verifier) Long narrow track running lower-left to upper-right, clearly longer than wide, buffer in the foreground. -- MET - track runs from the near buffer at lower-left to the far stop post at upper-right; pad 10.6 x 16.2.
5. [must] (verifier) End buffer reads as two chunky upright posts on footing blocks with a crossbeam, ~3 studs tall, clearly above the track. -- MET - two tall posts on wider footings with iron bands and a crossbeam spanning the track end, standing well above the rails in the iso cell.
6. [must] (verifier) Iron reads slate blue-grey, clearly lighter than the timber, not near-black navy. -- MET - rails render mid slate blue-grey (w15_iron #65738D, metallic 0), lighter than the ties.
7. [must] Pale sand pad (w15_sand) under the whole track, irregular outline, extending past the ties. -- MET - irregular sand pad visible around the track.
8. [must] 3-5 grey faceted rocks (w15_rock) around the pad edges, chunky facets, not dominating the pad. -- MET - 5 faceted grey rocks at the pad edges, smaller than before so the track dominates.
9. [should] (verifier) 3+ bright green leafy tufts visible beside rocks / buffer. -- MET - 5-6 clearly visible green clumps at rock bases and the pad edge.
10. [should] Ties slightly irregular. -- MET - small length/angle variation.
11. [should] Far-end small stop post as in the reference. -- MET - small timber post on footing at the far right.

## FRONT
12. [should] (verifier) Front cell: high-elevation ladder view. -- UNMET - the runner renders FRONT at a fixed 6 deg and exposes no FRONT_ELEVATION; the cell shows the rails over ties with the buffer behind. Not settable from the module.

## SIDE
13. [must] Side view: low cross-section, horizontal rail line on tie-end blocks, buffer post at one end. -- MET - long rail line on tie blocks, buffer post at the right end.

## TOP
14. [must] Top view: two parallel rails, bracket plates at each tie, ties past both rails, sand under, rocks at edges. -- MET - ladder with plates at each tie, sand and rocks visible.

## PARTS
15. [must] (verifier) Rail, Tie, JoinBracket, EndBuffer present and readable as separate, non-overlapping objects. -- MET - parts cell now shows buffer, rail, tie and bracket apart with clear gaps.
16. [must] RailSegment: single 8-long rail with 3 small thin bolt plates. -- MET - long slate rail with 3 small plates and bolts.
17. [must] WoodenTie: 6 x 1 x 0.7 timber with 2 bolt dots. -- MET - orange tie with 2 dark dots.
18. [must] JoinBracket: iron plate ~3 x 0.8 x 0.6 with 4 round bolts. -- MET - slate bar with 4 bolts on its face.
19. [must] EndBuffer: two timber blocks/posts with crossbar and iron strap, ~4 wide x 3 tall. -- MET - two posts (one taller with iron cap) joined by a crossbar with strap; 4.4 x 3.0.

## VARIATIONS
20. [must] Straight: 16-stud piece, 8 ties, 2 rails, sand outline. -- MET - straight ladder on a sand strip.
21. [must] (verifier) Curved: ~90 deg arc, ties fanning radially, readable curve (not edge-on). -- MET - arc now runs into the view and bends clearly, ties fan radially.
22. [must] Fork: main straight with a curved branch, rails crossing, ties fanning. -- MET - branch curves off right, crosses the main rail, own fanned ties.
23. [should] Same gauge / tie / rail sizes everywhere. -- MET - shared constants.

## Palette
24. [must] (verifier) One key per material: w15_timber, w15_iron, w15_rock, w15_sand, w15_foliage; iron mid-tone matches the reference slate. -- MET - 5 keys; iron slate blue-grey, wood orange-brown. Note: w15_iron deviates from the sheet value #454B66 (verifier fix); other W15 modules still use the old value.

## Iteration log
- Earlier run, builds 1-4: base layout, camera 202/32, fork branch, rocks.
- Revision build 1: w15_iron -> #6F7F96 non-metallic; HERO_ELEVATION 38; thin side bracket plates; hero track 10 long / 7 ties, narrow pad, tall buffer (posts 1.4x1.4 on 2x2 footings, crossbeam at z 2.2) + far stop post; smaller rocks; bigger tufts; curve mirrored so it runs into the view; tie part along Y. Iron, buffer, curve fixed; parts still overlapped.
- Revision build 2: iron #65738D (slightly deeper slate); rail part along Y so the grid sets it apart. Parts separated.
- Revision build 3: one extra back rock and tuft for the reference's rock ring. All musts met.
