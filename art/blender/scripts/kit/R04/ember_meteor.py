"""R04 row 2: Ember Meteor resource node (cracked-open charcoal shell around a molten core)."""
import math

SUBJECT = "EmberMeteor"
ROW = 2
HERO_AZIMUTH = -22
SIDE_AZIMUTH = -90   # reference SIDE cell shows the core on the right: view from the left side

PALETTE = {
    "r04_meteor_rock": ("#2E2E36", 0.9, 0, 0),
    "r04_impact_rock": ("#7D7570", 0.95, 0, 0),
    "r04_lava_crack": ("#FF9A1E", 0.5, 0, 1.5),
    "r04_ember_core": ("#E8501A", 0.6, 0, 1),
    "r04_cooled_ember": ("#A8401F", 0.8, 0, 0),
}

ROCK = "r04_meteor_rock"
RUBBLE = "r04_impact_rock"
CRACK = "r04_lava_crack"
CORE = "r04_ember_core"
COOLED = "r04_cooled_ember"

# The shared sheet key #2E2E36 renders near-black; the reference shell mid-tone is ~#46464E.
# Tint is a linear multiply (2.3x would be needed), so the fix belongs in the sheet palette.
# Shell keeps Tint 1.0 with only small random variation.
SHELL_TINT = 1.0


def _slab(a, size, loc, rot, cracks=()):
    """Crisp angular slab: icosphere subdiv 1, near-coplanar faces dissolved into ~10-16 big
    planes, underside flattened at z=0. `cracks` = list of (dir, top_frac) seams that walk the
    slab's own mesh edges (so they lie on its edges), copied before later calls invalidate verts."""
    r = (size[0] / 2, size[1] / 2, size[2] / 2)
    t = SHELL_TINT * (1 + a.rng.uniform(-0.03, 0.03))
    verts = a.ico(r, (loc[0], loc[1], r[2] * 0.88), rot, mat=ROCK, subdiv=1, jitter=0.12,
                  facets=0, tint=t, face_tint_var=0.04)
    ztop = max(v.co.z for v in verts) * 0.93   # chop the tip into a small crag facet
    for v in verts:
        if v.co.z < 0:
            v.co.z = 0.0
        elif v.co.z > ztop:
            v.co.z = ztop
    paths = [_walk(verts, d, top) for d, top in cracks]
    return paths


def _walk(verts, d, top=0.9):
    """Zig-zag crack along mesh edges: start low on the side facing d, climb through linked
    verts that keep facing d. Points are pushed 0.06 outward so the strip sits on the surface."""
    cx = sum(v.co.x for v in verts) / len(verts)
    cy = sum(v.co.y for v in verts) / len(verts)
    z0 = min(v.co.z for v in verts)
    z1 = max(v.co.z for v in verts)
    l = math.hypot(d[0], d[1]) or 1.0
    d = (d[0] / l, d[1] / l)

    def face(v):
        return (v.co.x - cx) * d[0] + (v.co.y - cy) * d[1]

    vs = set(verts)
    low = [v for v in verts if v.co.z < z0 + 0.35 * (z1 - z0)] or verts
    cur = max(low, key=face)
    path = [cur]
    while cur.co.z < z0 + top * (z1 - z0):
        nbrs = [e.other_vert(cur) for e in cur.link_edges]
        nbrs = [n for n in nbrs if n.co.z > cur.co.z + 0.05 and n not in path and n in vs]
        if not nbrs:
            break
        cur = max(nbrs, key=lambda n: face(n) * 1.0 + (n.co.z - cur.co.z) * 0.25)
        path.append(cur)
    pts = []
    for i, v in enumerate(path[:-1] if False else path):
        ox, oy = v.co.x - cx, v.co.y - cy
        ol = math.hypot(ox, oy) or 1.0
        pts.append((v.co.x + ox / ol * 0.06, v.co.y + oy / ol * 0.06, max(v.co.z, 0.12)))
    dense = []
    for p0, p1 in zip(pts, pts[1:]):
        dense += [p0, tuple((p0[k] + p1[k]) / 2 for k in range(3))]
    return dense + pts[-1:]


