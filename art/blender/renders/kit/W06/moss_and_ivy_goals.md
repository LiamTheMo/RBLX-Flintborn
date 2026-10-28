# W06 row 4 - Moss and Ivy: visual goals

Reference: `art/reference/kit/rows/W06_row4.png` (full sheet `W06_bushes_ferns_vines_moss.png`).
The reference hero and variants are drawn from the front-RIGHT (front face broad on the left of
the image, right face narrow on the right), so the module sets HERO_AZIMUTH = +22.

Status key: MET / UNMET, judged by eye on `moss_and_ivy_compare.png` (cell under cell), after build 5.
The runner's PARTS cell stacks the thin upright overlay parts in rows in front of one another, so
they overlap there; the part shapes were also checked one by one in
`moss_and_ivy_cells/parts_alone_check.png` (each part rendered alone with flintkit.render_sheet).

## ASSEMBLED / HERO
1. [must] Near-cube ruin block ~6.5 W x ~6 D x ~6.5 H studs overall (moss included), origin bottom centre, front -Y. - MET: reads as a chunky cube like the reference; KITSTAT 7.0 x 6.3 x 6.4 (foot moss adds the extra width).
2. [must] Stone core of 3 courses of chunky bevelled light-grey blocks (~1.5-2.2 wide, ~1.8 tall) with visible dark joints and running-bond (offset) vertical joints. - MET: 3 courses of rounded-edge grey blocks with dark joint grooves; vertical joints step between courses on both visible faces.
3. [must] A heap of 4-6 lumpy faceted moss cushions on top, biased to the back/left, bright yellow-green, some spilling over the front top edge. - MET: 5 big domes plus small ones piled on top, highest at back-left, two drips hang over the front edge.
4. [must] Dense ivy curtain on the front-right corner: right ~45% of the front face and the front ~1/3 of the right face, cascading from the top edge (leaves lip over the edge) down to the ground. - MET: hero and front cells show a solid leaf curtain from the top lip to the foot over the right half and round the corner.
5. [must] Ivy leaves are flat, pointed, 3-5 lobed (~0.5-0.8 across), lying close to the stone, tips mostly down/sideways; thin brown tendrils visible between leaves. - MET: broad pointed 5/3-lobed leaves hang tip-down close to the wall; brown stems show between them (clearest in the side cell).
6. [must] 3-5 moss cushions of mixed sizes at the foot (mostly along the front), plus 2-3 small grey rocks and a few loose leaves. - MET: 4 front moss mounds of mixed size plus one at the left, 3 grey rocks and 2 loose leaves.
7. [should] A small ivy patch climbs the lower-left of the front face (as on the reference hero). - MET: a short leafy run climbs the lower-left front blocks in the hero and front cells.

## FRONT
8. [must] Front view: stone face of ~3-4 block columns x 3 courses; ivy covers the right half top-to-bottom, stone clearly visible on the left half; moss mounds sit on the top and drip over the top edge. - MET: 4 columns x 3 courses, curtain on the right half, bare stone on the left, moss mounds along the top with drips.

## SIDE
9. [should] Side (right) view: dense ivy down the front (left-in-view) edge of the right face, a thinner strip toward the back edge, moss mounds on top. - MET: side cell shows a wide curtain on the left ~40% and a thin strip at the right/back edge, moss on top.

## TOP
10. [should] Top view: square-ish footprint, moss mounds + ivy leaves cover ~40-60% of the top, block joints visible on the rest. - UNMET: coverage is right (~60%, joints visible bottom-left), but the reference top is ivy-dominated while mine is moss-dominated (the moss heap is what the hero/front cells need).

