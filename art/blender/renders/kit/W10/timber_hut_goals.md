# W10 TimberHut goals (row 3, "C. Timber Hut")

Status after each build: MET / UNMET with one line of evidence.

## ASSEMBLED / HERO
1. [must] Reads as a small log-and-plank hut: plank box body on a grey stone course, cream canvas gable roof, chimney at the rear. Footprint ~16 x 20 studs, ridge ~14, eaves ~8.
2. [must] Roof: cream canvas (#E3CFA0-ish, warm, not white) gable, ridge along Y, chunky orange-brown bargeboards that cross/protrude at the front gable peak and an eave beam sticking out past the gable on both sides.
3. [must] Walls: horizontal overlapping boards (5-7 visible boards per wall height), orange-brown wood one colour; square corner posts at all 4 corners.
4. [must] Grey stone block foundation course (~1.2 tall) visible all round, blocks of uneven length, plus 2 stone entry steps under the door.
5. [must] Front gable faces the viewer-right in the hero: central plank door in a heavy frame, slightly ajar, a glowing lantern on an iron bracket either side.
6. [must] Square grey stone chimney with dark flue at the rear-right, standing ~3 above the roof.
7. [must] Red banner (#B8191F) on its own post with crossbar at the front-left, small cream diamond emblem, swallowtail bottom.
8. [should] Barrel (iron hoops) and crate at the bottom-left; grass tufts (w10_foliage green) at 5+ spots on the stone base; a few rubble stones.
9. [should] Small wooden step platform at the front-right by the door.

## FRONT
10. [must] Front view: symmetric gable silhouette ~1.3x wider than tall (excluding banner), door centred and ~1/3 of wall width, lanterns glowing either side, banner post at left, stone steps below the door.
11. [should] Front gable triangle filled with horizontal boards; ridge beam end and bargeboard tips protrude at the peak.

## SIDE
12. [must] Side view (+x): long wall with one 2x2 cross-framed window glowing amber in the middle, stone course along the bottom, canvas roof as a wide cream band with rope-tied battens, chimney top-right.
13. [should] Side roof shows 3 battens crossing the canvas and small rope ties along the eave.

## TOP
14. [must] Top view: cream rectangle (longer in Y, ~1.1-1.2x longer than wide) split by the ridge, canvas panel seams/battens forming a grid, chimney square near the top-right, wooden steps/platform poking out at the bottom (front).

## PARTS
15. [must] Six separate parts: RoofPanel (cream slab with timber edge boards and battens), RidgeBeam (long beam ~20), WallPanel (~8x8 stacked boards), Floor (plank deck 16x20 with 2-step entry), Doorframe (frame + plank door ~5x8), CornerPost (square post ~9 tall on grey stone footing).
16. [should] Parts each read as the same materials/colours as the hero (wood orange-brown, canvas cream, stone grey).

## VARIATIONS
17. [must] Standard One-Room: hut like the hero but simpler: no banner, one lantern, small side window, chimney, canvas roof.
18. [must] Open Workshop: front wall removed showing an open bay; workbench with a glowing lamp/goods and a barrel inside; roof overhang carried on front posts; canvas roof and chimney.
19. [must] Weathered: grey stone-slate roof (w10_stone shingle rows, cracked/uneven), green moss/vine patches on roof and walls, crooked chimney, no banner.

## PALETTE / SCALE / VFX
20. [must] One key per material: wood #8A4A22, canvas #E3CFA0, rope #C48A38, stone #9A9498, banner #B8191F, iron #575B64, lantern #FFB022 (emissive), foliage #3F8C24. Render wood reads saturated orange-brown, not grey-brown.
21. [must] Walkable: door opening >= 4 wide x 7 tall, floor top at z~1.2, interior clear height >= 7; collision precise; hero tris <= 8000, variants <= 6000, parts <= 1500; 0 problems.
22. [should] VFX: chimney_smoke at chimney tops (hero, Standard, Weathered), heat_glow at both lanterns + window (hero), at workbench lamp (Workshop).
## REVISION goals (from the verifier, all must unless noted)
23. [must] Hero: overlapping horizontal plank walls clearly readable on all 4 sides (visible board seams, warm brown).
24. [must] Front view: closed or near-closed planked door in a heavy frame, two glowing lanterns beside it.
25. [must] Material colours: one colour per material, wood a warm mid-brown with plank richness.
26. [must] Parts: roof panel, ridge beam, wall panel, floor, doorframe+door, corner post all present and readable in the exploded cell.
27. [should] Detail richness: iron hinges, ring handle, rope ties and chunky stone blocks visible at reference scale.
28. [should] Smoke is thin and pale, no dark smear.

## Iteration log
- Build 1: full hut, 6 parts, 3 variants (hero 5156 tris). Canvas battens too strong; foundation thin; barrel hidden; slate flat.
- Build 2: canvas seams + rope ties; foundation 1.55; barrel/crate front-left; bigger tufts; tilted slate; more moss.
- Build 3: deeper board tilt, larger lanterns, king post. 0 problems; hero 5120. (Verifier then FAILED it, 5.5/10.)
- Build 4 (revision): walls rebuilt from clapboard prisms (thick 0.6 bottom lip tapering behind the board above, 6 per wall) so every board throws a dark seam; door leaf closed to ~17 deg with bevelled planks, bigger iron strap hinges and ring handle, threshold; heavier frame; fewer larger jittered foundation blocks; thicker corner posts and rafter tails; eave overhang trimmed to 1.6; barrel/crate +25%; wall panel part as 6 clapboards + end posts; roof panel part flipped so its canvas top faces the camera; moss/vines as leaf_cluster patches; Workshop smoke socket removed. Weathered 6356 over budget.
- Build 5: trimmed Weathered vine/moss clusters (5856/6000), pale thin custom smoke emitters. 0 problems. Seams, door and wall panel now read; wood hue unchanged (shared key).

## Final status (build 5, judged by eye against the reference row)
1. MET - plank hut on grey stone course, cream gable roof, chimney rear; 23.2 x 25.6 x 15.2 incl. banner/overhangs.
2. MET - cream canvas gable, crossed bargeboards at the front peak, eave beams protrude past both gables.
3. MET - 6 clapboards per wall with a dark seam under each, square thick posts at the 4 corners.
4. MET - chunky grey block course with varied lengths/depths all round, 2 stone steps under the door.
5. MET - door gable to viewer-right, heavy frame, planked leaf only slightly ajar, lantern each side.
6. MET - square grey block chimney with dark flue at rear-right, ~3.6 above the roof.
7. MET - red swallowtail banner with cream diamond on its own post + crossbar at front-left.
8. MET - larger hooped barrel and crate front-left, ~10 grass tufts and rubble round the base.
9. MET - small plank platform front-right of the steps.
10. MET - front cell: symmetric gable, centred near-closed plank door, two glowing lanterns, banner left, steps below.
11. MET - gable filled with boards, king post, ridge/bargeboard tips protrude.
12. MET - side cell: long clapboard wall, centred cross-framed amber window, stone course, cream roof band, chimney top-right.
13. MET - battens and rope ties visible on the side roof.
14. MET - top cell: cream rectangle longer in Y, ridge split, seam grid, chimney top-right, platform at front.
15. MET - six parts visible: post on footing, doorframe+door, wall panel of stacked boards, roof panel (top side up), floor with steps, ridge beam.
16. MET - parts share the hero's wood/canvas/stone colours.
17. MET - Standard: no banner, one lantern, small window, chimney, canvas roof.
18. MET - Workshop: open front bay under extended roof on front posts, glowing workbench lamp, barrel and crate.
19. MET - Weathered: grey slate roof with gaps, leaf-cluster moss on roof and vine clumps on the walls, tilted chimney, no banner.
20. MET - palette keys exactly the sheet values, one per material.
21. MET - door opening 4.4 x 7.1, floor z=1.2, clear 7.2; precise collision; hero 5116, variants <=5856, parts <=452; 0 problems.
22. MET - sockets: chimney_smoke on hero/Standard/Weathered, heat_glow on both lanterns + window (hero), lantern (Standard), workbench lamp (Workshop).
23. MET - front/hero/side cells show stacked boards with a dark seam line under every board on all visible walls.
24. MET - front cell shows a closed-looking 4-plank door with two iron strap hinges and a ring handle, lanterns glowing either side.
25. MET (hue limited) - one key per material and plank contrast now comes from the clapboard geometry; the w10_wood hex is the sheet-shared #8A4A22 which every W10 module must use verbatim, so the hut still renders a little more orange than the reference's brown. Changing it needs the sheet planner (see open issues).
26. MET - exploded cell shows all six parts; the wall panel now reads as six stacked boards between end posts, the post is thick on its stone footing.
27. MET - strap hinges, ring handle and rope ties visible in the front/side cells; foundation blocks larger and irregular.
28. UNMET (should) - smoke above the chimney is now pale, but the top cell still shows a grey haze from the smoke sprite seen end-on; that is the shared preview renderer, not a mesh.
