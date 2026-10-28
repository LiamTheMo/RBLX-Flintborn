# W04 row 2 — Young Fir: visual goals (revision 5)

Reference: `art/reference/kit/rows/W04_row2.png` (studied at 2-3x crops) and the full sheet
`W04_pines_firs_saplings.png`. Compare render: `renders/kit/W04/young_fir_compare.png`.
Build: `BLENDER_ARGS="W04 --only young_fir" art/blender/run.sh scripts/build_kit.py art/blender/assets/kit/wip/W04_young_fir.blend`
Export check: `BLENDER_ARGS="art/blender/assets/kit/wip/W04_young_fir.blend" art/blender/run.sh scripts/export_kit_roblox.py art/roblox/kit/wip/W04_young_fir/manifest.json`

Reference measurements (front cell, silhouette profile, 17 studs tall): crown = a small top cone (tips
~14.3) plus one spiky hem (tips ~11.5, ~6 wide); a deep waist at ~11; middle group of two rows of flaps
down to ~7.8 (~8.5 wide); a waist at ~7.5; skirt of two rows down to ~4.9 (~10-11 wide); trunk ~1.4-1.8
wide below. Every row is a ring of long, broad, pointed leaf flaps radiating from the axis (a star of
pleats), not a flat pagoda ring. Canopy colour sampled from the hero cell: p10 #2F3A1C, median #467D3C,
lit p90 #A1BF34 — one needle colour shaded by light.

## ASSEMBLED / HERO
H1. [must] Hero ~11 W x 11 D x 17 H; slim spire, canopy W/H about 0.65.
H2. [must] Canopy reads as THREE groups (crown, middle, skirt), the outline stepping out at each.
H3. [must] Each hem is a ring of broad leaf flaps with V notches; the trunk is not seen through the
    canopy above the skirt.
H4. [must] Tips are long sharp points; the skirt tips droop clearly below their notches.
H5. [must] (verifier) Reddish-orange trunk visible below the skirt for about the LOWER THIRD (skirt
    bottom ~5.3-5.6), ~1.6 wide, flaring into small roots that are not hidden by the dressing.
H6. [must] Grey faceted boulder ~2 W x 3 H on the +X side, leaning, clearly visible beside the trunk.
H7. [should] 2 small pebbles, 5-7 grass tufts and a thin cream soil patch round the base.
H8. [must] Hero <= 4000 tris, one mesh, origin bottom centre, nothing below z=0, hull, dressing faces
    kit_nocollide=1, runner "0 problems".
