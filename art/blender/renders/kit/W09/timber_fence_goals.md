# W09 TimberFence goals (row 3)

Status after the latest build (revision build 4): MET / UNMET, with one line of evidence judged by eye against the reference row.

## ASSEMBLED / HERO
1. [must] The hero reads as a 2-rail ranch fence section about 12 studs long, clearly wider than tall. MET: the hero cell reads as a long 2-rail fence, about 2x wider than tall, like the reference.
2. [must] Two chunky square posts (about 1.2 wide) stand at the ends, each topped by a proud square cap block. MET: chunky posts at both ends with bevelled caps that overhang the posts.
3. [must] (verifier) The posts tower over the rails: the post top sits about 1/3 above the top rail, and the rails are thick. MET: the posts now rise about 1.8 studs above the top rail (post 6.0, rail top 4.2). The rails are 0.85 thick and read chunky.
4. [must] Two parallel rails pass in front of the posts, and their ends stick out past the posts. MET: the rails sit on the post fronts, with diagonal-cut ends poking past both posts.
5. [must] A rope X-lashing crosses the front of each post at the top rail, with extra wraps under the cap on the right post. MET: a tan X shows on the left post, and the X plus 2 wraps show under the cap on the right post.
6. [must] (verifier) The base has lush, layered leafy clumps 2-3 studs tall that hide the mound edge at the front and back, with a soil rim showing. MET: overlapping leaf clumps run the whole front and sit at the back of both posts. A brown soil rim shows under them, and the flat turf plate is gone.
7. [must] (verifier) 4-5 clearly visible white daisies with yellow eyes sit near the left post. MET: five daisies, each about 1.1 studs across, sit in front of the leaves either side of the rock and read clearly in the hero cell.
8. [must] A grey rock about 2 studs wide sits at the front bottom between the left post and the middle. MET: the grey rock now sits in front of the leaves, flanked by daisies, as in the reference.
9. [should] The rails are chunky and slightly uneven, and the posts and caps show bevels. MET: there is a visible kink at mid-rail, and the bevels show on the posts and caps.

## FRONT
10. [must] The front view shows the two posts, the two rails, rope X-lashings on both posts and tufts along the base. MET: the front cell shows both posts, both rails, both rope Xs and a continuous leaf band with daisies and the rock.
11. [should] (verifier) The front cell has no blank white patch. UNMET: a white band still shows above the front cell. It comes from the shared front-camera framing and background in the compare renderer, not from the model; nothing in the module changes it.
12. [should] In the front view the top rail sits at about 2/3 height and the bottom rail at about 1/3, with a clear gap between them. MET: the top rail is at about 65% and the bottom at about 33%, with a clear gap.

## SIDE
13. [should] The side view shows the post with the rails in front and a proud cap. MET: the three-quarter side cell shows the rails in front of the tall capped post, with leaves at its foot.

## TOP
14. [must] The top view shows a long thin bar (the rails) with square post caps at the ends and green at the base. MET: a thin rail bar with square caps at both ends and leaves along the front and back. The soil shows a little in the middle.

## PARTS
15. [must] All five parts are present and recognisable: post, top rail, bottom rail, rope-joint stub and cube cap. MET: all five appear in the parts cell.
16. [should] (verifier) The rope joint is a thick X-wrapped stub with 4-5 turns. MET: the rope is now 0.26 thick, with 4 wraps and an X covering the middle of a 2.5-tall stub, and it reads as a chunky tan lashing.
17. [should] The fence post part shows a dark slot near the top, a rope groove and a small knot hole low. MET: all three are visible on the post part, though small at cell size.

## VARIATIONS
18. [must] The Straight variant is a clean 2-rail section with ropes and small clumps only, and no rock. MET: a clean section with tall posts, small leaf clumps, 2 daisies and no rock.
19. [must] The Corner variant has 3 posts and two rail pairs meeting at a taller capped corner post, with rocks and clumps. MET: an L-shaped corner whose corner post is the tallest, with lashings, clumps at all three posts and 2 rocks on an irregular L-shaped soil mound.
20. [must] The Damaged variant has its left post leaning about 15 degrees, the top rail snapped with a jagged end, the bottom rail tilted down, a loose rail on the ground at the front, a rock and clumps. MET: the post leans, a snapped stub and a hanging rail are visible, the bottom rail is tilted, and the loose rail lies pulled out in front, angled, with a splintered end.

## PALETTE (one base colour each)
21. [must] All timber is warm, saturated orange-brown (w09_wood). MET: the timber renders the same warm orange-brown as the reference.
22. [must] The rope is pale tan (w09_rope) and clearly lighter than the wood. MET.
23. [should] The end grain is grey-brown, the rock cool grey, the leaves saturated green (w09_foliage), the soil brown (w09_soil) and the daisies white with a yellow eye. MET: the colours match. The foliage renders a little brighter than the reference, but the sheet palette is shared and must stay verbatim.

## SCALE / BUDGET
24. [must] Tris are under budget, and every build ends with 0 problems. MET: hero 3660/5000; variants 2150, 2910 and 2444 out of 3000; parts at most 536/1500; 0 problems.

## Iteration log
- Earlier run: builds 1-4 produced the first version (see the verifier failure: short posts, flat turf plate, tiny daisies, thin rope joint).
- Rev build 1: posts raised to 5.7 and caps enlarged to 1.5; rails moved to z 3.8 and 1.9; the turf plate was replaced by a soil mound plus leaf_cluster clumps at the front and back. The daisies were redone at 1 stud with flat petals, and the rope joint was given a 0.26-thick rope. The posts became taller, but the clumps were small and spiky.
- Rev build 2: posts raised to 6.0 (corner post 6.9); clumps scaled 1.3x with shorter blades; the corner mound was changed to an irregular L. The leaves became dense, but the daisies were hidden behind them.
- Rev build 3: daisies moved in front of the leaves and raised; they now read clearly.
- Rev build 4: rock moved forward in front of the leaves and daisies spread either side of it; the hero base now matches the reference's rock and daisy group.
