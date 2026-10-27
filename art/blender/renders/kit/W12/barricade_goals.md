# W12 Barricade goals

Status: all must goals MET after build 4.

## ASSEMBLED / HERO
1. [must] Low, wide straight fence: ~10 studs long x ~5.5 tall (width:height ~1.8:1), depth ~3.5 incl. stones. -> MET - hero cell reads low and wide like ref; KITSTAT 11.7x4.6x5.5 (width incl. end tufts).
2. [must] Four chunky upright posts (r~0.55, flat chamfered tops) with uneven heights 4.5-5.5; tops clearly above the upper rail. -> MET - 4 hexagonal posts with chamfered tops, uneven heights, tops well above upper rail.
3. [must] Two horizontal rail logs (z~1.6 and ~3.6) running the full length in front of the posts, with a second rail pair visible behind the posts. -> MET - two front rails full length; rear-3/4 side cell shows the back rail pair behind the inner posts.
4. [must] Two diagonal brace logs in front, rising in opposite directions (V/X pattern) from post bases to the upper rail. -> MET - front cell shows two braces rising outward from inner post bases to the upper rail, a V like the ref.
5. [must] 4-6 fat tan rope wraps visible at post/rail and brace/rail junctions, thicker than a thin line (reads as chunky bands). -> MET - fat tan X lashings at all 4 upper post/rail junctions plus rail wraps at brace tops (slightly bigger than ref).
6. [must] 3-5 grey faceted boulders (1.2-2 studs) at the feet, front side. -> MET - 4 grey faceted boulders along the front foot in hero and front cells.
7. [must] 6-10 small green clover tufts around the base, low (under ~1 stud tall). -> MET - low clover clumps form a green band along the base like the ref (14 small clumps, a few more than 10 to match its density).
8. [should] Rail and brace ends show cut log ends (round/octagonal section), slight overhang past end posts. -> MET - rails/braces show octagonal cut ends past the end posts.

## FRONT
9. [must] Front view: 4 posts evenly spaced (~3 studs apart), 2 rails, braces forming a V between inner posts and outer upper rail; rope wraps at the upper-rail junctions. -> MET - front cell: 4 evenly spaced posts, 2 rails, outward V braces, rope at upper junctions.
10. [should] Front view: stones and tufts sit along the bottom edge, not covering more than ~1/4 of fence height. -> MET - stones/tufts sit along the bottom, under ~1/4 of fence height.

## SIDE
11. [should] Side view shows double rail thickness (rails on both front and back of posts) and a brace profile; reads as ~3.5 deep at base. -> MET - side cell (rear 3/4, SIDE_AZIMUTH 135) shows doubled rails and a brace; depth reads ~3.5-4.

## TOP
12. [should] Top view: a thin long strip (~10 x 2) of rail logs with post tops as dots and stone/leaf clumps along the edges. -> MET - top cell: long thin strip of rails with post tops, rope rings, stones and tufts at the edges.

## PARTS
13. [must] Five parts: BarricadeRailLog (horizontal log with cut ends ~8 long), BarricadeUprightPost (tall post with rope wrap, chamfered top), BarricadeDiagonalBrace (45 deg log, angled flat-cut ends), BarricadeFootCollar (3-4 grey stones in a ring around a hole), BarricadeStake (upright pointed stake with tan tip). -> MET - parts cell shows rail log, roped post, angled-cut brace, 4-stone collar ring and stake.
14. [must] Stake tip is pale tan (w12_tan), body wood. -> MET - stake tip renders pale tan on wood body.

## VARIATIONS
15. [must] BarricadeStraight: simpler fence, ~9 long, 3 posts, 2 rails, one X brace, a couple of stones and leaf tufts. -> MET - Straight cell: 3 posts, 2 rails, one X brace, 2 stones, tufts.
16. [must] BarricadeCorner: L-shaped 90 deg plan with two ~6-stud arms meeting at a corner post, rails crossing at the corner, braces on both arms, rope bundle at the corner. -> MET - Corner cell reads as an L with the corner post at the back, rails crossing there, braces on both arms in a V; corner rope bundle is small but present.
17. [must] BarricadeDamaged: visibly broken - leaning/snapped posts, rails fallen diagonally, shattered brace pieces and loose logs on the ground, leaning stakes, hanging rope; stays within ~10x5x5. -> MET - Damaged cell: leaning/snapped posts, diagonal fallen rail, rail and brace pieces on the ground, leaning tan-tipped stakes, hanging rope; 10.9x5.0x5.0.

## PALETTE / SCALE
18. [must] Wood one saturated warm brown w12_wood #8F5A2C on all timber (posts, rails, braces, cut ends); render reads orange-brown like the reference, not grey. -> MET - all timber renders the same warm orange-brown as the reference, not grey.
19. [must] Rope tan w12_tan #C9985A on wraps and stake tips only; stone w12_stone #7E7F8C boulders; leaf w12_leaf #3F9A2E clover tufts. -> MET - tan only on ropes/stake tips, grey boulders, saturated green clover.
20. [should] Hero tris under 4000, parts under 1500, variants under 3500; nothing below z=0; origin bottom centre. -> MET - hero 3137/4000, variants <=2161/3500, parts <=232/1500; 0 problems.

## Iteration log
- Build 1: base design. Rope wraps too thin, tufts too small, side cell showed end-on view, collar stones scattered.
- Build 2: X lashings at junctions, tufts x1.35, stones x1.15, SIDE_AZIMUTH 135, tighter collar. Side cell now matches; lashings oversized.
- Build 3: lashing size 0.98->0.78, thinner rope, 5 more tufts. Rope scale and green base band now close to ref.
- Build 4: corner variant reworked so both arms face the camera with the corner at the back (V like ref B).
