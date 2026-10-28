# V01 FieldSedge goals (row 2)

Status per goal: MET / UNMET, with one line of evidence (filled after each build).

## ASSEMBLED / HERO
1. [must] Open radial fan of 14-18 broad, flat lance blades radiating from one hub; reads as a sedge fan, not a grass tuft or a blob. — MET - hero reads as a fan of 18 broad lance blades from one hub.
2. [must] Hero is wider than its blade height: ~4.2 wide vs ~3.2 tall blades (width/blade-height ~1.3). — MET - hero visibly wider than blade mass is tall (4.3 x 4.6 footprint, blades ~3.2).
3. [must] Two brown pointed seed spikes on thin green stems rise above the blades to ~4.2 tall, leaning in opposite directions, slightly off-centre. — MET - two brown pointed heads on thin green stems above the blades, leaning apart.
4. [must] Inner blades stand near-upright; outer blades lean 50-70 deg and their tips droop toward the ground. — UNMET - inner blades upright, outer lean ~60 deg, but tip droop is weaker than the reference's curled tips.
5. [should] Blade lengths visibly vary (large / medium / small mixed around the fan). — MET - long, medium and short blades mixed round the fan.
6. [should] Each blade shows a central ridge (two facets across its width) and a pointed tip; widest in its lower third. — MET - two facets either side of a ridge, pointed tips, widest low.
7. [should] A small brown root base is just visible at the hub at ground level. — UNMET - root base only faintly visible at the hub (top view), hidden in iso.

## FRONT / SIDE
8. [must] Front view: V-shaped fan silhouette, narrow at the base, wide at the top; both spikes visible above the blades. — MET - narrow base widening into a V fan, both spikes above.
9. [should] Side view: similar fan, slightly narrower than the front; spikes visible. — MET - side view is a similar fan with both heads visible.

## TOP
10. [must] Top view: open star of blades radiating evenly in all directions from the centre, blade tips separated (gaps between blades), brown heads visible near the centre. — UNMET - top view is a radiating star with both brown heads, but broad blades overlap; tips not cleanly separated like the reference.

## PARTS
11. [must] SedgeBladeLarge: single long (~3.5) lance blade, straight-ish, widest at lower third, pointed tip, keeled. — MET - long straight lance, widest low, pointed, faceted ridge.
12. [should] SedgeBladeMedium (~2.6) slightly curved; SedgeBladeSmall (~1.8) more curved/angled. — MET - medium gently curved, small angled and curved.
13. [must] SedgeSeedSpike: brown faceted pointed ovoid head (~0.8) on thin green stem (~2.5). — MET - brown faceted pointed head on thin green stem.
14. [should] SedgeRootBase: brown tapered knot ~0.6 tall with ~6 splayed roots touching the ground. — MET - brown tapered knot with 6 splayed roots on the ground.

## VARIATIONS / DEPLETED
15. [must] A. SedgeShortFan: ~3 wide x 1.8 tall, ~12 shorter blades, no spikes. — MET - low, wider-than-tall fan of 12 short blades, no spikes (2.8 x 2.0).
16. [must] B. SedgeTallArchingFan: ~5 wide x 3.8 tall blades arching/drooping outward, 2 spikes to ~4.5. — MET - bigger fan arching outward with two spikes above (5.0 wide, 4.4 tall); droop moderate.
17. [must] C. SedgeCutTuft (depleted): low clump ~1.6 wide x 1.0 tall, ~14 short blades with blunt flat cut tops, no spikes. — MET - low clump of 14 blades with flat clipped tops, no spikes (1.6 x 1.0).

## PALETTE / SCALE
18. [must] Blades one key v01_sedge_blade #8DB82A (lime yellow-green, renders lime not dark green); stems v01_stem #4C9230; heads + roots v01_brown #8A5530. No shade variants. — MET - lime blades from single v01_sedge_blade key; v01_stem stems; v01_brown heads/roots. Shadow sides a bit more olive than reference.
19. [must] Build reports 0 problems; all assets collision none, under budget, nothing below z=0. — MET - 0 problems, collision none everywhere, max 1126/3000 tris.

## Iteration log
- Build 1: custom keeled lance blade + loft helpers. Fans too upright/narrow (3.6 wide), cut tuft too narrow.
- Build 2: tiered leans (inner/mid/outer) with droop. Wider, but outer blades lay flat and the middle was empty; too wide in Y (5.5).
- Build 3: continuous lean spread, broader blades (0.8), 18 blades, droop scaled by f^2. Hero mass now resembles the reference fan; footprint 4.3 x 4.6.
- Build 4: cut tuft wider (1.6 x 1.0), blunt tops kept. Stopped at the 4-build cap.
- Open (must): outer tip droop weaker than reference (goal 4); top-view star blades overlap rather than separating (goal 10). Fix next: narrower outer blades with stronger droop (~70 deg) and fewer inner blades.

