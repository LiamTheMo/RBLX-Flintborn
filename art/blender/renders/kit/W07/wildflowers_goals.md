# W07 Wildflowers (row 3): goals (revision 3)

Reference: art/reference/kit/rows/W07_row3.png. Units are studs, and the front faces -Y. Each goal's status is updated after every build.

## ASSEMBLED / HERO
1. [must] Three clearly different flower shapes are readable: purple hanging fluted bells, a flat blue 5-point star with a white dot, and pink rounded cup blooms. — MET: the hero shows fluted purple hanging bells, a flat blue 5-point star with a white dot, and open pink cups.
2. [must] The big purple bell hangs mouth-down from a long arching stem at top left, with its top near the cluster's top. — MET: the big bell hangs mouth-down from the long arching crook at top left, with its stem apex near the top.
3. [must] The blue star is at upper right, the highest flower, facing up or toward the camera (not edge-on), and about 1.6 across. — MET: the blue star is the highest head at upper right, tilted to show all 5 points (about 1.7 across).
4. [must] (verifier) There are two fat pink cup blooms, one centre and one lower right. They are rounded deep cups about 1.1-1.3 wide with petals curling up and in, and a visible pale centre. They are not flat saucers. — MET: two rounded open pink cups (centre raised, lower right), about 1.3 wide, with lobed petals rising around a white centre. They read as cups, not saucers, but are a little smaller than the reference's.
5. [must] (verifier) A dense base of 8-10 big, separate, pointed, faceted light-green leaves fans clearly wider than the heads. Distinct leaf tips show in the silhouette, and each leaf shows two facet tones along its crease. The base is not a closed dark bowl. — MET: 10 broad, light-green, creased leaves with pointed tips fan out past the heads. Each shows two facet tones, front leaves arch low and back leaves stand up. The mound is about 1/4 of the height (the reference's is closer to 1/3).
6. [must] The hero is about 4.5 wide x 5 tall studs (width/height about 0.9-1.0), with the leaf fan as the widest element. — MET: 5.0 W x 4.4 D x 5.4 H, and the leaf fan is the widest element in the hero cell.
7. [should] (verifier) One small grey stone (about 0.6 wide) and one orange-brown chip (about 0.4) are tucked at the foot of the leaves, partly under the front leaf tips, not floating outside. — UNMET: both are enlarged and moved in to about 1.4-1.5 studs. The chip peeks out at the front in the front and side cells, but the leaves now hide the stone in the hero view.
8. [should] (verifier) The stems are dark green, kinked and hexagonal, thick enough to read at game distance (radius about 0.15+), with heads at varied heights (about 2.5 to 5). — MET: the stems are radius 0.15-0.16, kinked and 6-sided, and read clearly. The heads sit at about 2.4 / 2.8 / 3.0 / 4.5 / 5.0.
9. [should] (verifier) The heads are large relative to the cluster: the bell is about 1.3 wide, the star about 1.6 and the pink cups about 1.2. The cluster should not read as sparse. — MET (partly): bell 1.3, star 1.7 and pink cups 1.3. The heads are bigger and fuller, but the cluster is still a bit airier than the reference because the stems are long.

## FRONT / SIDE / TOP
10. [must] FRONT: the bell is on the left, the blue star top right, pink in the middle and right, and leaves fan at the base. — MET: front: bell on the left, star at top right, pink cups in the middle and right, leaves fanning at the base.
11. [should] SIDE: an arched stem with a bell hanging to one side and leaves at the base. The pink cups do not dominate the view. — MET (partly): the side shows the arching stem with the bell to one side and leaves at the base, but the pink cups still sit large in front of it.
12. [must] TOP: a round leaf rosette with flowers poking up in the middle, and green leaf tips visible around the full ring. — MET: top: a ring of broad pointed leaves with tips visible all round, with the bells, star and pink cups clustered in the middle.

## PARTS
13. [must] WildflowerStem: a 6-sided green stalk about 3 tall with a kink halfway. — MET: a 3.0 tall green 6-sided stalk with a mid-height kink.
14. [must] WildflowerFlowerHead: a purple faceted bell with a flared lobed rim and a small green cap. — MET: a purple faceted bell with a flared lobed rim and a green cap.
15. [must] WildflowerLeaf: a broad pointed leaf about 1 wide x 1.8 long with a visible central crease. — MET: a broad pointed leaf, 1.0 x 1.7, with a central crease.
16. [must] The part names are unique: WildflowerStem / WildflowerFlowerHead / WildflowerLeaf. — MET: the runner lists WildflowerStem / WildflowerFlowerHead / WildflowerLeaf with no .001 duplicates.

## VARIATIONS
17. [must] PurpleBell: a tall stem arching over, 3 hanging bells of different sizes, and leaves at the base. — MET: a tall arching stem with 3 bells of different sizes over 6 separate splayed leaves.
18. [must] BlueStar: 3 flat 5-point blue stars with tiny white centre dots on upright stems. — MET: 3 flat blue stars with white dots on upright stems over splayed leaves.
19. [must] PinkBloom: one large open pink cup on top, a smaller bloom on the left, a closed bud on the right, and leaves at the base. — MET: a large open pink cup on top, a smaller bloom on the left and a closed bud on the right, over splayed leaves.
20. [must] (verifier) Variant base: 5-6 separate leaves splayed outward at 30-45 degrees, each tilted differently, with an open spiky spread that is not a closed bowl. — MET: 6 separate broad leaves splay out at 30-50 degrees with different rolls. The spread is open and spiky with visible tips, not a bowl.

## PALETTE / SCALE / TECH
21. [must] One key per material: leaves and stems w07_leaf #4E9A2C; purple #8E5AD8; blue #4A62E0; pink #F48FB1; centres and dots w07_petal_white #F2EAD2; stone #8E8E94; chip w07_root #B8672A. There is no w07_stamen, no shade variants and no height or facing tint. — MET: the palette is the sheet values only, with no stamen key, no shade keys and 0 problems. w07_wood is kept because the spec lists it, though no mesh uses it.
22. [must] Tris are within budget (hero 2000, variants 1200, stem 100, head 350, leaf 150), collision is none, nothing is below z=0, and the build reports 0 problems. — MET: hero 1748/2000, variants 1008/684/1152 of 1200, stem 44, head 188, leaf 48. Collision is none and there are 0 problems.

## Iteration log
- Revisions 1-2: base geometry, renamed parts and palette. The verifier failed it at 6/10 because the leaves formed a dark bowl, the pink cups were flat saucers, the stems were thin and the stone and chip were outside the mound.
- Rev3 build 1: 10 leaves with per-leaf yaw, pitch and roll; deeper pink cups; stems thickened to 0.15; stone and chip enlarged and moved in. The leaves became separate but read as thin spikes, and the pinks looked like tulips.
- Rev3 build 2: the pink profile opened into a wide cup tilted to the camera, and the leaves were made bigger. The pinks read well, but the leaves were still low and spiky.
- Rev3 build 3: the leaves were pitched higher with less droop. The mound was taller, but the front leaves showed their shaded undersides.
- Rev3 build 4: the leaves were reoriented by facing: the front leaves are low (18-24 deg) so their tops face the viewer, the side leaves roll toward the front, and the back leaves stand at 55-70 deg. The leaves are now broad, light and distinct; the variants use the same scheme. Stopped at the 4-build cap. Open issue: the stone is hidden by the leaves in the hero view.
