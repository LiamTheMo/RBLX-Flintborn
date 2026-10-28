# CoalNode (R01 row 3): visual goals (revision 5: gem points after verifier fail)

Reference: art/reference/kit/rows/R01_row3.png (cells: hero iso, front, side, top, parts, drops + depleted).
Scale: 1 unit = 1 stud, origin bottom centre, front -Y. The reference front cell measures 143 px = 5 studs,
so the heap is about 7.2 W x 4.8 D x 5 H.
The light and dark facets on the reference are LIGHTING. Every material has one flat base colour.
(V) marks goals from earlier verifier audits, (V4) the revision 3 verifier fail and (V5) the revision 4
verifier fail (all musts). All were judged by eye from coal_node_compare.png (build 4, rev 5), cell by cell
against the reference row.

## ASSEMBLED / HERO
| # | Goal | Pri | Status | Evidence (build 4, rev 5) |
|---|------|-----|--------|----------|
| H1 (V4) | Three distinct near-black chunks (tall centre main, two side chunks leaning outward and slightly forward) read as a crown of gems, each separately outlined | must | MET | hero and front cells: three separate pointed gem outlines with dark gaps between them; side points clearly below the main shoulders |
| H2 (V5) | Main chunk broad (~3.9 W), tall (~4.9), a hewn gem of ~8-10 large crisp planes per view, NO flat top table, shoulders converging to a peak ~0.4 studs left of centre | must | MET | hero/front cells: vertical girdle with a big front face, ~60 deg shoulder planes, then five shallow crown planes meeting in a short ridge left of centre; the flat table is gone. CoalMainChunk 3.9 x 3.8 x 4.8 |
| H3 (V5) | Side chunks egg-shaped (~2.5-2.6 W x 2.2 D x 3.0-3.2 H) with few large planes and a visible point, leaning outward, tops ~0.65 of the main height, lower halves visible | must | MET | front cell: both side eggs end in a four-plane point, lean outward and top out at ~0.62-0.65 of the main; their lower halves show beside the front rock |
| H4 (V) | Wide low warm-grey front base rock (~3.6-3.8 W x 1.6 H) overlapping the coal's bottom, plus smaller grey rocks at both outer front corners | must | MET | hero/front cells: wide grey rock low in the middle over the coal feet, a grey rock at each outer corner |
| H5 (V4) | Silhouette width: side chunks flare out to about 7 studs and are clearly separated from the main chunk at the top | must | MET | front cell: background shows between the side points and the main shoulders; sides pulled in 0.15 and lean reduced, KITSTAT 7.2 W |
| H6 | Hero bounding box ~7.2 W x 4.8-5 D x 5 H studs | must | MET | KITSTAT CoalNode 7.2 x 5.0 x 4.9 |
| H7 (V5) | Crisp planar facets everywhere, no rounding, no slivers: each chunk reads as a hewn gem of a few big planes (main ~8-10 per view), not a rounded egg | must | MET | hero/front cells: main shows its big front face, 2 girdle sides, 3 shoulder and 3 crown planes with straight ridges and a point; side eggs show ~6-8 planes each and a point; no small noisy facets |
| H8 (V) | Thin light-catching edges from geometry only (no lighter edge colour, no outline) | must | MET | 0.025 coal chamfer in the coal material; hero cell shows faint edge highlights |
| H9 (V5) | Coal facets vary in value through their angle to the light (vertical girdle, ~60 deg shoulders, ~30 deg crown: 30-60 deg between neighbours), not through paint | must | MET | hero cell: the front face and upper-left crown planes read lighter grey, side girdle faces mid, shaded shoulders dark; Tint stays random 0.92-1.08. Overall still darker than the reference's blue-grey because the fixed coal key is darker than its lit swatch |
| H10 (V4) | Main chunk's front face is a large face toward the player | should | MET | front/hero cells: a big girdle face with a pointed top at the front of the main chunk; harvest_hit sits on it |

