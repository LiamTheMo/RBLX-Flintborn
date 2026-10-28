# R03 Amethyst goals

Status after the latest build (revision build 4), judged by eye against the reference row.

## ASSEMBLED / HERO
1. [must] Hero reads as a hollow geode: thick grey rock shell forming a rounded dome open to the front with a big dark-purple cavity. -- MET: the hero cell shows a grey slab ring around a large dark-purple opening full of crystals.
2. [must] Shell ~8 studs wide, ~7-8 tall; silhouette about as wide as tall. -- MET: 8.8 x 8.8 x 7.3 studs; the hero cell is about as wide as tall, like the reference.
3. [must] Cavity opening ~4.5 wide x ~5 tall, oval, rim ~1 stud thick. -- MET: the front cell's opening fills about 55% of the shell width, oval, with a ~1 stud rim all round. It is still a little smaller than the reference's.
4. [must] 5-6 vivid violet crystals fan up from the cavity floor: tallest in the centre (~4.5), two side ones leaning out ~20-25 deg (~3.2), small ones at the front (~2). -- MET: the fan is now upright, with a fat tall centre crystal and the sides at about 22 deg. It matches the reference fan better than the old flat splay.
5. [must] Chunky lip of 3 low rocks wraps the front-bottom in a crescent and hides the crystal bases. -- MET: three wide, angular lip rocks across the front-bottom, about 1/4 of the height.
6. [must] (verifier) Shell is chunky FACETED SLABS with a pronounced ~1 stud rim, not smooth boulders. -- MET: the shell is now 6 chamfered prism slabs with flat planes and crisp edges, with no rounded blobs. The seams are more regular than the reference's (a little masonry-like).
7. [should] (verifier) Rim thickness around the opening reads thick and uniform. -- MET: the front cell shows an even ~1 stud rim round the top and sides; the crown no longer dominates.
8. [should] (verifier) Consistent low-poly planar facets on the hero and parts. -- MET: every rock is a flat-faced prism (shell, lip, bottom shell, depleted), and no fine roughness noise is left.

## FRONT
9. [must] Front view: a ring of rock around an oval dark-purple opening, with crystals filling its lower 2/3 and the tallest tip at ~3/4 of the opening height. -- MET: the front cell matches this layout.
10. [should] Front view roughly symmetric, with 3 big lip blocks across the bottom. -- MET.

## SIDE
11. [must] Side view: the shell wall rises as a tall slab on the right, with crystals visible on the left and a lip rock at the bottom-left. -- MET: the tall wall is on the right, violet crystals stick out on the left, and the lip rock is at the bottom-left.
12. [should] (verifier) The side wall is a broad, rounded ovoid slab leaning over the cavity. -- UNMET: the wall is broad but reads as a straight-sided slab tilted back about 24 deg (the tilt is needed for the top view), while the reference's ovoid curls forward at the top.

## TOP
13. [must] (verifier) Top view: a round ring of rocks around an open dark-purple pit full of crystals. -- UNMET (improved): the ring of rocks and the dark pit with the crystal fan now show in the front/centre. The back crown band still covers about 40% of the cell, so the pit is not centred as in the reference.

## PARTS
14. [must] (verifier) AmethystTopShell is a curved, arched half-dome roof slab with a hollow dark underside. -- MET: the parts cell shows one arched hood of 4 overlapping slabs closed by a back plate, with the dark r03_geode_dark underside visible. It no longer reads as a ring of round rocks.
15. [must] AmethystBottomShell is a low U-shaped crescent of 4 chunky rocks (~8 x 5 x 3) with a dark inner floor. -- MET: 4 angular blocks in a U with a dark floor, 8.0 x 4.6 x 3.0.
16. [must] Four distinct crystals: tall (~4), B leaning (~3.5), C (~3), D small (~2); slender, hexagonal, with pointed tips. -- MET.

## DROPS / DEPLETED
17. [must] Two lumpy faceted violet nuggets (~1-1.4 studs): one lying, one upright. -- MET.
18. [must] Depleted: a low rock crescent with an empty dark cavity, NO crystals, a cracked half-ring standing at the back-right (~3.5 high) and rubble; footprint ~8 x 6. -- MET: the half-ring is 3.6 high at the back-right and clearly visible, with a low crescent, a dark floor, 3 rubble rocks and no crystals.

## PALETTE / SCALE / VFX
19. [must] Shell, lip and rubble all use the one r03_rock (#8C7E78), rendering warm grey-taupe. -- MET.
20. [must] Crystals and drops use the one r03_amethyst (#8A4BC9), rendering vivid lilac-violet. -- MET.
21. [must] Cavity lining uses the one r03_geode_dark (#3B2358) only on inner surfaces (lining band, back face, floors, TopShell underside). -- MET (waivered with kit_shading_ok).
22. [should] VFX: harvest_hit (0,-3,2.5) with amethyst chips; ore_glint (0,-1,3) with small violet glints and motes plus a violet PointLight; harvest_deplete (0,0,0.5) at a smaller scale. -- MET: the sprites are smaller and violet. A faint harvest_hit dust puff still shows at the front.
23. [should] Within budgets and nothing below z=0. -- MET: hero 784/4500, TopShell 312, BottomShell 172, crystals 32, drops 80, depleted 536/2500; 0 problems.

## Iteration log
- Earlier run (4 builds): an arch of subdivided ico slabs. The verifier failed it for boulder-like slabs, the top view, the TopShell ring and flat crystals.
- Rev build 1: replaced every rock with chamfered prism slabs (custom `chunk`), with the arch tilted back 22 deg and the crystals made more upright. Planar facets fixed, but the shell read as a regular brick arch with deep gaps.
- Rev build 2: added per-slab radius and front jitter, more tilt (28 deg), fatter crystals and wider lip rocks. Still masonry-like, and the side view was a barrel.
- Rev build 3: overlapped the slabs (no gaps) and tapered their backs for a rounded dome. The seams are subtler.
- Rev build 4: added irregular bumped outlines, 5-sided angular lip and basin rocks, and set the tilt to 24 deg. This was the build cap.
- Goal 13 is still UNMET. A closed dome seen straight down always shows its crown and back. The reference top cell is drawn from a steep front-top angle, not straight down, so the pit cannot be centred without removing the dome's back, which would break the hero, front and side cells. A camera tilt for the TOP cell would be needed (shared-lib request).
