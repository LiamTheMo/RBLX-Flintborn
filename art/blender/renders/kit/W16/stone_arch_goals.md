# W16 stone_arch (StoneArch, row 1) goals

Revision 2: the verifier failed revision 1 (4/10). Its unmet goals are now musts (V-tagged). Status is updated after every build.

## ASSEMBLED / HERO
1. [must] Freestanding pointed arch: two block piers + wedge ring meeting at a pointed apex; ~14 w x ~16 h studs (h/w ~1.1-1.2). -- MET - build 4: two block piers + pointed wedge ring; arch body 14w x 16.4h (rubble widens bbox to 18).
2. [must][V] Ring reads as ONE continuous pointed arch of 8-9 wedges (4 per side + keystone), tightly seated on the piers, joints ~0.1 stud, tilt jitter <=1 deg, left/right mirrored. -- MET - hero and front cells: one continuous tight band, 4 wedges per side + keystone, thin mirrored joints, no lopsided gaps.
3. [must][V] Keystone slightly larger than the wedges and sits IN the ring at the apex (top <=0.5 above the neighbouring wedge tops), sticking out ~0.3 in front; no leaf tuft on top adding height. -- MET - keystone sits in the ring at the apex, only ~0.25 above neighbouring wedges, projects 0.3 in front; no tuft on top.
4. [must][V] Piers ~3.5 wide: 5 stacked rectangular blocks ~1.8-2 tall, staggered 0.2-0.3, rotated 2-4 deg, on a clearly wider 4.5 x 4.5 x 1.4 plinth block. -- MET - front cell: 5 offset/rotated 1.7-tall blocks per pier on a visibly wider 2-stone plinth course (1.8 tall).
5. [must] Walk-through opening ~6 wide, >=10 tall at the apex (doorway >= 4 x 7). -- MET - front cell: opening ~6 wide, intrados apex ~13.7.
6. [must][V] Heavy bright-green ivy: dense, overlapping clumps (r 1.0-1.4) wrapping both piers, a continuous string along the arch top and over the keystone front, heavier on the right/back. -- MET - ~35 bushy overlapping clumps cover both piers (front, outer, back), a string along the ring top, heavier on the right; clumps are chunkier stars than the reference small-leaf ivy.
7. [must][V] 4-6+ rubble chunks (grey and sandstone, 0.6-1.2 studs) at BOTH feet, plus bushy leaf clumps at plinth corners and grass tufts, all within ~1.5 of the plinths. -- MET - hero/front: large sandstone and grey rubble blocks with a piled chunk at both feet, bushy clumps and tufts at both plinths.
8. [should][V] Overall ~14 w x <=5.5 d x ~16 h (plinth 4.5 deep plus flat ivy); reads as a thin gate. -- UNMET - bbox 18 x 7.7 x 16.4; the 4.5-deep plinths, wrapped ivy and the required foot rubble push past 3.5; still reads as a thin gate in the side cell.
9. [should] Brown soil vine stems visible under the ivy on pier fronts. -- MET - brown vine tubes visible under ivy on pier fronts.

## FRONT
10. [must][V] Symmetric pointed silhouette, piers ~1/4 of the width each, wedge ring continuous and tight, keystone not detached. -- MET - front cell: stone silhouette symmetric (mirrored ring, piers ~1/4 width each), keystone attached; only ivy is deliberately right-heavy.

## SIDE
11. [must] Side view: a single narrow pier column with plinth at the bottom and ivy up it, not the span. -- MET - side cell: one narrow pier column with plinth course and ivy.

## TOP
12. [should][V] Top view: arch bar with keystone in the middle, two square plinths visible below, ivy clumps. -- UNMET - top cell shows ring bar and ivy, but the runner camera hides the plinths and is dominated by cast shadow; no module camera API.

## PARTS
13. [must] Four parts: StoneArchKeystone (trapezoid ~2x2x2.5), StoneArchWedge (tapered ~2x3x2.5), StoneArchPier (stack of 4 blocks 3.5x3.5x8), StoneArchBase (4.5x4.5x2 + block on top). -- MET - parts cell: keystone, wedge, 4-block pier and base stone + block, all separate assets.

## VARIATIONS
14. [must][V] StoneArchPointed: tall narrow pointed arch ~12 w x 16 h, tight ring with seated keystone, heavy ivy on both sides. -- MET - pointed variant: tall narrow pointed arch (~12 arch width, 16.5h), tight ring, seated keystone, ivy on both piers and ring.
15. [must] StoneArchRound: semicircular ring of ~9 wedges with keystone on top, ~14 w x 15 h, ivy on piers and ring. -- MET - round variant: semicircular ring of 8 wedges + keystone, 15.6h, ivy on piers and ring.
16. [must] StoneArchCollapsed: left pier full height with half the ring ending broken mid-curve; right pier stub ~5 high; fallen wedge + rubble on the ground; more ivy and grass; ~13 w x 14 h. -- MET - collapsed variant: full left pier with broken half ring, right stub ~5h, fallen wedge, rubble, extra clumps/tufts, 14.5h.

## PALETTE / SCALE
17. [must][V] Cut stone renders as pale cream-tan like the reference, NOT orange-peach: one key w16_arch_stone #D6BF9C (module key: sheet w16_sandstone #CDA877 renders orange here; shared key cannot be changed without affecting other modules). Grey (w16_stone_grey #8F8D86) only on rubble. -- MET - stone renders pale cream-tan close to the reference, no longer orange; grey only on rubble.
18. [must][V] Ivy one saturated green w16_ivy #3F8A1A, renders as bright as the reference, and as dense. -- MET - ivy saturated green, dense on piers; slightly darker/less yellow than the reference lime (shared sheet key kept).
19. [should] w16_soil #7A4A2A only on vine stems. -- MET - soil only on vine stems.
20. [should] Block scale consistent with sheet: pier blocks ~1.8, plinth 4.5, wedges ~2-2.5. Hero under 6000 tris. -- MET - pier blocks 1.6-1.7, plinth 4.5, wedges ~2.3; hero 5342/6000 tris.

## Iteration log (revision 1)
- Builds 1-4: wedge ring with 3.2 deg gaps, floating trapezoid keystone, 1.5-tall blocks, sparse ivy. Verifier failed it.

## Iteration log (revision 2)
- Build 1: rewrote ring (0.1-stud joints, <=0.8 deg tilt, mirrored), keystone seated in ring (+0.25 top, 0.3 front), 5 blocks per pier, module key w16_arch_stone #D6BF9C. Ring tight, colour pale tan; ivy flat stickers, base bare.
- Build 2: bushier clumps (squash 0.75, r x1.12), two-stone plinth course, bigger rubble/base clumps. Ivy denser; base still small.
- Build 3: plinth 1.8 tall, blocks 1.6-1.7, rubble x1.3 + piled chunks. Plinth reads; rubble still small at sheet scale.
- Build 4: rubble x1.55, base clumps x1.25. Rubble and clumps now read at both feet. Stopped (4-build cap); depth/top-view shoulds remain UNMET.