def _seam(a, pts, w=0.09):
    if len(pts) >= 2:
        a.tube_loop(pts, w, mat=CRACK, rseg=4, closed=False)
    return pts[len(pts) // 2]


def _rubble(a, rocks):
    for (sx, sy, sz), (x, y), rz in rocks:
        a.rock((sx, sy, sz), (x, y, 0), (0.1, -0.08, rz), mat=RUBBLE, subdiv=1, rough=0.16,
               facets=6, sink=0.2)


def _core(a, rad, loc):
    return a.ico(rad, loc, (0.3, 0.2, 0.4), mat=CORE, subdiv=2, jitter=0.1, facets=14)


def build(kit):
    fk, vfx = kit.flintkit, kit.vfx
    out = []

    # ---------------- hero ----------------
    a = fk.Asset("EmberMeteor", "R04 EmberMeteor", seed=4201, tint_var=0.04)
    _core(a, (2.5, 2.25, 2.5), (0.0, -0.8, 2.6))
    seams = []
    # big left slab, leaning out to the left; crack on its core-facing edge
    seams += _slab(a, (4.1, 4.3, 7.0), (-2.4, 0.3), (0.05, -0.24, 0.25),
                   cracks=[((1, -0.6), 0.8), ((0.3, -1), 0.6)])
    # tallest back-right slab, leaning back-right
    seams += _slab(a, (4.4, 3.0, 8.4), (1.3, 1.7), (-0.18, 0.12, -0.3),
                   cracks=[((-0.8, -1), 0.8)])
    # front-right slab, leaning out to the right; crack on edge and one on its front face
    seams += _slab(a, (3.7, 3.4, 5.6), (2.7, -1.3), (0.12, 0.26, 0.5),
                   cracks=[((-1, -0.5), 0.8)])
    # small left-front slab
    _slab(a, (2.6, 2.3, 3.4), (-1.9, -2.4), (0.2, -0.15, 0.6))
    seam_mid = [_seam(a, p) for p in seams]
    _rubble(a, [
        ((3.0, 2.5, 2.5), (2.9, -3.0), 0.4),
        ((2.4, 2.0, 1.6), (0.4, -3.5), 0.1),
        ((2.0, 1.8, 1.4), (-1.6, -3.6), 0.9),
        ((2.2, 2.0, 1.5), (-3.6, -2.2), 0.3),
        ((1.9, 1.7, 1.3), (-4.0, 0.4), 1.2),
        ((1.8, 1.6, 1.2), (-3.0, 2.7), 0.6),
        ((1.6, 1.4, 1.0), (0.0, 3.4), 0.2),
        ((2.0, 1.7, 1.3), (3.2, 2.4), 0.8),
        ((1.9, 1.6, 1.3), (4.0, -0.3), 0.5),
        ((1.2, 1.0, 0.8), (-4.3, -1.2), 1.4),
    ])
    o = a.finish()
    vfx.add(o, "heat_glow", (0.0, -1.7, 2.8), scale=1.5, color=["#FF6A10", "#FFB030"],
            light={"color": "#FF6A10", "brightness": 1.6, "range": 14, "flicker": True})
    vfx.add(o, "embers", (0.0, -0.8, 5.4), scale=1.0)
    for p in seam_mid:
        vfx.add(o, "heat_glow", p, scale=0.4)
    vfx.add(o, "harvest_hit", (0, -4, 3), color=["#46464E", "#FF8A2A"])
    vfx.add(o, "harvest_deplete", (0, 0, 0.8))
    out.append(kit.tag(o, "hero", collision="hull", budget=4000,
                       notes="Ember Meteor node. heat_glow at core (orange PointLight), embers rising "
                             "above the core, small heat_glow on each lava seam, harvest_hit on the "
                             "front strike face (charcoal chips), harvest_deplete at base centre. "
                             "No ore_glint: core is molten, not glossy ore."))

    # ---------------- parts ----------------
    a = fk.Asset("EmberMeteorShellPiece", "R04 EmberMeteor part", seed=4202)
    p = _slab(a, (4.0, 3.0, 5.0), (0, 0), (0.0, 0.1, 0.3), cracks=[((0.4, -1), 0.75)])[0]
    m = _seam(a, p)
    o = a.finish()
    vfx.add(o, "heat_glow", m, scale=0.4)
    out.append(kit.tag(o, "part", collision="hull", budget=1500,
                       notes="Shell Piece: tall angular charcoal slab with one glowing seam "
                             "(small heat_glow)."))

    a = fk.Asset("EmberMeteorShellPieceB", "R04 EmberMeteor part", seed=4203)
    _slab(a, (5.0, 2.5, 3.0), (0, 0), (0.0, 0.08, -0.25))
    o = a.finish()
    out.append(kit.tag(o, "part", collision="hull", budget=1500,
                       notes="Shell Piece variant: flatter angular charcoal slab."))

    a = fk.Asset("EmberMeteorCore", "R04 EmberMeteor part", seed=4204)
    _core(a, (2.25, 2.0, 2.25), (0, 0, 2.15))
    o = a.finish()
    vfx.add(o, "heat_glow", (0, 0, 2.2), scale=1.0, color=["#FF6A10", "#FFB030"],
            light={"color": "#FF6A10", "brightness": 1.3, "range": 12, "flicker": True})
    out.append(kit.tag(o, "part", collision="hull", budget=1500,
                       notes="Ember Core: faceted molten core, emissive; heat_glow with orange light."))

    a = fk.Asset("EmberMeteorImpactBase", "R04 EmberMeteor part", seed=4205)
    _rubble(a, [
        ((3.0, 2.6, 1.8), (0.6, 0.1), 0.3),
        ((2.0, 1.8, 1.3), (-1.8, 0.3), 0.9),
        ((1.4, 1.2, 1.0), (-3.0, -0.5), 0.2),
        ((1.2, 1.0, 0.8), (2.8, 0.6), 1.1),
        ((0.9, 0.8, 0.6), (2.9, -0.8), 0.5),
        ((0.8, 0.7, 0.6), (-0.6, -1.2), 0.7),
        ((0.6, 0.6, 0.5), (1.6, 1.3), 0.0),
    ])
    o = a.finish()
    out.append(kit.tag(o, "part", collision="hull", budget=1500,
                       notes="Impact Base: grey-tan rubble cluster."))

    # ---------------- drops ----------------
    for name, rad, rot, seed in (
        ("CooledEmberFragment", (0.6, 0.5, 0.72), (0.4, 0.3, 0.5), 4206),
        ("CooledEmberFragmentB", (0.5, 0.45, 0.78), (0.2, 0.5, 1.1), 4207),
    ):
        a = fk.Asset(name, "R04 EmberMeteor drop", seed=seed)
        a.ico(rad, (0, 0, rad[2]), rot, mat=COOLED, subdiv=1, jitter=0.12)
        o = a.finish()
        out.append(kit.tag(o, "drop", collision="none", budget=300,
                           notes="Cooled Ember Fragment drop: dull burnt shard, no glow."))

    # ---------------- depleted ----------------
    a = fk.Asset("EmberMeteorDepleted", "R04 EmberMeteor depleted", seed=4208)
    _rubble(a, [
        ((2.6, 2.2, 2.0), (-0.6, 0.4), 0.3),
        ((2.2, 2.0, 1.7), (1.6, 0.8), 0.9),
        ((2.0, 1.8, 1.5), (0.8, -1.6), 0.4),
        ((1.8, 1.6, 1.3), (-2.4, -1.0), 1.2),
        ((1.6, 1.4, 1.1), (3.3, -0.6), 0.6),
        ((1.5, 1.3, 1.0), (-3.3, 1.2), 0.1),
        ((1.3, 1.1, 0.9), (-1.0, 2.3), 0.8),
        ((1.2, 1.0, 0.8), (2.4, 2.4), 0.2),
    ])
    o = a.finish()
    out.append(kit.tag(o, "depleted", collision="hull", budget=2000,
                       notes="Depleted (Base): low rubble pile, no meteor or glow."))
    return out
