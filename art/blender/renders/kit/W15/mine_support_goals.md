# W15 row 1 MineSupport - goals

Status: revision builds R1-R3 (latest R3). Goals 1, 2, 7 and 12 were re-judged after the verifier's audit.

## ASSEMBLED / HERO
1. [must] Symmetric timber portal: 2 square upright posts on grey stone footing blocks, 1 horizontal lintel across the top, square collar blocks at both post tops, a long diagonal brace per upper corner forming the portal triangle. - MET (R3): long chunky braces in both corners now read clearly in the front and iso cells; see goal 23.
2. [must] Big faceted grey rocks (5-7 large ones) hug both sides of the frame and arch over the lintel; rock mass at the back is ~1.3x as tall as the frame. - MET (R3): cut to 7 big rocks that arch over the lintel; the crown is 20.9 against a 16.2 frame.
3. [must] Dark recessed tunnel visible through the opening (rock walls/roof/back behind the frame, not open sky). - MET: hero and front cells show a dark grey recess behind the frame.
4. [must] Pair of iron rails on timber sleepers runs out of the tunnel across a sandy patch toward the viewer (-Y). - MET: rails on timber sleepers run from the tunnel out over the sand toward the camera.
5. [must] Two amber lanterns hang on the front of the posts (emissive glass reads glowing orange), plus one smaller lantern visible deeper inside the tunnel. - MET: two large amber glass lanterns on the post fronts and a smaller inner one glowing in the tunnel (front cell).
6. [must] Red banner with a small pale diamond hangs from the lintel at the right post. - MET: red pointed banner with pale diamond on the right post just under the lintel.
7. [should] Iron corner brackets with bolt heads visible on post/lintel joints and brace ends (dark blue-grey). - MET (R3): enlarged about 1.5x; see goal 26.
8. [should] 5+ bright green leaf tufts at rock bases, and 1-2 clumps up on the upper-right rock. - MET: 8 ground tufts at rock bases plus clumps on the upper-right and left rocks.
9. [must] Opening clear >= 8 wide x 9 tall studs (posts' inner faces >= 9 apart; lintel underside >= 11 above the floor). - MET: posts 9.2 apart inside, lintel underside 12.6; brace lower edges stay above ~9 at x=+-4 (geometry check plus front cell shows a tall clear doorway).

## FRONT
10. [must] Front view: frame reads as a rectangle ~1.1x wider than tall inside a grey rock outline that is wider than the frame and rises above it; rails converge into the dark tunnel centre. - MET: front cell frame ~15.5 x 15.3 inside a wider grey outline that rises above it; rails lead into the dark centre.
11. [should] Front view shows about 8-12 large rock facets per big rock, no noisy small ones. - MET: big boulders show ~8-12 broad facets each.

## SIDE
12. [should] Side view shows post + brace timber structure in front of grey rock mass that is taller than the frame. - MET (R3): the side cell shows the post, the X side braces and the lantern at the front, with the rocks behind.

## TOP
13. [should] Top view: grey rock crown covers the back half; lintel and rails visible at the front, sand patch in front. - MET: top cell shows grey crown over the back, lintel and rails at the front, sand in front.

## PARTS
14. [must] 4 separate parts: LintelBeam (~12 x 1.2 x 1.2 with iron end plates + bolts), UprightPost (~1.4 x 1.4 x 10 on a ~2.2 wide grey footing), Collar (~1.6 block with iron strap), DiagonalBrace (~5.5 long angled beam with chunky end blocks/iron plate). - MET: parts cell shows the post on footing, lintel with iron end plates, collar block with strap and the angled brace with end blocks.

## VARIATIONS
15. [must] MineSupportNarrow: ~10 wide portal, one lantern each side, banner on the LEFT post, opening >= 5 wide x 8 tall, rocks around it. - MET: narrow portal with two lanterns and the banner on the left post, rocks on both sides and above.
16. [must] MineSupportWide: ~22 wide, double (stacked) lintel, thicker posts, 3 lanterns, rock mass behind, no banner. - MET: wide cell shows thick posts, stacked double lintel, 3 lanterns, rock mass behind, no banner.
17. [must] MineSupportDamaged: one post leaning, lintel cracked and slanted, two braces fallen on the ground, rubble in the opening partly blocking it, torn banner, extra foliage. - MET: right post leans, lintel is broken into a slanted two-piece, two braces lie on the sand, rubble pile fills half the opening, short torn banner, 10 tufts.

## PALETTE (one base colour per material)
18. [must] Timber w15_timber #A9662B warm orange-brown on all wood; render reads warm mid-brown like the reference, not grey. - MET: wood renders warm orange-brown like the reference.
19. [must] Rock w15_rock #8E8E96 neutral grey on cliff, footings, rubble. - MET: rocks, footings and rubble render neutral grey.
20. [must] Iron w15_iron #454B66 dark blue-grey on rails, brackets, bolts, lantern frames. - MET: rails, plates and lantern frames render dark blue-grey.
21. [must] Sand w15_sand #D4B98E pale tan ground patch; foliage w15_foliage #3E9A22 vivid green; banner w15_banner #C8161F red; glass w15_lantern_glow #FFB347 emissive. - MET: tan sand, vivid green tufts, red banner, glowing amber glass all read as in the reference.

## SCALE
22. [must] Hero frame ~16 wide x ~14 tall studs; a 5.5-stud character fits through the doorway with room to spare; rails ~2.4 gauge. - MET: frame 15.5 wide x 15.3 tall (caps included), doorway 9.2 x 12.6, gauge 2.4.

## Iteration log
- Build 1: rocks floated (rock() takes the base z, I passed the centre) and read as spiky subdiv-1 diamonds; lanterns tiny; posts thin.
- Build 2: rocks sit on the ground with subdiv 2; added tunnel side walls and lintel end caps; posts 1.8; bigger lanterns and tufts. Fixed Tint >1.25x problem (tint_var 0.05).
- Build 3: pushed side rocks behind the frame so the timber reads in front; longer/thicker braces; lintel raised to 12.6 so the 8x9 clear opening survives; lanterns s=2.0.
- Build 4: Damaged variant got a bigger rubble pile in the opening and thicker fallen braces. All must goals MET; remaining gap: the reference frame is a bit more dominant vs the rocks and its braces are longer.

## REVISION (verifier fail, resemblance 5.5) - added must/should goals
23. [must] Hero: portal triangle clearly visible in iso and front: two heavy posts, lintel, collars and TWO diagonal braces per side (a long chunky front brace ~5.5+ long, 1.2 section, per upper corner, plus a second braced frame set behind it), long and dominant like the reference. - MET: front cell shows a long chunky brace in each upper corner running from mid-post to the lintel (~5.9 long) forming the portal triangle, the braced inner frame set shows through the opening, and the side cell shows an X brace on the post side.
24. [must] Timber frame dominates: posts ~2 studs, lintel ~1.8; frame occupies most of the front view; rocks frame it from behind/beside, not covering it; side view shows the post and braces in front of the rocks. - MET: posts 2.0 and lintel 1.8 thick; the frame fills most of the front and iso cells, with the rocks behind and beside it; the side cell shows the post and braces in front of the rocks.
25. [must] Rock massif uses 5-7 large faceted rocks (plus only small rubble), ~1.3x frame height at the back. - MET: 7 big rocks (2 flanks, roof slab, 2 roof rocks, crown, back wall) plus 4 small rubble stones; the crown reaches ~20.9 against a ~16.2 frame (1.3x).
26. [should] Iron corner brackets and bolt heads ~1.5x larger, readable as plates with bolts at every joint. - MET: brackets are now 1.4-1.9 wide plates with 0.36 bolt heads, reading as dark plates with bolts at the lintel ends, post joints and brace feet.
27. [should] Footprint tighter: hero ~22 wide or less, sand patch no wider than the rocks. - UNMET (partial): sand is tighter (19 wide), but the rock flanks keep the hero at 24.5 x 25.6; the frame itself is 16 wide. The flanks are needed to frame the portal.
28. [should] Lanterns ~1.3x larger, bright amber glass. - MET: post lanterns at s=2.5 (glass ~1.55) read as large amber boxes; the glass key is fixed by the sheet palette, and the heat_glow light adds warmth in-game.
29. [should] Narrow variant banner on the RIGHT post (reference image overrides spec text). - MET: the narrow cell shows the red diamond banner on the right post, with lanterns low on both posts.
30. [should] Wide variant: visible double lintel plus braces each side, thick posts, rocks behind ~1.3x frame height. - MET: the wide cell shows thick posts, a stacked double lintel, long braces in both corners, 3 lanterns and the rock mass behind, rising above the frame.
31. [should] Parts: lintel with iron end plates + 2 bolts each; brace with notched end blocks and iron plate. - MET (by geometry; the parts cell overlaps items): the lintel has iron end plates with 2 bolts; the brace has stepped notched end blocks with plates and a centre strap.
- R1 (revision): posts 2.0, lintel 1.8, front braces 1.25 thick with a second braced inner frame; brackets 1.5x; lanterns s=2.5; 6 rocks plus rubble; sand rx 9.5; narrow banner moved to the right post; wide frame braced, with taller rocks behind; brace part notched. Braces were still short.
- R2: lintel raised to 13.5; braces drop 5 / reach 4, ~5.9 long and now dominant in the front view; added a roof slab rock to shade the tunnel. Side flank rocks read as tall spikes.
- R3: flank and back rocks made deeper and lower; inner frame pulled forward to depth 3.8 so it shows through the doorway; added an X cross brace on the side. The side view now matches the reference layout (frame at the front, rocks behind). Doorway clear: 10 wide at 9.1+ under the braces, lintel underside 13.5.
