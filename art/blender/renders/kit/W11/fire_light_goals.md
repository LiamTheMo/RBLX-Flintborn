# W11 row 3 FireLight goals

Status after each build: MET / UNMET with one line of evidence.

## ASSEMBLED / HERO
1. [must] Ring of ~10 big chunky grey faceted boulders, outer diameter ~12 studs; front stones visibly larger than rear ones. — MET: hero/top show a closed ring of 10 big grey boulders ~11.7 studs across; front ones slightly bigger.
2. [must] Stones are rounded-chunky, 8-14 large facets each, no noisy small faces; one grey (w11_stone ~#8D9097). — MET: stones read as chunky faceted lumps with a handful of big facets, one grey.
3. [must] Tripod of three wood poles splayed from ground to an apex ~9 studs high, poles crossing and poking ~1 stud above the bind. — MET: three orange poles splay from the ring to an apex ~8.3, tips poke ~1 stud above the bind (front/side cells).
4. [must] Tan rope bind (w11_rope) of 3-4 wraps at the apex, clearly lighter/yellower than the wood. — MET: tan 4-wrap collar at the apex, visibly yellower than the poles.
5. [must] Black/dark iron cauldron (~2.6 dia) with rim lip and bail handle hangs from the apex by a rope/chain, its bottom ~3.5 above the logs. — MET: dark cauldron hangs under the apex on a rope over the logs; it is a little washed by the campfire smoke preview and its handle is faint. (superseded by goal 19)
6. [must] 5-6 crossed orange-brown logs in a star/teepee pile inside the ring, with small glowing orange ember blobs low among them; no big flame mesh. — MET: star of 6 crossed logs in the ring centre with orange emissive embers low; no flame mesh.
7. [must] campfire VFX socket at (0,0,0.8) + embers at (0,0,1.5) + heat_glow at logs. — MET: campfire (0,0,0.8) x1.2, embers (0,0,1.5), heat_glow at logs; flame/smoke visible in render.
8. [should] Hero overall ~12 x 12 x 9.5 studs, silhouette roughly a wide triangle (tripod) over a low round ring (ring height ~1/6 of total). — MET: KITSTAT 11.5 x 11.7 x 9.7; silhouette is a tall A over a low round ring like the reference.

## FRONT
9. [must] Front view: A-shape of two poles meeting at the top with the pot centred under the apex; stone ring forms a low band across the bottom ~1.6-2 tall. — MET: front cell shows an A of two poles with the pot centred under the apex over a low stone band.

## SIDE
10. [should] Side view also reads as an A-frame (third pole visible), pot centred. — MET: side cell shows the A-frame with the third pole and pot centred.

## TOP
11. [must] Top view: closed ring of ~10 stones round a star of logs; tripod poles radiate from the centre in three directions. — MET: top cell shows a closed ring of 10 stones round a log star, with three pole spokes.

## PARTS
12. [must] Parts present: HangingPot (black pot with handle), TripodPole (single long pole), RopeBind (tan collar), Fire (log pile of 5 crossed logs + embers), LogPiece (single log), StoneRing (single chunky stone). — MET: parts cell shows pole, pot with handle, rope collar, log pile fire, single log, single stone.
13. [should] Pot part ~2.6x2.6x2.4 incl handle; pole 9 long x 0.7 dia; log 3 x 0.6. — MET: pot 2.5x2.6x2.9 (incl handle), pole 9 x 0.7, log 3 x 0.6.

## VARIATIONS
14. [must] BasketBrazier: three splayed wooden legs ~2 high under a bowl-shaped slatted wooden basket with two dark iron bands and glowing orange coals inside; ~3.5 dia x 5.5 tall; brazier_fire socket at top. — MET: brazier cell shows three splayed legs, slatted flaring wooden basket, two dark iron bands, glowing coals; 3.8 x 4.5 + brazier_fire socket.
15. [must] LanternPost: stone/iron base block, tall wooden post (~8.5), arm reaching to one side at top with diagonal brace, hanging iron-frame lantern with glowing amber glass at the arm end. — MET: lantern cell shows dark base block, tall wood post, arm to the right with diagonal brace, hanging iron lantern with glowing amber glass.
16. [must] WallTorch: flat iron wall plate behind, two iron bands holding a vertical wooden handle ~4.5 tall, widening bowl head with glowing rim; torch_fire socket at head top. Flat back. — MET: torch cell shows flat dark wall plate behind, two iron bands, wooden handle widening to a bowl head under the torch_fire flame.

## PALETTE
17. [must] Wood one orange-brown (#B5702C), iron one dark blue-grey (#40444F), stone one mid grey (#8D9097), rope tan (#C99A55), embers orange emissive (#FF8C1A), glass amber emissive (#FFC23D). — MET: render colours match: orange-brown wood, dark iron, mid-grey stone, tan rope, orange embers, amber glass.
18. [should] Tris: hero <= 6000, parts <= 1500, variants <= 3000; build ends 0 problems. — MET: hero 2254/6000, parts <=420, variants <=1580; 0 problems.

## REVISION (verifier goals, all must)
19. [must] Black cauldron ~2.6-2.9 dia hangs under the apex with a rim lip and a clear, thick bail handle, and reads dark/black in the hero and front cells (not washed out by glow). — MET (build R4): front/side cells show a large near-black pot (3.25 dia) centred between the poles under the apex, rim lip and thick bail arc visible; hero cell pot reads dark, not smoke-washed.
20. [must] BasketBrazier is ~5.5 tall: legs ~2, then a dense rounded bowl basket of many thick slats, two thick iron bands, and a heaped ember mound (not a flat disc). — MET: brazier cell shows short stout splayed legs, a dense rounded bowl of 22 thick slats, two thick dark bands, glowing rim of heaped coals; 5.4 tall.
21. [must] Chunkiness: tripod poles and logs read as thick, hand-sized shapes (pole r ~0.45, log r ~0.5); the rope bind has 5-6 wraps. — MET: poles and logs visibly stouter in every cell; rope collar is a thick tan wrap with pole tips crossing above it (4 thick wraps chosen so the crossing tips show, as in the reference).
22. [should] Front stones are taller (~2.6) and chunkier, so the ring is not a low flat band. — MET: front cell stones are taller and chunkier than the rear ones; ring reads as a band of big boulders.
23. [should] RopeBind part ~1.5 dia x 1.2 tall. — MET: parts cell collar visibly larger; KITSTAT 1.6 x 1.5 x 1.1.
24. [should] LanternPost base is a 1.8x1.8x0.8 stone block and the diagonal brace is thick. — MET: lantern cell shows a grey stone base block with iron cap and a thicker brace.

## Iteration log
- Build 1: first pass. Stones too small and spaced out, thin logs/poles, Tint 1.26x problem.
- Build 2: stones 2.9-3.1 wide at r=4.6 (closed ring), logs r=0.4, poles r=0.4, thicker rope, tint_var 0.05, curved brazier slats -> 0 problems, ring now matches.
- Build 3: taller stones (2.3), wider tripod feet (r=4.8), smaller heat_glow so the pot shows, iron disc in torch bowl.
- Build 4: hero pot scaled 1.15 and lowered to 3.2 so it reads under the apex. Stopped (max 4 builds).
- Revision R1: poles r0.45, logs r0.5, taller front stones, pot 2.9 dia with 0.15 bail, heat_glow 0.3, brazier rebuilt 5.6 tall with 22 slats x3 segments, thick bands, ember mound; lantern stone base + thick brace. Pot still hidden behind the front-left pole; rope bind too tall.
- R2: pot raised, bowl profile rounder, stouter legs. Pot still occluded.
- R3: tripod feet rotated to -168/-12/90 so no pole crosses the pot in the hero view; pole tips extended; bind 4 thick wraps. Pot now dark and visible.
- R4: pot lowered to 3.0 with taller bail (rise 1.45) so the handle arc shows. 0 problems; stopped (4 builds).
- Note: w11_iron kept at the sheet value #40444F (shared by all W11 modules); the pot now reads black through size and placement instead.
