"""009 Iron Meteor (references/009.png): a big dark faceted meteorite with jagged cracks glowing orange where its
metal core shows through, a smaller cracked lobe at its front left, and a ring of pale impact rocks round its foot.

    import importlib, m009; importlib.reload(m009); m009.build()

Parts as on the sheet: Rock Shell Piece (reusable, 4-5 per meteor), Metal Core, Impact Rock (reusable). The hero
is the meteor shell with the cracks carved in (exact boolean difference; the groove walls take the core's
orange) unioned with the rocks. A kit sheet owns `IronMeteor`, so the hero is `IronMeteorDeposit`.
"""
import math
import random

import bmesh
import bpy
from mathutils import Matrix, Vector

import flintkit

import kit_mcp as K
import kit_models as M
import m004

NUM, TITLE, SHEET = 9, "Iron Meteor", "M009"
SHELL, SHELL_GREY, CORE, IMPACT, IMPACT_COOL = ("m009_shell", "m009_shell_grey", "m009_core", "m009_impact",
                                                "m009_impact_cool")

# meteors: (label, centre, radii, seed, points, shell-piece directions as (azimuth deg, elevation deg); -90 = front)
METEORS = (("Main", (0.3, 0.5, 2.7), (3.7, 3.4, 3.4), 9001, 48,
            ((-140, 10), (-60, 20), (20, 15), (110, 10), (40, 72))),
           ("Lobe", (-2.9, -1.4, 1.5), (2.0, 1.85, 1.8), 9002, 30, ((-160, 10), (-70, 35))))
GAP = 0.32                  # seam width between the reusable shell pieces
# cracks: (meteor, polyline of (azimuth, elevation)); jagged as on the sheet, running partway round, not all over
CRACKS = (("Main", ((-112, 72), (-100, 52), (-116, 36), (-104, 18), (-118, 0), (-108, -14))),
          ("Main", ((-38, 64), (-26, 46), (-38, 30), (-24, 14), (-34, -2), (-26, -14))),
          ("Main", ((-112, 52), (-80, 60), (-62, 56))),
          ("Main", ((96, 60), (84, 42), (98, 26), (86, 8), (96, -10))),
          ("Main", ((150, 55), (164, 34), (150, 16), (160, -6))),
          ("Lobe", ((-128, 62), (-112, 38), (-126, 16), (-114, -8))))
CRACK_W, CRACK_DEPTH = 0.5, 0.8
CORE_FRAC = 0.84            # core radius as a share of the shell's smallest radius
ROCK_RINGS = [(0.0, 0.9, 7), (0.35, 1.0, 7), (0.7, 0.72, 6), (1.0, 0.3, 4)]


def palette():
    # the "Rock Shell" swatch is #3E3C41, but the sheet's lit shell renders read #5C575D: matched to the renders
    K.set_colour(SHELL, "#55515A", rough=0.85)
    K.set_colour(SHELL_GREY, "#645E63", rough=0.85)
    K.set_colour(CORE, "#F55E21", rough=0.5, emit=1.5)   # "Crack / Core": glows (a Neon piece in Roblox)
    K.set_colour(IMPACT, "#B8A498", rough=0.92)      # "Impact Rock" swatch #AD998E, lifted to read pale all round
    K.set_colour(IMPACT_COOL, "#ABA09A", rough=0.92)


def _dir(az, el):
    a, e = math.radians(az), math.radians(el)
    return Vector((math.cos(a) * math.cos(e), math.sin(a) * math.cos(e), math.sin(e)))


def _cloud(centre, radii, seed, n):
    """Evenly spread, slightly lumpy points on an ellipsoid (a Fibonacci sphere): the meteor's broad facets."""
    rng = random.Random(seed)
    c = Vector(centre)
    pts = []
    for k in range(n):
        z = 1 - 2 * (k + 0.5) / n
        r = math.sqrt(1 - z * z)
        th = k * 2.39996 + rng.uniform(-0.12, 0.12)
        s = rng.uniform(0.93, 1.05)
        pts.append(c + Vector((math.cos(th) * r * radii[0], math.sin(th) * r * radii[1], z * radii[2])) * s)
    return pts


