# W10 RuinLeanTo goals

Revision after a verifier FAIL (resemblance 5/10). Status after revision build 4, judged by eye against the reference row.

## ASSEMBLED / HERO
1. [must] L-shaped ruin wall of chunky grey block masonry at back (+Y) and left (-X), ~40-55 bevelled blocks (~2.5 x 1.85 face), clear joints. MET - deep L of bevelled grey blocks with visible joints in hero, front and rear cells.
2. [must] (verifier) Walls are thick (3-4 studs) and massive and dominate the silhouette; tallest column at the back-left corner ~11 studs; jagged stepped top with missing blocks. MET - arms are now 3.2 deep and read as block masses; back-left corner 11.1 tall, the left wall steps 11 -> 7.4 -> 5.5 to the front, missing top blocks along the back.
3. [must] (verifier) Arch-like gap / break in the left wall at y -1..-3, >= 3 wide, >= 5 tall, with a lintel, readable from the hero camera. UNMET (partly) - a 3.8-wide, 3-course (5.6) opening with a broken lintel now cuts the left wall at y +1..-2.8 and shows clearly as a break in the top view, but from azimuth -22 it is seen edge-on and reads only as a low step behind the left post. See open issues.
4. [must] (verifier) Cream canopy ~12 x 10 sags into a V between the wall tie and the two post ties, sloping down to the front. MET - front cell shows a clear V sag (centre ~1.8 lower than the ties); the hero shows the sheet dipping in the middle; corners stay at 7.3 at the posts.
5. [must] (verifier) Two stout orange-brown uprights ~9 tall, ~1.5 thick, with chunky rope collars. MET - posts are now 1.5 studs thick, 9 tall, with a 3-wrap rope collar at the tie and a notch; they read as chunky logs like the reference.
6. [must] Red banner (~1.6 x 4) hanging from the right upright with a cream diamond emblem. MET - red swallowtail banner with cream diamond on an arm off the right post.
7. [should] (verifier) Under the canopy: 3 crates, 2 hooped barrels, tan bed mat with green bedroll, log bench, readable and not lost in shadow. MET - crates 2.3, barrels 0.9 r, bedroll 0.7 r; the crate stack, barrels, bench and green roll all read in the hero; the stack is still in canopy shade, as in the reference.
8. [must] (verifier) Ivy and moss drape down the wall faces and rubble, not only sit on top; 5+ vine strands. MET - 8 ivy spots with 16 leafy vine strands hanging down the inner, outer, end and rear faces (visible on the left wall front and rear-cell faces), caps cut to small lip clumps, moss on 2 rubble stones.
9. [should] Loose rubble blocks (6+) and grass/fern tufts (5) plus 2-3 small flowers around the front base. MET - 8 rubble blocks (2 fallen out of the left breach), 5 fern tufts, 3 cream flowers and a leafy clump.
10. [must] Front opening between the uprights >= 6 wide x 7 tall; footprint ~18 x 16 studs. MET - posts 13.6 apart, canopy 7.3 at the posts; hero 20.6 x 16.2 x 11.5 studs.

## FRONT
11. [must] Front view: wall spans the full width behind the canopy, tall columns at both ends, posts framing the front, canopy hanging between them as a V. MET - front cell shows the full-width block wall, both posts and a clear V-sagging canopy with the banner on the right.

## SIDE (rear three-quarter, 135)
12. [should] Rear view shows the block-grid backs of both walls with ivy strands on them, a post and canopy edge past the wall end. MET - rear cell shows the deep block backs with several hanging vines, the right post with banner and the canopy edge.

## TOP
13. [must] (verifier) Top view: square cream canopy in the middle, wall L along the back and left, both posts visible at the front corners. MET - top cell shows the canopy, the thick wall L with the left-wall break, and both post tops just outside the canopy front corners.

## PARTS
14. [must] (verifier) All 7 parts present and legible in the exploded cell: stepped WallBlocks chunk (~8 x 3 x 8, ~12 blocks, ivy), Canopy, UprightPost, WallAnchor, Crate, BedMat, Peg. MET - parts cell shows the post, stepped ivy wall chunk, anchor stake with ring, crate in the back row, the torn canopy and mat with bedroll in front and the peg at the front; nothing hides behind the canopy now.

## VARIATIONS
15. [must] Snow Shelter: snow caps on wall tops, canopy and crates; bare posts, no banner; bench and barrel. MET - white caps on every wall top, snow on the canopy back and post tops, snowy crates and barrel, bench under.
16. [must] Trader Stall: banner on right post, table with cream/red/amber goods, barrels and crates, lantern on a post (emissive + heat_glow). MET - banner, goods table, crates, barrels, glowing lantern on the left post with a heat_glow socket.
17. [must] Abandoned: canvas torn into ragged hanging strips, one upright, heavier ivy, overgrown tufts, no goods. MET - ragged strips with the left side collapsed, one post plus a stump, heavy ivy, 7 tufts, no goods.

## PALETTE
18. [must] One flat key per material from the sheet palette (w10_wood posts/crates/barrels/bench, w10_canvas canopy/emblem/flowers, w10_rope collars/ties/mat/cut ends, w10_stone blocks/rubble, w10_banner, w10_iron, w10_foliage, w10_bedroll, w10_snow, w10_lantern). MET - only sheet keys used; wood orange-brown, canvas warm cream, stone lilac-grey, ivy saturated green.
19. [should] (verifier) Stone reads as mid grey-lilac bevelled blocks of varied size with visible facets. MET - stronger bevel (20% of block size) and jitter give faceted, varied blocks in every cell.
20. [should] Tris: hero <= 8000, variants <= 6000, parts <= 1500; 0 problems. MET - hero 7957, variants 5412/5568/5754, parts 92-808; 0 problems.

## Open issues
- Goal 3: from azimuth -22 a gap through the left wall is seen edge-on. With the required 3.2-stud wall a see-through opening would need a wall thinner than ~1.5 studs (width x tan 22 deg). The break is real and visible from the top and rear, but it reads only as a step from the hero camera.
- The verifier suggested lightening w10_wood. It is a shared sheet key that all four W10 modules must keep identical, so I left it as given.

## Iteration log
- Builds 1-4 (earlier run): first pass, then tuning. The verifier failed it: walls thin and flat, posts thin, canopy flat, ivy as blobs, gap and top-view posts not visible, parts cell sparse.
- Revision build 1: walls 3.2 deep, posts 1.5 thick at x 6.8 y -5.8, V-sag canopy, vine strands in place of the double moss clumps, bigger gear, flowers, bevelled blocks, gap moved forward. Hero 8675 and Trader 6052 were OVER budget. The canopy part hid the anchor and peg.
- Revision build 2: dropped the lower rope collar and one ivy spot, trimmed tufts, lowered the canopy (7.9 at the back, 7.3 at the front) so the wall rises above it, flattened the canopy part so it sorts into the front row. 0 problems; all 7 parts legible. Gap still invisible.
- Revision build 3: the arch is now y 1..-2.8 with 2 fallen rubble stones outside it. Still edge-on.
- Revision build 4: broken lintel; the front half of the gap is open to the sky. The break shows in the top view, and the hero shows a step. Stopped at the build limit.
