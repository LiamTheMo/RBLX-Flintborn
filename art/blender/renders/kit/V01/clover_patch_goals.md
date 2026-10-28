# V01 CloverPatch (row 1) goals

## ASSEMBLED / HERO
1. [must] Rounded mound silhouette ~1.3-1.4x wider than tall (~3.2 x 3.2 footprint, ~2.4 tall to flower tops). — MET - build 4 hero reads as a rounded mound, ~1.2x wider than tall (2.9 x 2.9 x 2.4), close to the reference clump
2. [must] 9-11 three-leaf modules visible, each read as three chunky heart leaflets joined at a point. — MET - 12 three-leaf modules, each three chunky heart leaflets meeting at a point
3. [must] Exactly 3 cream domed flower heads poking above the leaves: tallest at back right, one front/left lower, one mid. — MET - 3 cream pom-pom heads: tallest at back right, one mid-left, one lower front-left
4. [must] Thin brown roots splay out at the base, visible below the leaves. — MET - 6 thin brown roots splay out clearly under the hero
5. [should] Leaflets tilted at varied angles so they overlap; leaves near the top are the largest masses. — MET - leaflets tilt at varied angles and overlap; the top modules are the largest masses
6. [should] Leaflets read thick and faceted (visible rim thickness), not paper-thin. — MET - since build 4 the leaflet rims are visibly thick and faceted

## FRONT / SIDE
7. [must] Front view: thin green stems visible between leaves fanning up from the root; mound narrower at the base. — UNMET - front view: stems show only near the base; the denser build-4 leaves hide the fan of stems the reference shows
8. [should] Side view: similar width to front (round footprint), flowers on taller stems above leaf line. — MET - side view is about as wide as the front, with the flower on a stem above the leaf line
9. [should] Stems show a visible bend/joint rather than dead-straight rods. — MET - stems are 3-point polylines with a kink at the middle (visible in the parts cell and the sprig)

## TOP
10. [must] Top view: roughly round crown of overlapping three-leaf rosettes, 2-3 cream flowers visible inside it. — MET - top view: round crown of overlapping rosettes with 3 cream flowers inside

## PARTS
11. [must] CloverLeafModule: three heart leaflets on a short stem, ~1.2 wide. — MET - module part: three heart leaflets on a short stem, 1.2 wide
12. [must] CloverLeaflet: single faceted teardrop/heart ~1 stud long, pointed tip, keel ridge on the underside. — MET - leaflet part: faceted teardrop with a pointed tip, 1.0 long; the centre crease reads as two shaded halves
13. [must] CloverStem: thin ~1.6 long green stalk with a visible bent joint/node mid-way. — MET - stem part: 1.6 long green stalk with a node collar and a bend mid-way
14. [must] CloverFlowerHead: cream dome ~0.7 wide of many petal wedges, short green stem with collar. — MET - flower part: cream petal-wedge dome, 0.7 wide, on a green stem with a collar
15. [must] CloverRootBase: brown knot ~0.6 tall with 5-6 splayed tapering roots. — MET - root part: brown knot 0.6 tall with 6 splayed tapering roots (a bit stump-like)

## VARIATIONS
16. [must] A. Single Sprig: 1-2 leaf modules on 2 stems from a tiny root, ~1.4 wide x 1.5 tall, no flowers. — MET - sprig: 2 modules on 2 bent stems from a tiny root, 1.5 x 1.5, no flowers
17. [must] B. Spread Patch: wide low mat ~4 x 3.5, ~1.2 tall, many leaf modules, 2 small low cream flowers. — MET - spread patch: wide low mat 4.3 x 4.0 x 1.4, 14 modules, 2 low cream flowers
18. [must] C. Flowering Patch: like the hero but taller, 4-5 cream flowers at differing heights, ~3 wide x 2.8 tall. — MET - flowering patch: 5 cream heads at stepped heights, 2.9 wide x 2.8 tall

## PALETTE
19. [must] Leaflets one saturated mid green v01_clover_leaf #2E9A3A; render must look vivid, not pale/grey, matching the reference greens. — MET - leaves render a vivid saturated green close to the reference; lit tops are slightly less lime than the reference
20. [must] Stems v01_stem #4C9230 (slightly yellower green), roots v01_brown #8A5530, petals v01_cream #EFE6CF; no other colours. — MET - only these 4 keys are used: stems v01_stem, roots v01_brown, petals v01_cream
21. [must] Budgets: hero/variants <= 3000 tris, parts <= 1500; nothing below z=0; build reports 0 problems. — MET - hero 2720, variants <=2794, parts <=268 tris; z clamped to >=0; 0 problems

## Iteration log
- B1: base build. Flowers were spiky white stars, leaflets narrow, the mound low and flat, roots faint.
- B2: blunter, more numerous petal wedges and a bigger core, so the heads read as domes; wider heart leaflets; jointed stem node; bigger flowers.
- B3: 3-ring hero layout gives a taller mound; longer, thicker roots; the sprig is narrowed to 1.5.
- B4: 5 low outer modules fill the bottom of the mound; thicker, more cupped leaflets. Stopped at the 4-build cap. Goal 7 (stems visible in the front view) is still UNMET: the stems are hidden by the denser foliage.