def _clip(pts, centre, d, others):
    """The convex hull of pts cut back to the Voronoi cell of direction d (bisector planes against every other
    direction, each moved GAP/2 toward d): one shell piece's points."""
    bm = bmesh.new()
    vs = [bm.verts.new(p) for p in pts]
    bmesh.ops.convex_hull(bm, input=vs)
    for o in others:
        n = (o - d).normalized()
        geom = list(bm.verts) + list(bm.edges) + list(bm.faces)
        bmesh.ops.bisect_plane(bm, geom=geom, dist=1e-4, plane_co=Vector(centre) - n * GAP / 2, plane_no=n,
                               clear_outer=True)
    out = [v.co.copy() for v in bm.verts]
    bm.free()
    return out


def shell_piece(a, label, k, at_origin=False):
    _, centre, radii, seed, n, dirs = next(m for m in METEORS if m[0] == label)
    ds = [_dir(*x) for x in dirs]
    pts = _clip(_cloud(centre, radii, seed, n), centre, ds[k], [o for i, o in enumerate(ds) if i != k])
    bm = a.bm
    vs = [bm.verts.new(p) for p in pts]
    bmesh.ops.convex_hull(bm, input=vs)
    vs = [v for v in vs if v.is_valid and v.link_faces]
    bmesh.ops.recalc_face_normals(bm, faces=K.faces_of(vs))
    a._finish(vs, SHELL)
    # the cut faces are the seam walls: the core's orange (the sheet's "inner face"); a few broad outer facets
    # carry the lighter shell grey (by noise, not by facing)
    planes = [(o - ds[k]).normalized() for i, o in enumerate(ds) if i != k]
    ci, gi = a._mi(CORE), a._mi(SHELL_GREY)
    nf = K.noise_field(scale=0.4, seed=seed + k)
    for f in K.faces_of(vs):
        if any(f.normal.dot(n) > 0.97 for n in planes):
            f.material_index = ci
        elif nf(f.calc_center_median()) > 0.3:
            f.material_index = gi
    K.texture(a, vs, amp=0.03, scale=0.5, jitter=0.03, seed=seed + k)
    return vs


def core(a, label, at_origin=False):
    """The metal core: a faceted orange ball just inside the shell, so it fills the seams."""
    _, centre, radii, seed, _, _ = next(m for m in METEORS if m[0] == label)
    R = min(radii) * CORE_FRAC
    sq = [r / min(radii) for r in radii]
    c = Vector((0, 0, 0)) if at_origin else Vector(centre)
    pts = _cloud(c, [R * s for s in sq], seed + 50, n=22)
    bm = a.bm
    vs = [bm.verts.new(p) for p in pts]
    bmesh.ops.convex_hull(bm, input=vs)
    vs = [v for v in vs if v.is_valid and v.link_faces]
    bmesh.ops.recalc_face_normals(bm, faces=K.faces_of(vs))
    a._finish(vs, CORE)
    return vs


def shell(a, label):
    """The whole meteor shell: one faceted hull, a few broad facets in the lighter shell grey."""
    _, centre, radii, seed, n, _ = next(m for m in METEORS if m[0] == label)
    bm = a.bm
    vs = [bm.verts.new(p) for p in _cloud(centre, radii, seed, n)]
    bmesh.ops.convex_hull(bm, input=vs)
    vs = [v for v in vs if v.is_valid and v.link_faces]
    bmesh.ops.recalc_face_normals(bm, faces=K.faces_of(vs))
    a._finish(vs, SHELL)
    gi = a._mi(SHELL_GREY)
    nf = K.noise_field(scale=0.4, seed=seed)
    for f in K.faces_of(vs):
        if nf(f.calc_center_median()) > 0.3:
            f.material_index = gi
    K.texture(a, vs, amp=0.03, scale=0.5, jitter=0.03, seed=seed)
    return vs


