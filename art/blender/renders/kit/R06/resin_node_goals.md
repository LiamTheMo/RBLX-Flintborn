# R06 ResinNode goals

Revision after verifier fail (5/10). Status after revision build 4 (the cap). Verifier goals are added as musts (V1-V8).

## ASSEMBLED / HERO
1. [must] The main r06_softbark trunk rises diagonally to the upper right, is ~7-8 studs tall and ~3 thick at the base, and has chunky faceted sides. MET: the hero cell shows a thick, 7-sided jittered trunk leaning up-right, nearly as thick as the reference's log.
2. [must] (V1) The trunk tip is a pale r06_cutwood cut face that is clearly visible from the iso camera. MET: a tilted tan disc reads at the trunk top in the hero cell, with leaves behind it to the right.
3. [must] A second thick limb lies forward-right along the ground (~6 long) and ends in a pale cut tip at the lower right. MET: a thick limb runs to a pale cut tip at the cell's lower right.
4. [must] (V2) A broad, low, faceted r06_dirt mound spans the base, with its rim visible round the trunk, limb and big gem. UNMET (partial): a chunky dark mound is now visible under the big gem (front-left) and under the limb, but the right and back rim are hidden and it reads smaller than the reference's mound.
5. [must] A big faceted orange resin lump (~4-5 dia) sits on the trunk's front-left at mid height and is the largest focal mass. MET: a big orange gem on the trunk's front-left is the focal mass.
6. [must] A smaller resin lump (~2.5-3 dia) sits on the trunk's upper right below the tip. MET: a smaller orange gem sits on the upper right of the trunk.
7. [should] (V3) Exactly 3 leaf clumps of broad pointed leaves in star rosettes: top-right behind the tip, base front-centre, right mid. MET: three broad-leaf star rosettes sit in those three positions. The leaves are wider than in the last revision but still a little sparser than the reference's.
8. [should] (V4) The hero is a chunky mass, ~1.4x wider than tall. UNMET: the hero cell reads only slightly wider than tall (11.7 x 8.8 studs in bbox). It is chunkier than before but more compact than the reference.
9. [should] (V8) Chiselled low-poly: large flat facets on the trunk and mound, with no fine regular cylinders. MET: the trunk and limb use 7 sides with strong jitter, and the mound is made of large facets.

## FRONT
10. [must] (V5) The FRONT cell shows a near-vertical tapered trunk with a visible cut top, the big gem low-centre over the lower front, the small gem mid-right and the mound at the base. UNMET (partial): the gems and the mound at the base now match, and the pale top is visible. The trunk still leans ~30 deg right, against the reference's slight lean. The hero needs a strong rightward lean on screen, and that conflicts with a near-vertical front view: with a +Y lean the hero turns vertical too.

## SIDE
11. [should] (V6) The SIDE cell shows the trunk leaning strongly to one side over a wide dirt base, with both gems visible. MET (mostly): the side cell shows the trunk leaning strongly right over a wide mound base with both gems. The limb's cut end still shows at the lower left.

## TOP
12. [should] Top view: the trunk and limb form a V with pale cut ends, and the gems and rosettes sit round the edges. MET: the top cell shows the V, with the pale tip, gems and rosettes round the edges.

## PARTS
13. [must] ResinNodeWoodyBase: a tall tapered broken trunk ~7 tall with a flared base and a visible pale cut top, r06_softbark. MET: 7.4 tall, with a flared jittered base and a pale tilted cut top visible in the parts cell.
14. [must] ResinNodeResinLump: a single faceted gem lump ~3 across, r06_resin. MET: a faceted orange gem, ~2.8 across.
15. [must] ResinNodeLeafClump: 5-7 pointed leaves on a short stem, ~3 wide, r06_leaf. MET: a green broad-leaf rosette on a stem, ~3.1 wide.

## DROPS / DEPLETED
16. [must] ResinNodeRawResin: one faceted orange nugget ~1.3-1.5 studs, closed, <=300 tris. MET: a faceted orange nugget ~1.3 studs, 20 tris, 0 problems.
17. [should] ResinNodeRawResinSmall: a ~1 stud nugget with different facets. MET: a ~0.9 stud nugget.
18. [must] ResinNodeBareBranch: a bare lying branch ~7 long with one forked twig, pale cut ends, no resin and no leaves; slightly curved with a thicker raised end. MET: the branch is 7.7 long, its thick end is raised at the left with a big pale cut face, it has one forked twig, and there is no resin or leaves. The curve is gentle.

## PALETTE / SCALE / VFX
19. [must] Resin is the most saturated element (#F29A1A), bark is mid-brown #8A5B3E, pale #E0B27C appears only on cut ends, the leaves are #3F9A2C green and the mound is r06_dirt #6A5047. MET: the render shows these colours in these places.
20. [must] The hero is within 4500 tris, with 0 problems, nothing below z=0 and the origin at the bottom centre. MET: 576/4500 tris, 0 problems.
21. [must] (V7) VFX: an ore_glint with an orange PointLight on both lumps, harvest_hit on the big lump's front face with resin chips, harvest_deplete at the base and orange motes. MET: the small lump's glint now carries light=GLOW_SMALL (#FF9A1A); the other sockets are unchanged.

## Iteration log
- Prior run, builds 1-4: thin trunk, hidden mound, 4 narrow-leaf clumps, and no light on the small glint.
- Revision build 1: trunk at 7 sides with r 1.6 to 1.0, a tilted cut disc, lean partly toward +Y, a 4-lobe mound, 3 broad-leaf rosettes, subdiv-1 gems, small-glint light, and a 3-segment bare branch. The mound was still hidden and the trunk read near-vertical in the hero.
- Revision build 2: trunk r 1.85 to 1.15, more X lean, a longer limb and bigger gems. The trunk is now chunky, but the mound was still hidden behind the gem and flare.
- Revision build 3: mound raised to 3.3 with a front-left lobe pushed out, the big gem moved up and back, and higher gem jitter. The mound is now visible in the front and hero cells.
- Revision build 4: cut disc tilted further toward the camera, the limb lengthened, the big gem moved further left, the top leaf moved behind the tip and the branch's thick end raised. The pale top is clearly visible and the hero is a little wider.
- Still open: the front view lean (it conflicts with the hero's strong screen lean) and the mound's rim on the right and back.
