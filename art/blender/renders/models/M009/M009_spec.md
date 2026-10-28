# 009 Iron Meteor — spec

Reference: `art/blender/assets/references/009.png` (IRON METEOR, page 13). Builder: `art/blender/kit/mcp/m009.py` → `build()`.
Assets (collection `Kit/M009 Iron Meteor`): `IronMeteorDeposit` (hero), `IronMeteorShellPiece` (reusable), `IronMeteorCore`, `IronMeteorImpactRock` (reusable). A kit sheet already owns `IronMeteor`, so the hero is `IronMeteorDeposit`.

## Study (2a)

- **Classification:** full asset (resource node / meteorite deposit), budget 4000 tris; parts 1000.
- **Silhouette:** a big dark faceted meteor, wider than tall, with a smaller lobe fused at its front left. Jagged cracks run partway round it, glowing orange where the metal core shows through. A ring of pale impact rocks sits round the foot, bigger at the front, with a few loose stones further out. Broad flat faces.
- **Parts:** rock shell pieces (4–5 per meteor, reusable), a central metal core, impact rocks (reusable).
- **Scale:** 11.8 × 11.0 × 5.9 studs.
- **Colours (sheet swatches):** rock shell #3E3C41, metal core #877E7C, impact rock #AD998E, crack/core #F55E21. The lit shell in the sheet's renders reads #5C575D.
- **Effects:** the cracks and core glow. VFX sockets: `heat_glow` at the meteor's centre and `embers` above it.

## Delivery

- Palette:
  - `m009_shell` #55515A with `m009_shell_grey` #645E63 as broad facet patches (by noise, not by facing). These are matched to the sheet's renders, not to the darker swatch.
  - `m009_core` #F55E21 at emission 1.5, which exports as a glow (Neon) piece.
  - `m009_impact` #B8A498 and `m009_impact_cool` #ABA09A, lifted from the #AD998E swatch so the ring reads pale all round.
- Hero:
  - Two faceted hulls (the main meteor and the lobe).
  - Six jagged cracks carved by exact boolean difference. The cutter is V-wedges, 0.5 wide and 0.8 deep, whose walls take the core's orange.
  - Unioned with 22 impact rocks, then cut flat at z = 0. The floor faces under the meteors are orange, as on the sheet's underside view.
  - 2278 tris; zero non-manifold or boundary edges.
  - 8 closed shells: the meteor and its touching rock ring, plus the loose stones further out, as on the sheet's top view.
  - Export: 3 solid and 3 glow (Neon) pieces, 2 VFX sockets.
- Parts:
  - `IronMeteorShellPiece` is one Voronoi wedge of the meteor shell, with orange seam faces.
  - `IronMeteorCore` is the faceted orange core ball.
  - `IronMeteorImpactRock` is one rim rock.

## Conflicts

- The "Metal Core" swatch is medium grey, but every view on the sheet shows the core and inner faces as the orange "Crack / Core" colour. Orange is used; the grey swatch is not used.

## Result

- Verifier round 1 PASS 6/10 (all technical checks clean; several closed shells accepted for the loose stones). Then: meteor sunk deeper so the orange underside is larger, lobe smaller and fused deeper, outlying stones larger and closer, impact rocks paler.
- Open minors: cracks are an even width (the sheet's taper and vary); `IronMeteorShellPiece` is a plain wedge without the sheet's hollow interior.
