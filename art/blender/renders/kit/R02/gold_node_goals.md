# R02 GoldNode goals

Palette: r02_gold_host #7B5640 (host boulder, depleted mound; uniform part Tint ~1.12 so it renders tan, not chocolate),
r02_gold #E3A817 (nuggets, drops; slightly glossy), r02_base_rock #8C827D (base rocks at the toes, light warm grey).

## ASSEMBLED / HERO
1. [must] Hero ~10 x 8 x 8 studs overall; boulder ~9 wide, ~1.3x wider than tall.
2. [must] (verifier) Host colour matches the reference mid-tone: warm tan-brown, lit faces light brown, not dark or red; distinct from iron grey.
3. [must] (verifier) 3 fat gold nuggets visible from the front (big ~3.8 right-front low, medium ~3 left, ~2.4 upper-right shoulder), each a crisp gem of ~10-12 big planar facets; plus 1 small (~1.8) on the crown.
4. [must] Nuggets protrude ~1 stud, embedded like geodes, no rim/border geometry; the shoulder nugget is a compact tilted gem, not curved.
5. [must] (verifier) Three light-grey base rocks clearly visible at the toes in hero and front cells: front-left ~2.5-2.9, front-right low ~2, small front-centre ~1.4 (ratio big:small ~2:1).
6. [should] Gold renders bright saturated amber with glossy lit faces.
7. [must] (verifier) Host and gems are crisply faceted like the reference: host ~30-50 medium flat facets, gems 10-12 visible planar facets, no soft blobs.

## FRONT
8. [must] Front silhouette is a dome; big nugget right of centre low, left nugget mid-height on the left edge, shoulder nugget at the upper-right edge.
9. [should] Base rocks visible at both bottom corners in the front view.

## SIDE
10. [must] Side profile is egg-shaped and peaked: narrower than wide, apex slightly toward the back, front slope carries the nugget(s) on the right as in the ref.
11. [must] (verifier) Side cell is not near-black: lit host faces read mid brown.

## TOP
12. [must] (verifier) Top view: roundish outline, crown nugget, nuggets visible at the left, right and front edges.

## PARTS
13. [must] GoldHostRock: bare brown boulder ~9x7x7, no gold.
14. [must] GoldNugget: upright elongated faceted nugget ~1.6x1.4x4; GoldNuggetB squat variant present.
15. [must] GoldBaseRock: small light grey rock ~2x1.7x1.5.

## DROPS / DEPLETED
16. [must] GoldNuggetDrop: chunky tilted faceted bar ~1.5x1.1x1.2, <=300 tris, closed.
17. [should] GoldNuggetDrop2: rounder faceted gem ~1.3x1.2x1.2, not a sphere.
18. [must] (verifier) GoldNodeDepleted: low wide brown mound ~9x7x3 that tapers up from the base, rough-faceted top with 2-3 shallow pits, two grey base rocks at the ends, no gold; not a smooth disc.

## VFX / tech
19. [must] harvest_hit (gold chips) on the strike face mid height; ore_glint on big and left nugget; harvest_deplete at the depleted base centre; no light (gold does not glow).
20. [must] Budgets: hero <=4500, host 1500, nugget 500, base rock 400, drops 300, depleted 2000; build ends 0 problems.

## Status
(final, revision build 4 / overall build 8; judged by eye against the reference row)
1 MET: hero 10.3 x 8.0 x 7.6 studs, reads as a wide dome like the ref.
2 MET: host now renders light tan-brown on lit faces, mid brown in shadow; no chocolate/near-black. Residual: a touch more orange than the ref's greyish tan (sheet colour is fixed; see open issue).
3 MET: big gem right-front low with a broad flat front facet, medium gem on the left, shoulder gem upper right, crown gem visible; all crisp planar facets.
4 MET: gems stick out ~1 stud from the host, no rim; shoulder gem is a compact tilted gem (the hook is gone).
5 MET: hero and front cells show the big front-left rock, small front-centre rock and the front-right rock beside the big nugget.
6 MET: saturated amber with bright glossy faces.
7 MET: host shows medium flat facets, gems show ~10-12 flat facets each; no soft blobs (gems are a little more pointed than the ref's rounder gems).
8 MET: front dome, big gem right of centre low, left gem on the left edge, shoulder gem top right.
9 MET: grey rocks at both bottom corners in the front cell.
10 MET: side is a peaked egg with the front slope and nugget on the right, apex slightly back, like the ref.
11 MET: side cell lit faces are mid brown; only the lower shadow side is dark, as in the ref.
12 MET: top view is round, crown gem on top, gems at left, right and front edges.
13 MET: bare brown host part.
14 MET: upright elongated gem and squat GoldNuggetB in the parts cell (the elongated one sits at the cell's right edge).
15 MET: small grey base rock part.
16 MET: tilted faceted bar drop, 1.4x1.1x1.1, 20 tris.
17 MET: GoldNuggetDrop2 faceted jittered gem 1.1x1.3x1.2 (still fairly regular, but faceted, not round).
18 MET: depleted is a faceted mound tapering from a wide base to a flattened rough top with grey rocks at both ends, no gold; pits read as shallow facet dents on the top (faint at this scale).
19 MET: harvest_hit gold chips, 2 ore_glint, harvest_deplete on the depleted base; no light.
20 MET: hero 564/4500, all budgets ok, 0 problems.

## Iteration log
1-4 (first run): coarse icos, then subdiv 3 / dissolve; result was soft blob nuggets, dark host, hidden right rock, disc depleted (verifier fail 6/10).
5. Revision build 1: crisp subdiv-1 gems, host subdiv 2 + uniform Tint 1.12 (colour now tan), right toe rock moved out to (3.8,-3.1), SIDE_AZIMUTH -90 (front on the right like the ref, lit side), depleted rebuilt as a sunk-equator mound with flattened top and pits. Host too coarse, nuggets too small.
6. Revision build 2: host subdiv 3 / 13 deg facets, bigger and more protruding gems, left gem higher and further left (top view spread). Side lost its peak (narrow too low).
7. Revision build 3: narrow 0.32 restored the peaked egg; tried subdiv-2 gems: too round, reverted. Depleted subdiv 3 for visible pits.
8. Revision build 4: subdiv-1 gems flattened in depth with 14 deg merge: crisp gems with a broad front facet. Every must goal met.
