# R04 Stormglass goals (revision 2)

Status after revision build 4 (final, at the build cap). Each goal is marked MET or UNMET, with evidence from stormglass_compare.png judged cell by cell against the reference row. V = a verifier goal added as a must.

## HERO (assembled iso)
1. [must] A teal crystal tree rises from a wide tan sand mound. The crystal is about 3/4 of the height and the mound about 1/4. MET: the teal limbs fill the upper 3/4 above a low tan mound.
2. [must][V] The limbs are fat coral prisms: the trunk is about 2 thick, 8-sided, and fills about 1/2 of the footprint width. MET: the limbs are now 2.2-2.6 thick, bulge slightly and are faceted. The crystal mass spans about half the mound, like the reference.
3. [must][V] Y fork: a tall trunk (about 7.5), a thick right branch angling up-right and a shorter left branch going out-left (about 5), clearly splayed. MET: the left arm leans about 55 degrees out-left and the right arm curls up to the right. The fork is low (about 3). In the iso the trunk sits partly behind the right arm, so the tallest tip reads less than in the reference.
4. [must] The sand mound is a low faceted dome with an irregular outline, about 9-10 x 8-9 x 2.3. MET: the outline is wobbly and the dome is low.
5. [must][V] 9-12 dark brown-grey angular rocks of 0.8-2.5+ studs ring the rim: big ones at the front-left and front, mid-size ones around the rest, and 2 poking through the sand. MET: 9 rim rocks sit at the base edge, with a big chunky front-left rock and a big front rock, plus 2 small pokers. They are no longer black dots.
6. [should][V] A small third stub at the back. UNMET: the stub exists but is mostly hidden behind the trunk in the hero and side cells.
7. [should] Hero is about 9-11 wide x 8 tall. MET: 11.2 x 9.9 x 8.0.
8. [should][V] Facets are irregular and the limbs slightly taper, coral-like rather than machine-straight. MET: each limb is a 7-9 ring swept tube with a radius bulge, ring wobble and vertex jitter, and the right and left arms curve upward.

## FRONT
9. [must] Front cell: the left arm goes out-left, the right arm up-right and the trunk between them, with tips at different heights. MET: the front cell shows a fan with the left arm out-left and the right arm up-right. The right arm leans toward the camera, so the Y is a little less open than in the reference.
10. [should] The mound is a wide low hump with rocks breaking the outline at both ends. MET: big rocks show at both ends.

## SIDE
11. [should][V] The side cell shows overlapping limbs (a Y), not a single column, with rim rocks at the ends. MET: the side cell now shows a clear Y of two limbs with rocks at both ends.

## TOP
12. [must][V] Top cell: three arms radiate from the middle like a cross over round sand with rim rocks. UNMET: a long left arm and a front-right arm with its cap show, and the trunk cap leans back-right. The arms still overlap at the centre, so the top reads as a cluster more than the reference's crisp three-armed cross. The rocks do ring the disc.

## PARTS
13. [must][V] Main Branch is about 6.5 tall, Y-forked and fat. MET: it is 6.7 tall, a fat trunk with an up-right arm, and the Y is obvious.
14. [must][V] Side Branch is a small Y twig about 3 tall and about 1+ thick. MET: it is 3.2 tall, with two fat arms that read as a Y. It is still smallish beside the Main Branch, as in the reference.
15. [must][V] Sand Base is the mound with its rim rocks, about 9 x 8 x 2.5. MET: 10.9 x 9.8 x 2.3 with the full rock ring.
16. [must][V] Branch Stub is a roughly horizontal broken limb about 4 x 1.8 x 1.8, with a slight upward tilt and a cut hex end. MET: 4.3 x 1.9, tilted up, with a chamfered cut cap. The parts cell's automatic grid places it top-right, not left of the Main Branch; the module cannot control that layout.

## DROPS / DEPLETED
17. [must] Two chunky faceted teal shards: one lying flat (about 1.5 x 1 x 1) and one taller (about 1 x 0.9 x 1.5). MET: one lies flat and one stands upright.
18. [must][V] Depleted: a flatter sand mound (about 2) with the same rock ring, no crystal and a visible centre dent. MET: the 1.2-stud crater with a 1.7-stud flat floor reads as a shaded hollow in the depleted cell. Its rim rocks look larger than the reference's.

## PALETTE
19. [must][V] The crystal (r04_stormglass, #28BDAA) renders bright aqua-turquoise and glassy, not pale cyan. MET: the limbs render saturated teal-aqua like the reference.
20. [must][V] The sand (r04_sand, now #CFB08C) renders pale warm tan, not orange. MET: the mound renders light tan in every cell. It is a touch warmer than the reference in the depleted close-up.
21. [must] The rocks (r04_storm_rock, now #625454) render dark brown-grey, clearly darker than the sand and not black. MET.

## VFX
22. [must] ore_glint on the trunk front and each branch tip, a cyan heat_glow with PointLight at the fork, dust over the sand in sand colour, harvest_hit at (0,-3,4) in teal and harvest_deplete at (0,0,0.8). MET: all sockets were added, and the glints and dust show in the renders.

## Iteration log
- Revision build 1: rewrote the limbs as swept 8-sided tubes with chamfered caps, built a custom irregular sand dome with a flat base and a crater option, and moved the rocks out to the rim. Lightened the sand to #D8B080, the rocks to #625454 and the glass to #28BDAA. The sand was tan but the limbs were still thin.
- Revision build 2: limbs fattened 1.2x and given resampled bulges. The sharp-walled crater shows a little. The Y read in the front cell, but the side was still one column.
- Revision build 3: spread the branch azimuths (right to the front-right, left out-left, stub to the back) and set the sand to #CFB08C. The dent was deepened to 1.2 and the twig fattened 1.45x. The side now shows a Y, but the top view was still a cluster.
- Revision build 4: increased the horizontal reach (left arm to x=-3.6, trunk top leaning back-right, right arm to the front-right) and made the rim rocks 1.18x bigger. The top view shows more separate arms, and the rock rim is chunky. Stopped at the 4-build cap.
- Open: the top cross is not as crisp as the reference's (goal 12), and the back stub is hidden (goal 6). The palette retune of the sheet keys needs the planner to sync (only this module uses them).