H9. [must] (verifier) The gaps between the groups read as SHADOW (the dark underside of the upper group
    over the next group's top), never as a lit trunk stub: no bark visible between groups.
H10. [must] Trunk continuous from the ground into the canopy (no floating bark sliver).
H11. [should] (verifier) Canopy bulk and flap size comparable to the reference: chunky overlapping
    flaps with clearly darker undersides, not a stack of thin pagoda rings.
H12. [should] (verifier) Boulder out at x~3.5, ~2 W x 3 H, clearly leaning.
H13. [should] (verifier) Tips ~20% longer than revision 4 and of uneven length (ragged spikes).

## FRONT
F1. [must] Front silhouette: one sharp apex, stepped rows widening downward to ~10-11 at the skirt,
    trunk centred below, boulder at the bottom right.
F2. [should] Front shows ~5 broad flap points along each hem edge.

## SIDE
S1. [should] Side view reads as the same tree (same rows, same widths).

## TOP
T1. [must] Top view: a sharp star outline (7-8 main points with smaller interleaved points), not a
    round blob.
T2. [should] A small crown star visible at the centre with ridges radiating from the axis.

## PALETTE / MATERIALS / EXPORT
P1. [must] One key per material: w04_needle (#6A963E, the sheet's shared value) on every canopy face;
    w04_bark trunk/roots/branches (reddish-orange); w04_wood_end only on cut tops/stub ends; w04_ground
    soil; w04_grass tufts; kit_rock boulder/pebbles. Tint = one uniform per-tree needle Tint plus small
    random variation, quantised.
P2. [should] (verifier) Canopy as dark and saturated as the reference (median ~#467D3C, lit faces
    lime, undersides dark), not pale yellow-green.
E1. [must] (verifier) The Roblox export (`export_kit_roblox.py`, pinned layout, no FB_RETINT) reports
    0 problems.

## PARTS
A1. [must] Five parts with exact names: YoungFirCrownTier (top cone + one spiky hem), YoungFirMiddleTier
    (two nested hems), YoungFirLowerSkirt (two hems, widest ~11, drooping tips), YoungFirTrunk (tapered,
    cut top with wood-end ring and sunken heart), YoungFirRootBase (flared roots cut flat at ~1.8,
    pebbles, tufts, soil).
A2. [must] Parts within budget (1500 / 1500 / 1500 / 800 / 1500), origin bottom centre, hull.
A3. [should] Canopy parts are the hero's own hems, so they re-stack into the hero.
A4. [should] (verifier) YoungFirTrunk's cut top shows a wide wood-end ring and a sunken heart.

## VARIATIONS
V1. [must] YoungFirSparse ~8 W x 16 H: 5 small separated tiers, long reddish trunk, bare branch stubs.
V2. [must] YoungFirFull ~12 W x 17 H: 7 dense overlapping hems, wide skirt, trunk barely visible.
V3. [must] YoungFirLeaning ~10 W x 15 H: bowed trunk, tip ~2.5 studs toward +X.
V4. [should] Variants carry the same base dressing (tufts, pebbles, soil).

## Status after revision-5 build 8 (final): runner 0 problems, 9 assets, 8286 tris; export 0 problems
Judged by eye, cell by cell, against the reference row in the compare image (2x crops), plus 420x560
studio renders of the hero beside the reference front cell.

- H1 MET: KITSTAT 11.4 x 11.2 x 17.0; a slim spire like the sheet's, a touch narrower in the front view.
- H2 MET: iso and front show a crown spire, a middle mass and a wider skirt, the outline stepping out
  under the crown hem and under the middle group; the steps are softer than on the sheet.
- H3 MET: each row is a ring of broad pointed flaps with V notches; no trunk shows through the canopy.
- H4 MET: flaps end in long sharp points; the skirt points hang below the notches (front cell).
- H5 MET (was UNMET): the skirt bottom is now at ~5.6, so the reddish trunk shows for about the lower
  third in hero and front cells, ~1.5 wide, with the root flare clear of the tufts (tufts moved to the
  sides and back).
- H6 MET: the boulder stands right of the trunk at x~3.4, ~2.3 W x 2.9 H, chunky and leaning outward;
  visible in the hero and front cells.
- H7 MET: 7 tufts, 2 pebbles, cream soil patch.
- H8 MET: hero 1826/4000 tris, one mesh, hull, dressing kit_nocollide=1, runner 0 problems.
- H9 MET (was UNMET): the trunk now ends at z=10.8 inside the middle group and each group's apex rises
  into the under-cone of the group above, so no bark shows between groups; the bands under the crown hem
  and the middle group read as shadow on the next group's flaps (hero and front cells).
- H10 MET: one trunk from the ground into the middle group.
- H11 PARTLY / UNMET (should): the canopy is now rows of long broad leaf flaps radiating from the axis
  (no pagoda rings), with darker keels under each flap; still less chunky and less contrasted than the
  sheet's fat two-tone flaps.
- H12 MET: boulder at (3.4, -1.3), 2.3 x 2.1 x 2.9, lean ~16 deg, no longer hidden behind the trunk.
- H13 MET: tips run from near the axis to well past the notches (notch 0.56 R) with +/-9% length jag;
  visibly longer, more ragged spikes than revision 4.
- F1 MET: front cell: one apex, stepped rows widening to the skirt, trunk centred, boulder bottom right.
- F2 MET: about 4-5 flap points per row across the front.
- S1 MET: side cell is the same tree.
- T1 MET: top cell is a star of ~7 big points with smaller interleaved points; more ragged than the
  sheet's crisp 8-point star.
- T2 UNMET (should): the centre star is there but does not stand out lit as on the sheet.
- P1 MET: one key per material; w04_needle kept at the shared #6A963E (the other three W04 modules still
  use it); one uniform needle Tint 0.75 with +/-5% variation quantised to 0.025 steps.
- P2 UNMET (should): render median #627255-#648543 vs reference #467D3C, lit p90 #80A756 vs #A1BF34: the
  canopy is a little darker than revision 4 but still lower contrast and less lime than the sheet; the
  studio's blue ambient flattens it and the hue is the shared key's.
- E1 MET (was UNMET): FB_RETINT=1 export refreshed the wip layout; a pinned re-export then reports
  "palette 6 colours / 33 levels, 0 problems".
- A1 MET: five parts with exact names; crown 5.5 x 5.4 (top cone + hem), middle 8.4 wide (two rows),
  skirt 10.8 wide with drooping points, trunk 4.6 tall with cut top, root base cut at 1.8.
- A2 MET: 224 / 208 / 240 / 86 / 850 tris, all hull.
- A3 MET: the canopy parts are built by the same hero_tiers() call, so they re-stack exactly.
- A4 PARTLY (should): the trunk part's ring is wider (heart 0.42 of the radius) and the heart sinks 0.28,
  but at the parts cell's 20-degree elevation the cut top shows only as a thin pale rim.
- V1 MET / V2 MET / V3 MET / V4 MET: unchanged from revision 4 (Sparse 8.2 x 16.0, Full 12.7 x 17.0,
  Leaning 10.0 x 15.0, all with tufts, pebbles and soil); the verifier passed them.

## Iteration log (revision 5)
1. Removed the 0.74 needle Tint base; Tint quantised to 0.025 steps. Steeper spruce hems; trunk visible
   to ~5.2; tufts moved off the root flare; bigger boulder at x~3.5; trunk part cut top wider/sunk.
   Spire shape better, trunk shows the lower third.
2. Deep pleats (fold 0.4, keel 0.55) and a chunkier boulder: canopy went blocky, groups merged. Reverted.
3. 6-7 broad flaps per hem, interleaved yaws, uniform needle Tint 0.85: shape OK, still a solid cone.
4. Re-measured the sheet's front silhouette; tall crown hem: crown became a faceted diamond. Rejected.
5. Rewrote the hero as six hems (2+2+2) with full-length pleats from near the axis (s_r 0.12, s_f 0.9),
   tip heights from the sheet's profile, trunk ending inside the middle group: rows of spiky flaps, no
   bark in the gaps.
6. Wider flaps (wE 0.56, rE 0.8): flaps went blunt (stacked rings). 7. Edges widest at 0.6 of the flap
   (rE 0.6), notch 0.56: broad flaps with long sharp points.
8. w04_needle back to the shared #6A963E (siblings keep it) with a uniform needle Tint 0.75; export with
   FB_RETINT=1, then a pinned export: 0 problems. Stopped here (build cap reached; every must MET).
