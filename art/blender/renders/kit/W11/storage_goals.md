# W11 Storage — goals

Reference: art/reference/kit/rows/W11_row2.png. Status after each build is marked [MET]/[UNMET].
Note: the reference row shows no ground dressing (no rubble, grass or flowers) around any storage
asset, so none is added.

## ASSEMBLED / HERO
1. (must) Crate at left, barrel at right, side by side and both fully visible in iso; barrel ~75% of crate width. — [MET] revision: barrel moved 0.55 forward/right, whole barrel incl. both hoops visible beside the crate
2. (must) Crate is a cube ~4.5 studs; overall hero ~8.5-9 x 4.5 x 4.8 studs (about 1.9x wider than tall). — [MET] KITSTAT 8.9 x 4.6 x 4.8; strip reads ~1.9x wider than tall like reference
3. (must) Every visible crate side face shows a thick X brace of two diagonal planks running corner to corner of the inner opening. — [MET] X of two diagonal planks visible on both visible crate faces in iso, front and rear cells
4. (must) Four corner posts stand proud of the faces (visible step at each vertical corner) and top/bottom frame boards border each face. — [MET] revision: posts now 0.18 proud of the chunky frame boards; clear step and shadow line at every vertical corner in hero iso
5. (must) Barrel has a visible bulge: belly clearly wider (~3.4) than its ends (~2.6), with 12 vertical stave facets. — [MET] front cell: barrel clearly bulged at belly vs ends; convex staves read as 12 boards
6. (must) Two dark iron hoops, one near the top, one near the bottom, standing slightly proud of the staves. — [MET] two dark iron bands near top and bottom, standing slightly out from staves
7. (should) Barrel top is an open rim with a wooden lid inset below the rim edge, visible in the iso view. — [MET] iso shows open rim with planked lid sunk inside
8. (should) Dark iron round nail heads at the brace ends and at the crate corners (about 4 per face plus corners). — [MET] revision: 0.32-wide 8-sided heads, 4 per post face + 1 at each brace end; read as big dark rivets in iso like the reference
9. (should) Crate top is a slatted panel of 4 planks inside a raised border. — [MET] top cell shows 4 planks inside a raised border frame

## FRONT
10. (must) Front view: square X-braced crate face at left and a barrel at right with two dark bands; barrel top at about the crate top height. — [MET] front cell matches: square X crate left, two-band barrel right, tops level

## SIDE
11. (should) Side view still reads as a braced crate plus barrel (X brace visible on the side face). — [MET] rear cell (SIDE_AZIMUTH 180) shows X-braced crate and barrel side by side (mirrored left/right vs reference)

## TOP
12. (must) Top view: square slatted crate top at left and a round barrel top with a dark hoop ring outline and a planked lid at right. — [MET] top cell: square slatted crate top + round planked barrel lid with dark hoop outline

## PARTS
13. (must) All 8 parts exist as separate assets AND each is visible in the parts cell. — [MET] parts cell: tapered curved stave (back-left), side panel, post, top panel, flat X brace, thick dark hoop, lid and base discs all visible
14. (must) MetalHoop is a dark iron ring ~3.4 across; LidTop and BasePanel are planked wooden discs (~2.6/2.7) with visible plank seams. — [MET] hoop is a dark ring ~3.4; lid/base are planked discs with visible seams
15. (should) WoodenStave is a curved, bulged single stave, tall and narrow (~4.8 x 1.1); XBrace is two crossed diagonal planks; SidePanel is an X-braced board. — [MET] stave now spindle-tapered and turned to camera, reads as a barrel stave; X brace two crossed planks; side panel X-braced

## VARIATIONS
16. (must) SquareCrate: smaller (~3.5) cube crate with X braces on its sides, corner posts and nails. — [MET] square crate: X on sides, corner posts, nails
17. (must) LongChest: long low box (~6 x 3 x 3, 2x longer than tall) of horizontal planks, slightly arched lid, 3 dark iron straps wrapping over the lid and down the front. — [MET] long chest: horizontal planks, slight arch lid, 3 dark straps over lid and down front
18. (must) OpenCrate: open-top crate, corner posts and 3 horizontal slats per face with see-through gaps, thick bottom visible inside. — [MET] open crate: 3 slats per face with see-through gaps, open top, thick floor visible

## PALETTE / SCALE
19. (must) Wood is ONE warm orange-brown (w11_wood #B5702C) on all planks, posts, staves; render reads as warm orange like the reference, not grey or pale. — [MET] all wood one warm orange key; render is somewhat brighter/more orange than reference but same hue
20. (must) Iron (w11_iron #40444F, dark blue-grey) only on hoops, straps and nail heads. — [MET] iron only on hoops, straps, nail heads
21. (should) All assets under budget (hero 4500, parts 1500, variants 3000), 0 problems. — [MET] hero 2248/4500, variants <=1536/3000, parts <=316/1500, 0 problems

## Iteration log
- Build 1: all assets built, 0 problems. Side view had the barrel hiding the crate; X brace part stood in front of the stave in the parts grid; X braces and stave seams faint.
- Build 2: SIDE_AZIMUTH=180 (crate and barrel side by side); X brace part laid flat so the stave shows; panels recessed deeper. Stave now visible, rear cell readable.
- Build 3: braces stand further proud; barrel staves made convex (mid line pushed out) so each stave reads. All must goals MET.

## Verifier revision goals (added as must)
22. (must) HERO: corner posts clearly proud of faces with chunky frame boards and big iron corner studs. — [MET] hero cell: posts step 0.18 out from frame boards, frame boards 0.55 tall, large dark studs at every post end
23. (must) HERO: X brace is thick (~0.6 wide) and clearly proud of the panel planks, reading as a raised X. — [MET] bevelled brace planks 0.6 wide, 0.25-0.3 proud; the X shows edge highlights/shadow lines in iso, front, side and square-crate cells
24. (must) PARTS: all 8 named parts present and visible in the exploded cell (stave and hoop clearly readable). — [MET] all 8 visible (see 13); hoop widened to 0.22 radial so it reads as a dark band
25. (must, partly impossible) PARTS: laid out like the reference (vertical barrel stack lid/hoop/staves/hoop/base, propped panels). — [UNMET-IMPOSSIBLE] the runner's grid_parts() repositions every part asset onto the ground in a packed grid (sorted by height) and only one MetalHoop asset is specified, so a module cannot stack parts vertically or show two hoops; X brace laid flat so it does not hide the stave
26. (should) DETAIL: nail/rivet heads ~4+ per face, dark and chunky, also on variants. — [MET] square crate, open crate and long chest straps all show large dark heads
27. (should) LongChest lid visibly arched. — [MET] crown raised 0.3; arch visible in the variant cell with straps following it
28. (should) Wood mid-tone ~#B8743A. — [MET by palette rule] sheet palette w11_wood #B5702C is fixed and shared by all W11 modules (copied verbatim); render hue matches, slightly more saturated than reference

- Revision build 1: deeper face layering (posts 0.18 proud), bw 0.6, nails 0.32 wide 8-sided, barrel forward/right, chest arch +0.3, tapered stave. Nails and posts now read; X still flat.
- Revision build 2: brace planks rebuilt as bevelled boxes -> X reads raised with edge lines.
- Revision build 3: hoops prouder, hoop part wider; stave rotated (wrong way, edge-on).
- Revision build 4: stave rotated +0.45 rad, its curved face now visible. All buildable musts MET.
