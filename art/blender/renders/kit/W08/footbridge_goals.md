# W08 Footbridge (row 1) goals

Orientation and spec deviation: the spec asks for the bridge along Y (ends at +-4), but the
reference FRONT cell shows the long side (3 posts) and the SIDE cell shows the end (X brace).
The runner's cameras are fixed (front az 0, side az 90, top straight down with -Y at the bottom),
so the bridge runs along **X** to make FRONT and SIDE match. Planks therefore run along Y and
stringers along X. The cost is that the TOP cell shows the bridge horizontal while the reference
draws it vertical: the reference sheet is internally inconsistent here, and no single orientation
can match FRONT, SIDE and TOP with these cameras. All cameras are also perspective (no ortho
option for a module), so the SIDE cell cannot render as a flat orthographic view.

## ASSEMBLED / HERO
1. [must] (verifier) Long low plank deck, about 2:1 or longer, reads as a long bridge — UNMET (partial): deck now 10 x 4.1 (2.4:1), posts only 1.6 above the deck and the iso cell reads clearly longer and lower than before, but the fixed perspective camera still makes the screen silhouette ~1.4:1 against the reference's ~1.9:1, and the length runs only slightly diagonal (HERO_AZIMUTH -26; -38 made it stubbier).
2. [must] Posts rise from the ground through the deck; deck at ~55-60% of post height — MET: deck top 2.0, posts 3.6; hero/front show the deck band just above mid-post like the reference.
3. [must] 3 square posts per side with flat top, rope collar near the top and brass nail — MET: 3 posts per side with brass caps, chunky double rope collars, nail dots on the faces.
4. [must] (verifier) Rope sagging between post tops on both sides, thick tan twisted cord; collars are wrapped rope, not flat bands — UNMET (colour only): ropes are now thick (r 0.19) two-strand twisted cords and collars are round chunky tori, matching the reference shape; but the mandatory shared key w08_rope #D4A857 still renders more golden-yellow than the reference's tan. The palette must be copied verbatim, so this needs a sheet-wide palette change (shared_lib_requests).
5. [must] ~15 chunky transverse planks with visible gaps and slight jitter — MET: 15 wide chunky planks with dark gaps, slight height/rotation jitter visible in hero and top.
6. [should] Brass nail heads read as small round copper dots — MET: visible on post faces in front/hero.

## FRONT (long side)
7. [must] 3 posts, deck band at mid-height, rope drooping between post tops — MET: front cell matches the reference's long-side view closely.
8. [must] Diagonal braces below the deck visible from the long side — MET: knee braces from each post foot up to the deck read as V shapes.
9. [should] Thick edge beam band under the plank edge — MET: fascia band visible under the plank line.

## SIDE (end)
10. [must] (verifier) 2 posts with rope wraps, X brace under the deck, flat orthographic look — UNMET (camera): 2 end posts with collars, deck band and the X brace are present, and lower posts make it flatter than before, but the fixed perspective side camera still shows the deck receding as a box with the near posts large. Not fixable from a module.

## TOP
11. [must] (verifier) Vertical bridge with 2 edge stringers and corner posts poking beyond the deck — UNMET (impossible with fixed cameras, see note): edge beams, plank stripes and 6 posts poking past the deck edge are all visible, and the shadow is shorter now, but the bridge lies horizontal because FRONT must show the long side.

## PARTS
12. [must] 6 separate parts: Post, RopeSegment, Plank (3 planks), Stringer, Crossbeam, Brace — MET: all six exist and render.
13. [should] (verifier) Parts legible and spaced: post with nail dots and collar, rope arc, plank group, stringer, crossbeam, L brace — UNMET: staggering removed from the plank group and the brace shortened to 2.4, but the runner's grid puts the tall post and brace in the front row, so they still partly hide the plank group and rope behind them.
14. [should] Rope segment is a sagging twisted arc — MET: two-strand twisted arc visible behind the brace.

## VARIATIONS
15. [must] A. Short Span: ~4.4 long, 2 posts per side, one swag each side — MET: compact bridge with 4 posts and 2 twisted ropes.
16. [must] B. Arched: deck rises in a smooth ~1.2 arch, end posts, rope follows the rail — MET: humped deck in 3-segment curved stringers; rope now follows the arch just above the rail (lowered).
17. [must] C. Broken: missing planks, crooked planks, leaning post, hanging frayed rope, dangling plank — MET: sparse crooked right half, leaning front-right post, rope hanging down, dangling plank.

## PALETTE / SCALE
18. [must] All timber one key w08_wood #A8582A, rope w08_rope #D4A857, nails w08_nail, stones w08_stone — MET: timber renders orange-brown like the reference; 0 shading problems.
19. [should] (verifier) Scale ~8 long, 5 wide, deck z~1.6, walkable width >= 4 — UNMET (deliberate): width 5.3 incl. posts, walkable 4.1, deck 2.0 (within the verifier's 1.6-2.0), but length is 10 to deliver the 2:1 "long bridge" must.
20. [must] Budgets, nothing below z=0, 0 problems — MET: hero 3824/5000, variants <= 2984/3000, parts <= 232/1500, 0 problems.
21. [should] Small dressing at the feet (rubble stones) — MET: small grey stones at post feet (reference shows almost none).

## Iteration log
- Builds 1-4 (first run): first pass, budgets fixed, deck 2.6, length 9.6, HERO_AZIMUTH -32.
- Revision build 1: deck 2.0, posts 1.6 above deck, length 10, posts at y +-2.35, 15 wide planks, two-strand twisted rope r 0.19, round collar tori; arched/broken over budget.
- Revision build 2: lighter rope/collar tessellation -> broken in budget; arched still 56 over; HERO -38 looked stubbier.
- Revision build 3: HERO -18 (reads longer), rounder collars, arched rope lowered; arched 48 over.
- Revision build 4: arched 3 stringer segments (in budget), HERO -26 for a little diagonal, shorter brace part. 0 problems.
