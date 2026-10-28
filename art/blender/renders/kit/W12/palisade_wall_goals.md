# W12 PalisadeWall goals

Reference: art/reference/kit/rows/W12_row1.png. Revision after a verifier fail (resemblance 5/10). Status filled in after each build.

## ASSEMBLED / HERO
1. [must] Hero reads as a long straight wall ~12 x 2.5 x 9 (posts to ~10.5), silhouette ~1.3x wider than tall, not boxy.
2. [must] 9-12 upright sharpened logs packed edge to edge, heights visibly uneven (7.5-9.5); about 9+ tips visible on the skyline.
3. [must] Two thicker flat/blunt-topped end posts, clearly fatter (~1.4x) than logs and the tallest points.
4. [must] Each end post carries chunky tan rope lashing at 2 heights (about z3 and z6), each band 2 turns.
5. [must] Red banner with cream diamond emblem and swallowtail bottom hangs on the front, right of centre, spanning ~z3.5-8, from a small crossbar + rope loop.
6. [must] 3-5 chunky faceted grey boulders (1.5-2.2 studs) hug the foot: one big one at each end post and one mid-front, plus small rubble.
7. [must] 5-8 raised, lobed green clover tufts among the stones and along the front, with a few small pale flowers and grass blades.
8. [should] Tan rope bands also cross the logs where the beams meet them.
9. [must] Tan cone tips ~1/5-1/4 of the log height, tapering to a sharp point (same on PalisadeLog and the variants).

## FRONT
10. [must] Front view: logs fill the width with no gaps; banner right of centre; tips form an uneven zig-zag skyline; boulders + clover along the foot.
11. [should] Rear beams only glimpsed from the front (not covering logs).

## SIDE / REAR
12. [must] Straight-on rear view (az 180) shows two horizontal beams (~z3 and ~z6) running the full length between the posts, with rope at the post joints.

## TOP
13. [should] Top view: a single row of round log tops with stones and leaf tufts at the ends and front.

## PARTS
14. [must] Six part assets: PalisadeLog (sharpened, tan tip), PalisadeBeam (horizontal 8-long log), PalisadePost (thick, flat top, 2 rope bands), PalisadeLashing (2-turn tan rope coil), PalisadeGroundCollar (3-4 grey stones in a ring ~2.4 wide), PalisadeBanner (red, cream diamond, swallowtail, crossbar).
15. [should] Collar and lashing coil read at a sensible visible size in the parts cell (chunky stones, fat rope), not specks.
16. [should] Parts upright and at the stated sizes (log h8, post h10.5, banner 1.6 x 4.2).

## VARIATIONS
17. [must] A INTACT: ~10 mixed-height sharpened logs with end posts, beams, rope bands, boulders + clover, NO banner.
18. [must] B LOW/BROKEN: most logs snapped to 2-4 stud stumps with jagged pale tops, full logs left and right, one beam fallen diagonally, debris at the base, more stones and tufts.
19. [must] C TALL: ~13 tight logs 10-12 tall, end posts ~13, three beam levels, rope not dominating; clearly taller than the hero.

## PALETTE
20. [must] Timber is one warm saturated mid-brown (w12_wood #8F5A2C) on logs, posts and beams; render reads saturated brown, not grey.
21. [must] Rope bands and log tips share one pale tan (w12_tan #C9985A); stones one grey (w12_stone #7E7F8C); tufts one mid green (w12_leaf #3F9A2E); banner red (#C8202B) with cream (#F2E6D2) emblem; flowers pale yellow (w12_flower #F6DC6A).

## Status (after build 4 of this revision)

1. MET - hero cell now reads as a long wall about 1.27x wider than tall (12.7 x 10.0); still deeper than spec (3.2) because the front boulders protrude, as in the ref.
2. MET - 11 thinner logs, about 10 sharp tips visible on an uneven skyline.
3. MET - end posts clearly fatter and highest, flat chamfered tan tops.
4. MET - double tan rope rings at two heights on both posts.
5. MET - red swallowtail banner with cream diamond right of centre, crossbar and rope loop.
6. MET - big faceted grey boulder at each post foot and one mid-front, plus rubble; they now read chunky like the ref.
7. MET - raised star-lobed clover tufts along the whole foot, yellow flower dots visible; a few grass blades.
8. MET - tan bands wrap the two logs beside each post at both beam heights.
9. MET - tips are long tan pencil cones (~1/5 of the log) ending in a sharp point; same on the log part and variants.
10. MET - front cell: logs fill the width, banner right of centre, zig-zag tips, stones + clover along the foot.
11. MET - beams are hidden behind the logs from the front.
12. MET - rear cell is now straight-on (az 180): both beams run post to post with rope rings at the post joints; shaded but readable.
13. UNMET - top view still reads as one long band of log tops with a heavy cast shadow (renderer sun); tufts only along the front.
14. MET - all six parts present and recognisable.
15. UNMET - coil is now a fat tan ring, but the collar reads as a small cluster of 3 stones rather than a clear ring.
16. MET - parts upright; log 8, post 10.5, banner 1.6 wide (5.1 tall incl. crossbar loop).
17. MET - intact: 10 mixed logs, posts, beams, rope, boulders + clover, no banner.
18. MET - broken: six jagged stumps, full logs left and right, diagonal fallen beam, logs at the base, more stones/tufts.
19. MET - tall: 13 tight logs 10-12, posts 13, three beams, rope only on posts plus one mid band; longer tips.
20. MET - timber renders warm saturated brown.
21. MET - single colours per material as listed; flowers yellow.

## Iteration log
- Earlier run (builds 1-5): first full module; verifier failed it (boxy 14.2x3.6, short tips, tiny rocks/flat tufts, 3/4 rear view).
- Rev build 1: posts in to x+-5.0, 11 logs r0.55 packed in +-3.75, beams end at posts and moved into the logs, tips 1/4 of height, SIDE_AZIMUTH 180, 2-clump clover + flowers + grass. Size 12.4x2.9. Rocks still rendered small, tips too spiky.
- Rev build 2: rocks x1.3 wide / x1.6 tall and brought forward, clover radius x1.5, tips 0.21, collar stones x1.35. Rocks now chunky.
- Rev build 3: hero logs 7.4-9.1 and posts 10.0 for a lower, longer read; rounder raised clover (squash 1.0). Ratio ~1.27.
- Rev build 4: flowers raised and moved to the front of the tufts (every other tuft); now visible. Cap reached; top and collar should-goals left open.