def crack_cutter(a):
    """The crack grooves as cutting shells in the core's orange: each crack segment a V-wedge (CRACK_W wide at the
    surface, CRACK_DEPTH deep), overlapping at the joints."""
    for label, path in CRACKS:
        _, centre, radii, _, _, _ = next(m for m in METEORS if m[0] == label)
        c = Vector(centre)
        pts = [_dir(az, el) for az, el in path]
        pts = [c + Vector((d.x * radii[0], d.y * radii[1], d.z * radii[2])) for d in pts]
        for p0, p1 in zip(pts, pts[1:]):
            t = (p1 - p0).normalized()
            p0, p1 = p0 - t * 0.12, p1 + t * 0.12
            ring = []
            for p in (p0, p1):
                out = (p - c).normalized()
                side = t.cross(out).normalized()
                ring += [p + out * 0.5 + side * CRACK_W / 2, p + out * 0.5 - side * CRACK_W / 2,
                         p - out * CRACK_DEPTH]
            vs = [a.bm.verts.new(q) for q in ring]
            bmesh.ops.convex_hull(a.bm, input=vs)
            vs = [v for v in vs if v.is_valid and v.link_faces]
            bmesh.ops.recalc_face_normals(a.bm, faces=K.faces_of(vs))
            a._finish(vs, CORE)


def carve(o):
    """Cut the cracks into the built hero: an exact boolean difference whose new groove walls take the core's
    orange. The cutter is built in the same build coordinates as the hero, so it is placed by the hero's
    bottom-centre offset (found from a probe build)."""
    probe = flintkit.Asset("_probe", "probe")
    hero(probe)
    xs, ys, zs = ([v.co[i] for v in probe.bm.verts] for i in range(3))
    off = Vector(((min(xs) + max(xs)) / 2, (min(ys) + max(ys)) / 2, min(zs)))
    probe.bm.free()
    cut = flintkit.Asset("_crack_cutter", "probe")
    crack_cutter(cut)
    c = cut.finish(collection=o.users_collection[0], mark_asset=False, origin=None)
    c.matrix_world = o.matrix_world @ Matrix.Translation(-off)
    m = o.modifiers.new("Cracks", "BOOLEAN")
    m.operation, m.solver, m.object = "DIFFERENCE", "EXACT", c
    m.use_self = True
    m.material_mode = "TRANSFER"
    with M._override(o):
        bpy.ops.object.modifier_apply(modifier=m.name)
    me = c.data
    bpy.data.objects.remove(c, do_unlink=True)
    bpy.data.meshes.remove(me)


def impact_ring():
    """The impact rim: (x, y, w, d, h, seed) for pale rocks round the meteor's foot, bigger at the front."""
    rng = random.Random(9100)
    out = []
    n = 17
    for i in range(n):
        az = -90 + 360 * i / n + rng.uniform(-6, 6)
        front = max(0.0, -math.sin(math.radians(az)))
        s = rng.uniform(0.8, 1.15) * (1.0 + 0.45 * front)
        rad = 4.2 + rng.uniform(-0.2, 0.3) + 0.3 * front
        x = 0.3 + math.cos(math.radians(az)) * rad * 1.05
        y = 0.5 + math.sin(math.radians(az)) * rad * 0.95
        out.append((x, y, 1.9 * s, 1.6 * s, 1.0 * s, 9101 + i))
    # loose stones further out, as on the sheet's top view
    for i, az in enumerate((-20, 60, 150, 215, 290)):
        rad = 5.8 + rng.uniform(-0.2, 0.3)
        out.append((0.3 + math.cos(math.radians(az)) * rad, 0.5 + math.sin(math.radians(az)) * rad * 0.9,
                    1.3, 1.15, 0.8, 9130 + i))
    return out


def impact_rocks(a, which=None, at_origin=False):
    out = []
    for i, (x, y, w, d, h, seed) in enumerate(impact_ring()):
        if which is not None and i not in which:
            continue
        vs = K.hull_rock(a, (w, d, h), loc=(0, 0, 0) if at_origin else (x, y, 0), seed=seed, mat=IMPACT,
                         rings=ROCK_RINGS, jitter=0.07, rot=0.53 * (seed % 11), keep_bottom=True)
        K.blend(a, vs, IMPACT, IMPACT_COOL, K.noise_field(scale=0.4, seed=seed), level=0.15, width=0.4, steps=1)
        K.texture(a, vs, amp=0.04, scale=0.5, jitter=0.04, seed=seed)
        out += vs
    return out