## PARTS
11. [must] MossCushionLarge ~2.6 x 2 x 1.2: lumpy cluster of 5-7 faceted domes; MossCushionSmall ~1.4 x 1.2 x 0.8 of 3-4 domes; both w06_moss. - MET: alone-render shows 6 and 4 distinct round faceted lumps; KITSTAT 2.5 x 1.9 x 1.2 and 1.3 x 1.1 x 0.8. (In the runner's parts cell the large one is partly behind the ivy cluster.)
12. [must] IvyClusterFlat: upright mat ~2 x 2, <= 0.4 deep, 10-14 leaves on short tendrils, wider at the top and drooping to a ragged point. - MET: rounded leaf mat, wide at top, tapering to a single drooping leaf; 2.3 x 0.4 x 2.1.
13. [must] IvyTendril: curly brown stem ~2.5 long rising diagonally with 3-5 small leaves. - MET: S-curved stem rising bottom-left to top-right with a hooked tip and 5 small leaves (2.3 x 0.4 x 1.9).
14. [must] IvyCornerPiece: ivy cluster bent 90 deg round an outside corner, ~2 x 2 x 2.5, a stem showing at the bottom. - MET: leaves on two perpendicular faces with stems at the foot; 2.0 x 1.8 x 2.5.
15. [must] IvyLeafSingle: one faceted pointed 3-lobed leaf (with small basal lobes) ~0.9 long with a stalk. - MET: broad 5-point ivy leaf (3 main lobes + 2 basal), faceted fan, brown stalk at the top; 0.9 x 0.2 x 1.0.

## VARIATIONS
16. [must] CornerWrap ~5 x 5 x 5: 3 smaller courses, moss heaped on top, ivy wrapping the front-right corner and running down both faces to the ground, moss and rocks at the foot. - MET: cell matches the reference A (3 courses, moss heap, corner curtain to the ground, rocks and moss at foot); 5.4 x 5.2 x 5.1.
17. [must] WallStrip ~7 W x 2 D x 4.5 H: low 3-course wall, two separate vertical ivy strips (left third and right of centre) hanging from the top edge to the ground, moss tufts along the base. - MET: two separate full-height strips with bare stone between, moss tufts at the base; 7.1 x 2.8 x 4.8.
18. [must] RockCap ~6.5 x 5 x 4: rounded faceted light-grey boulder, 3-4 moss mounds on top, ivy draping down its front-left face, small rocks at the foot. - MET: big faceted grey boulder, moss heap on top, ivy curtain on the front-left to the ground, rock + moss at the foot; 7.1 x 5.2 x 4.1.

## PALETTE
19. [must] One colour per material: w06_stone #B1ADA9 (blocks, boulder, rocks), w06_moss #ACC722 (cushions, tufts), w06_ivy #66A828 (all ivy leaves), w06_bark #8D6237 (tendrils/stalks); no shade variants. - MET: only these 4 keys in the module PALETTE and on the assets; runner reports no shade pairs or painted lighting.
20. [must] Moss and ivy read as clearly different greens (moss yellow-green and puffy, ivy deeper green and leafy) in every cell; never blended. - MET: lime moss domes vs mid-green leaves are distinct in every cell.

## SCALE / OVERLAYS / BUDGET
21. [must] Overlay parts (IvyClusterFlat, IvyTendril, IvyLeafSingle, IvyCornerPiece) are thin and face -Y so they lay on any wall (flat ones <= 0.4 deep). - MET: flat/tendril/leaf 0.4/0.4/0.2 deep facing -Y; the corner piece faces -Y and +X by design.
22. [must] Budgets: hero <= 5000 tris, variants <= 4000, parts per spec; runner ends with 0 problems. - MET: hero 4488, variants 2681/1954/1258, parts 180/120/324/184/516/42; "0 problems".

## Iteration log
- Build 1: first pass. Hero 5402 tris (over), leaves spiky/thin, top moss low flat clusters, parts cell a pile; ivy flat/corner stems poked above the leaves.
- Build 2: broader leaves (0.6-0.85), 3-sided stems, puffier domes, crown leaves to hide stem tops, smaller core. Curtain now dense; hero under budget; corner piece 642 (over).
- Build 3: top/foot moss rebuilt as heaps of big round domes (reference's chunky mounds), RockCap/CornerWrap moss heaps, shorter overlay parts, corner piece trimmed to 516. Top moss now reads like the reference.
- Build 4: hero blocks narrowed to ~1.6 (4 columns in the front view like the reference), extra tendril on the right face so the side view shows the wide curtain.
- Build 5: ivy leaf outline with shallower notches (reads as ivy, not stars), moss parts rebuilt as distinct dome lumps, flat cluster tapers to a point, leaf stalk attached. Every must goal MET; stopped.
