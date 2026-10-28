# W15 row 3 Minecart - goals

Axes: cart length runs along Y (rails along Y), front = -Y (coupling block), rear = +Y (U-handle).
Hero/variants: long side dominant, end to the right (HERO_AZIMUTH -62, which also puts the lit long side to camera).

## Palette (one base colour per material)
- G1 must: all wood is one key w15_timber #A9662B (orange-brown); renders orange-brown like ref, not grey or dark chocolate.
- G2 must: all iron (bands, plates, bolts, wheels, axles, handle) is one key w15_iron #454B66, renders dark blue-grey.
- G3 must: wheel hub caps are timber (brown) in the centre of the dark iron wheel.
- G4 should: ore chunks only in Loaded cart, w15_ore #33468A dark blue; sand patch w15_sand and grey w15_rock only in Broken cart.

## ASSEMBLED / HERO
- G5 must: open-top box ~6 long x ~4.5 wide (incl. wheels) x ~4 tall studs; body visibly wider at the rim than at the floor (tapered sides).
- G6 must: each long side shows 3 clear horizontal planks with visible seams; each end shows 3 planks.
- G7 must: iron corner plates with bolt heads at all 4 top corners, iron straps running down the corner posts.
- G8 must: 4 chunky dark 10-sided wheels, diameter ~2.2, mounted OUTSIDE the body near front and rear, lower edge on z=0, body bottom roughly at wheel centre height.
- G9 must: iron U-handle rising above the rim at the rear end (~2.5 wide).
- G10 should: small coupling/bumper block at the front bottom centre.
- G11 should: interior is empty and open, floor boards visible.

## FRONT
- G12 must: front view shows the narrow end: trapezoid body wider at top, 3 planks, wheels flanking both sides below the body, coupling block bottom centre.

## SIDE
- G13 must: side view shows long body ~2x as long as tall (body only), two wheels near the ends, handle silhouette at the rear top.

## TOP
- G14 must: top view: rectangle ~1.35x longer than wide, floor planks visible inside, handle bar across one end, wheels peeking out at the 4 corners.

## PARTS
- G15 must: 7 parts: SidePanel (3 planks + iron end straps), EndPanel (3 planks), Handle (U bar), BasePlank (4 planks + 2 runners), Wheel (10-sided disc with timber hub), Axle (rod with end collars), MetalBand (bolted iron plate).
- G16 should: wheel part stands upright showing its face; axle is a thin long rod.

## VARIATIONS
- G17 must: Empty Cart reads as the same cart as hero.
- G18 must: Loaded Cart: 7-9 faceted dark blue ore chunks heaped clearly above the rim.
- G19 must: Broken Cart: tilted, one wheel missing from the cart and lying detached on the ground, side panel cracked/missing planks, 2 fallen planks, sand patch and 2 grey rocks.
- G21 must (verifier): hero long side shows 3 clearly separate boards with dark/light seam lines, not one flat face.
- G22 must (verifier fix): horizontal iron band across the middle of each long side, with 2 bolt heads.
- G23 must (verifier fix): thick timber axle beams under the body, full width between the wheels, at wheel-centre height; sills under the sides.
- G24 should (verifier): top view: wheels peek out at the 4 corners; cart ~1.35x longer than wide; handle across the end.
- G25 should (verifier): hero framed with the long plank side dominant and the iron corner plates at the near end.
- G26 should (verifier): Broken sand patch ~9 studs, irregular, extending around and behind the cart.
- G27 should (verifier): Wheel part ~2.2 dia x ~0.7 thick; ore chunks vary in size.
- G20 should: all under budget (hero 3500, variants 4000, parts 1500), nothing below z=0, 0 problems.

## Status (after revision build 4)
- G1 MET: boards render the same orange-brown as the ref in every cell.
- G2 MET: wheels, plates, straps, bands, handle, axle all one dark blue-grey like the ref iron.
- G3 MET: brown hub caps clear on every wheel in hero, side and variants.
- G4 MET: ore only in Loaded, sand and grey rocks only in Broken.
- G5 MET: 5.3 x 6.8 x 4.4 studs (incl. wheels/handle); front cell is a clear trapezoid wider at the rim.
- G6 MET: hero and variants show 3 boards per long side with bevelled seam lines; ends show 3 planks in the front cell. Side cell (shade side) is fainter but planks still read above/below the band.
- G7 MET: L-shaped bolted iron plates with caps at all 4 top corners, straps down the posts.
- G8 MET: 4 dark 10-sided wheels outside the body near both ends, on the ground, dia 2.2.
- G9 MET: U-handle rises above the rear rim (hero top-left, side and top cells).
- G10 MET: coupling block with iron plate at front bottom centre (front cell).
- G11 MET: open interior with floor planks visible (hero, top).
- G12 MET: front cell: trapezoid end, 3 planks, wheels flanking, coupling bottom centre, axle beam visible.
- G13 MET: side cell: long body, 2 wheels near the ends, handle at the rear top, sill line under the body.
- G14 MET: top cell: rectangle with floor planks, handle across one end, wheel edges now poke out at all 4 corners.
- G15 MET (content) : all 7 parts present; the auto layout still overlaps the side panel / handle slightly (layout is automatic).
- G16 MET: wheel upright showing its face; axle a thin rod with collars.
- G17 MET: Empty cart = hero cart with front bumper bar.
- G18 MET: 9 faceted dark blue chunks of varied size heaped above the rim.
- G19 MET: Broken tilted toward camera, front-left wheel gone and lying flat on sand, top side plank missing and middle cracked, 2 fallen planks, 2 grey rocks.
- G20 MET: hero 2648/3500, variants 2528-2840/4000, parts 84-304/1500, 0 problems.
- G21 MET: hero cell now shows three distinct boards on the lit long side, each edge a bevel line with a groove between (clapboard lean + 0.28 gap + 0.1 bevel + per-plank tint).
- G22 MET: dark iron band with bolts runs across the middle board of each long side (hero, side, variants).
- G23 MET: timber axle beams visible between the wheels in the front and hero cells; side sills under the body.
- G24 MET: top cell wheels peek out at the corners; reads ~1.3x longer than wide with the handle bar at the end.
- G25 MET: hero shows the long plank side dominant with the end and corner plates to the right, as in the ref (mirror of handle position is the only difference).
- G26 MET: irregular ~9 x 9 sand pool spreads under and around the Broken cart.
- G27 MET: wheel part 2.2 x 0.7 x 2.2 (KITSTAT); ore chunk radii 0.5-1.05.

## Iteration log
1-4 (first run). Proportions, seam gaps, corner plates, rocks; see earlier status.
R1. Revision: bevelled lean planks, wider seams, mid-side iron band, full-width axle beams, sills, bigger/thicker wheels pushed out, irregular 9-stud sand, varied ore. Seams still faint because the hero saw the shaded side; wheels too heavy.
R2. HERO_AZIMUTH -62 (lit long side to camera), gap 0.28, lean 0.16, bevel 0.1; wheel r 1.1 x 0.65. Seams now clearly visible in hero/variants.
R3. Broken: wrecked side and missing wheel moved to the camera-facing -X side so they show.
R4. Wheel part hub/disc gap fixed (thickness 1.2 -> 0.7).
Note: w15_ore kept at the sheet palette value #33468A (palette must be copied verbatim); the verifier suggested #3A4468.
