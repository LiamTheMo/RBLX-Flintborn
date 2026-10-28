# W08 RopeCrossing goals (row 4)

Orientation: the reference FRONT cell shows the long elevation and SIDE shows it end-on. The kit's FRONT camera looks along +Y and SIDE along -X, so to match those two cells the bridge length must run along X. The spec says Y. The reference TOP cell is drawn rotated 90 degrees from its own FRONT cell, so no single orientation can match FRONT, SIDE and TOP at once. I kept X (16 x ~8 x 7.8 studs) and document it here and in the module docstring.

## ASSEMBLED / HERO
1. [must] Reads as a suspension rope bridge: a sagging plank deck between two pairs of grey anchor stones, one pair at each end.
2. [must] Size ~16 long x ~7-8 wide x ~7.5-8 tall; deck width 3.4 (>= 3); deck sags ~1.2 studs at mid-span.
3. [must] 4 tall orange-brown square end posts with flat tops, each with a thick rope collar near the top and a brass nail.
4. [must] One thick main rope per side sweeps from the post collar down to ~2 studs above the deck at mid-span.
5. [must] ~10 vertical hanger ropes per side between the main rope and the deck edge, shortest at mid-span.
6. [must] ~13-14 chunky planks (0.35 thick) across the deck width with small gaps, each tilted to follow the sag.
7. [must] (verifier) Red flags are small cloth tags (~0.6 x 1.1) hanging just under the collar on the inner faces of the posts, not long strips.
8. [should] 1-2 small rubble stones beside the front-left anchor stone.
9. [must] (verifier) Anchor stones are massive, chunky, tapered grey blocks with a flat top, about 40-50% of the visible height and clearly wider than the post bases.
10. [must] (verifier) Rope is thick (main rope radius ~0.28) and reads as twisted rope with strand ridges.
11. [must] (verifier) Rope colour reads as pale beige tan like the reference, not saturated yellow.

## FRONT
12. [must] Long elevation: posts at both ends rise ~1.4-1.6x the stone height above the stones, with the rope curve and hanger fence between them and the plank deck curve below.

## SIDE
13. [must] (verifier) End-on view shows a broad solid wooden end wall between the two posts, a rope arc between the collars, and big stones under the posts.

## TOP
14. [should] (verifier) Planks form a ladder between 4 corner stones, with two side ropes clearly along the deck edges. The long axis matches the reference top (vertical).

## PARTS
15. [must] Six parts: MainRope (arched twisted rope ~8 long with end loops), HangerRope (vertical 2.5 with wraps top and bottom), Plank (3.4 x 0.6 x 0.35), EndPost (0.8 x 0.8 x 5.5 with collar and nail), AnchorStone (~3.4 cube-ish faceted block with flat top), SideRope (~6 long, sagging, loop knots).

## VARIATIONS
16. [must] A. Narrow: deck ~2 wide, fewer hangers, two anchor stones per end.
17. [must] B. Wide: deck ~6 wide, doubled main ropes per side, extra posts (a pair at each corner), four large anchor stones.
18. [must] C. Damaged: missing planks, some tilted or hanging, one main rope snapped and hanging down on one side, one hanger detached.

## PALETTE
19. [must] w08_wood (#A8582A) on planks, posts and end walls renders warm orange-brown like the reference.
20. [must] w08_stone (#9CA2AA) is a cool light grey, w08_nail is brass, w08_banner is red. There is one key per material.

## Iteration log
- Builds 1-3 (earlier run): stones went from plain boxes to boulders and back to tapered blocks; Wide was trimmed. The verifier failed the result: stones too small, flags too long, rope thin, side cell lacked the end wall.
- Build 4 (revision 1): stones 3.4 x 3.4 x 3.2 with a stronger taper, posts moved to the stone centres, two-strand twisted main ropes (r 0.28), wooden end walls (two stacked beams) lifting the deck ends, swag rope between the collars, flags cut to 0.6 x 1.1 tags on the inner faces under the collar, 10 hangers, 0.35 planks, thicker edge ropes. Wide was 5700/5000 tris (1 problem).
- Build 5 (revision 2): Wide trimmed (no chip rocks, 2-ring collars on the extra posts, 11 planks, 5 hangers, coarser twist), 4916/5000. 0 problems. The bigger stones, twist, tags and end wall all read clearly.

## Status after build 5 (judged by eye against the reference row)
1 MET: two grey stone pairs with a sagging plank deck between them, recognisably the reference bridge.
2 MET: the stones and deck are in proportion. The deck dips clearly at mid-span. Size is ~16 x 8 x 7.8.
3 MET: 4 orange square posts with fat tan triple collars near the top. The brass nail dot sits on the outer face.
4 MET: a thick twisted main rope swoops from each collar to about 2 studs above the deck.
5 MET: 10 hangers per side form a lighter fence than before and are shortest at the centre.
6 MET: 14 chunky planks with small gaps follow the curve.
7 MET: the flags are now short red tags just under the collar on the inner post faces (visible on the right-hand posts in the hero and front cells), no longer long strips.
8 MET: two small faceted rubble stones sit at the front-left stone.
9 MET: the stones are big tapered flat-topped blocks filling about the lower 40-45% of the hero, much wider than the posts, like the reference.
10 MET: the main ropes are clearly thicker and show spiral strand ridges (most visible in the MainRope part and the top cell).
11 UNMET (convention): the rope still renders a warmer, more saturated yellow than the reference's beige. The colour is the sheet-shared key w08_rope #D4A857, which must be copied verbatim by all four W08 modules, and a second rope key would be a shade pair. It needs a sheet-wide palette change (requested).
12 MET: the front elevation shows posts at both ends over big stones, with the rope curve, hanger fence and deck curve between.
13 MET: the side cell now shows a broad wooden end wall between the posts with a rope arc between the collars and big stones beneath, like the reference.
14 UNMET (should, documented): the top shows a plank ladder between 4 corner stones with edge ropes along the deck, but it runs left-right. Length on X is needed to match FRONT and SIDE (see the orientation note).
15 MET: all six parts are shown: the arched twisted main rope with loops, the hanger with wraps, the plank, the collared post with nail, the flat-topped block stone and the twisted side rope with loops.
16 MET: Narrow is shorter, with a ~2-stud deck, 6 hangers and two stones per end.
17 MET: Wide shows a broad deck, paired posts at each corner, doubled main ropes and four large stones.
18 MET: Damaged has gaps in the deck, tilted hanging planks, the front main rope snapped and dangling, and one hanger swinging loose.
19 MET: the wood renders warm orange-brown, close to the reference.
20 MET: grey stones, brass nails and red flags, with one key each.

Origin and z: every asset is finished by Asset.finish() (origin at the bottom centre). Stones and rubble sit on z=0 with no sink, and the runner reported 0 problems.