def core_underside(o):
    """The floor cut's faces under the meteors take the core's orange, as on the sheet's underside view (the core
    shows through the open bottom of the shell)."""
    slot = next(i for i, m in enumerate(o.data.materials) if m.name == "FB_" + CORE)
    xs = [v.co.x for v in o.data.vertices]
    ys = [v.co.y for v in o.data.vertices]
    probe = flintkit.Asset("_probe", "probe")
    hero(probe)
    pxs, pys = [v.co.x for v in probe.bm.verts], [v.co.y for v in probe.bm.verts]
    probe.bm.free()
    # build coords -> object coords (the bottom-centre shift in x and y)
    dx = (min(pxs) + max(pxs)) / 2 - (min(xs) + max(xs)) / 2
    dy = (min(pys) + max(pys)) / 2 - (min(ys) + max(ys)) / 2
    for p in o.data.polygons:
        if p.normal.z > -0.99:
            continue
        c = p.center
        for _, centre, radii, _, _, _ in METEORS:
            u, v = (c.x + dx - centre[0]) / radii[0], (c.y + dy - centre[1]) / radii[1]
            if u * u + v * v < 0.95 ** 2:
                p.material_index = slot


def hero(a):
    for m in METEORS:
        shell(a, m[0])
    impact_rocks(a)


NOTES = {
    "IronMeteorDeposit": "iron meteorite deposit: a big dark faceted meteor with jagged cracks glowing orange where "
                         "the metal core shows through, a smaller cracked lobe at its front left, and a ring of pale "
                         "impact rocks round the foot with a few loose stones further out; cracks glow",
    "IronMeteorShellPiece": "Rock Shell Piece (reusable, 4-5 per meteor): dark faceted wedge of the meteor's shell "
                            "with orange inner (seam) faces",
    "IronMeteorCore": "Metal Core: faceted glowing orange ball that fills the seams between the shell pieces",
    "IronMeteorImpactRock": "Impact Rock (reusable): pale faceted stone of the impact rim",
}


def build(render=True):
    M.coll(NUM, TITLE)
    palette()
    main_c = METEORS[0][1]
    fx = [("heat_glow", main_c, {"scale": 2.2}), ("embers", (main_c[0], main_c[1], 6.2), {})]
    specs = [("IronMeteorDeposit", "hero", hero, 4000, "hull", fx),
             ("IronMeteorShellPiece", "part", lambda a: shell_piece(a, "Main", 1), 1000, "hull", ()),
             ("IronMeteorCore", "part", lambda a: core(a, "Main", True), 1000, "hull", ()),
             ("IronMeteorImpactRock", "part", lambda a: impact_rocks(a, (0,), True), 1000, "hull", ())]
    objs = [M.mk(SHEET, n, fn, subject=TITLE, role=r, notes=NOTES[n], budget=b, collision=c, fx=f)
            for n, r, fn, b, c, f in specs]
    audits = []
    for o in objs:
        if o.get("kit_role") == "hero":
            carve(o)
            M.union_loose(o)
            m004.floor_cut(o)
            core_underside(o)
        audits.append(M.finish(o, union=False))
    M.display(NUM, objs, TITLE)
    out = {"audit": audits, "problems": K.check(objs)}
    if render:
        hero_o, shell_o, core_o, rock_o = objs
        saved = M.explode(objs[1:], {})
        try:
            hx, hy = hero_o.location.x, hero_o.location.y
            shell_o.location = (hx + 40 - 4.5, hy, 2.5)
            core_o.location = (hx + 40 + 1.0, hy, 1.0)
            rock_o.location = (hx + 40 + 5.5, hy - 1.0, 0)
            out["views"] = M.views(NUM, [hero_o], extra={"exploded": (objs[1:], -14, 12)})
        finally:
            M.restore(saved)
            M.display(NUM, objs, TITLE)
    return out