## PALETTE / MATERIAL
| # | Goal | Pri | Status | Evidence |
|---|------|-----|--------|----------|
| P1 | Only two materials: `coal` (KIT_PALETTE #2F3137, used as-is, not redeclared) and `r01_stone` (#877C78) | must | MET | module PALETTE = {r01_stone} only; COAL = ("coal",), STONE = ("r01_stone",) |
| P2 | No shade variants: no coal_light ridge colour, chamfers stay coal | must | MET | finish_chunk puts bevel faces on material 0; runner reports 0 problems |
| P3 | Every grey base rock (hero, base-rock part, depleted) is r01_stone, the same stone as StoneNode | must | MET | every base_rock() call uses STONE; the rocks read warm grey in the hero, parts and depleted cells |
| P4 | Tint is a modest random value per facet (coal +/-8%, stone +/-6%), never set by face direction | must | MET | COAL_TINT (0.92, 1.08) and STONE_TINT (0.94, 1.06), drawn with rng.uniform per face |
| P5 | Strong value contrast: near-black coal vs light warm-grey stone in every cell | must | MET | every cell: grey rocks clearly lighter than the coal |
| P6 | Runner reports 0 problems (nothing like 'lighting is painted into the colours', no shade pairs) | must | MET | STATS R01/coal_node: 7 assets, 3018 tris, 0 problems |

## FRONT / SIDE / TOP
| # | Goal | Pri | Status | Evidence |
|---|------|-----|--------|----------|
| F1 (V5) | Front view: three gems, main peak left of centre and tallest, side tops ~0.65 of its height, low wide front rock, rocks at the outer corners | must | MET | front cell: main rises to a short ridge left of centre, side points at about 0.62/0.65 of its height, wide grey rock over the coal feet, corner rocks |
| S1 (V5) | Side view: tall tapered main chunk behind and clearly tallest, one side chunk standing forward of it (to the -Y side) at ~0.65 of its height, grey rocks at the foot | must | MET | side cell: main rises behind to a crown well above the near side gem, whose point sits at about 0.6 of the main; grey rocks at both feet. The main's flank reads darker and blockier than the reference |
| T1 (V4) | Top view: compact triangle of three coal gems (main at the back centre, sides front-left and front-right), grey rocks peeking out at the front, the back and the left/right edges | must | MET | top cell: main's crown planes converging off-centre, two side gems toward the front, grey rocks visible back-left, back-right, the sides and front |

## PARTS
| # | Goal | Pri | Status | Evidence |
|---|------|-----|--------|----------|
| A1 (V5) | CoalMainChunk: broad hexagonal gem ~3.9 x 3.8 x 4.9 ending in a point left of centre | must | MET | parts cell: hexagonal gem with a big front face and a pointed crown; 3.9 x 3.8 x 4.8, 234 tris. It reads a little narrower than the reference's parts-cell drawing |
| A2 (V5) | CoalSideChunk: squat egg gem ~2.6 W x 2.2 D x 3.1 H with a point, not a pillar | must | MET | parts cell: egg-shaped gem widest at ~40% of its height, ending in a four-plane point; 2.6 x 2.3 x 3.1, 218 tris |
| A3 | CoalNodeBaseRock: two grey rocks side by side, one wider/lower, one taller | must | MET | parts cell: wide low rock + taller one, r01_stone; 3.8 x 1.8 x 1.7 |

## DROPS / DEPLETED
| # | Goal | Pri | Status | Evidence |
|---|------|-----|--------|----------|
| D1 | CoalLump ~1.25 x 1.05 x 0.9 closed, chunky, faceted coal lump, <=300 tris, box collision | must | MET | drops cell: chunky hexagonal gem lump; 1.2 x 1.1 x 0.9, 196 tris |
| D3 (V) | CoalLumpB ~1.2 x 1.0 x 0.9, wedge-ish so it differs from CoalLump | must | MET | drops cell: five-sided lump with a slanted top; 1.1 x 1.0 x 0.9, 162 tris |
| D2 | CoalNodeDepleted: grey r01_stone rocks only (larger centre rock, smaller ones left and right), no coal, low, on the hero footprint | must | MET | depleted cell: grey rocks only; 7.1 x 5.0 x 1.5 |
| D4 | Drops read as large as the reference lumps next to the depleted base | should | UNMET | drops cell: lumps look small because they keep the specified ~1.25 stud size (verifier: leave as is); the reference cell draws them larger |

## BUILD / VFX
| # | Goal | Pri | Status | Evidence |
|---|------|-----|--------|----------|
| B1 | Build clean: exit 0 and "0 problems" | must | MET | STATS 7 assets, 3018 tris, 0 problems |
| B2 | All assets under budget, nothing below z=0, one mesh each, origin bottom centre | must | MET | hero 1166/3000, parts <=276/1500, depleted 766/2000, drops <=196/300; gem_bm clamps z >= 0 |
| V1 | harvest_hit on the main chunk front at z~2.7 (chips #3A3C43/#24262B, dust #55575F/#3B3D44), harvest_deplete at base centre, faint ore_glint at z~3.8 (#C9CED8/#8E94A2, rate 0.3, light 0.4); no VFX on parts, drops or depleted | must | MET | sockets ray-cast onto the main chunk's front face; only the hero carries sockets |

## Iteration log
Revisions 1-3 (13 builds): shapes, rocks, sockets, one colour per material. Revision 4 (6 builds): coal rebuilt
from explicit plane tiers (gem_bm); the verifier then failed the main chunk as a flat-topped rounded egg with
no apex, and the near side gem as too tall in the side view.

Revision 5:
1. Build 1: replaced the flat top table with an apex tier (crown planes all passing through one point ~0.4 studs
   left of centre) on the main (4 planes) and the sides (3 planes); side chunks pulled in 0.15 and set to
   3.0/3.2 high. The main became a sharp spike, much narrower at the top than the reference.
2. Build 2: blunter peak (5 crown planes at ~30 deg world slope, shoulders ~58 deg), side crowns 4 planes, less
   outward lean. The peak now reads left of centre; the hero was still 7.5 W because of the corner rocks.
3. Build 3: girdle a little higher and crown shallower so the top is broad like the reference; corner rocks
   pulled in to x +/-2.8. Hero 7.2 x 5.1 x 4.9.
4. Build 4: trimmed the main's depth so CoalMainChunk is 3.9 x 3.8 x 4.8. All musts MET by eye.
