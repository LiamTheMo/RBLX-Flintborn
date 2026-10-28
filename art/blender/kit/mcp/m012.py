"""012 Amber (references/012.png): a big egg-shaped faceted amber nodule nestled in weathered wood: long splintered
beams lying across its front and back, and upright splinters standing at its sides and rear.

    import importlib, m012; importlib.reload(m012); m012.build()

Parts as on the sheet: Amber Nodule (main crystal), Wood Base (Front), Wood Base (Rear), Side Wood (Left), Side Wood
(Right). The hero is their union. The R03 kit sheet owns `AmberNodule`, so the nodule part is `AmberCrystalMain`.
"""
import math
import random

import bmesh
from mathutils import Vector

import kit_mcp as K
import kit_models as M
import m004

NUM, TITLE, SHEET = 12, "Amber", "M012"
A_LIGHT, A_MID, A_DARK = "m012_amber_light", "m012_amber_mid", "m012_amber_dark"
WOOD, WOOD_DARK, WOOD_LIGHT = "m012_wood", "m012_wood_dark", "m012_wood_light"

NODULE = ((0.0, 0.3, 3.5), (2.7, 2.4, 3.6), 12001)        # centre, radii, seed: sunk 0.1 into the ground
# wood groups: beams (p0, p1, width, depth, taper, seed); each group is one part on the sheet
WOOD_GROUPS = {
    "BaseFront": (((-4.6, -2.0, 0.6), (4.0, -3.0, 1.6), 2.8, 2.0, 0.9, 12011),     # the thick, sloped front log
                  ((-3.4, -1.2, 2.1), (2.6, -1.7, 2.3), 1.9, 1.3, 0.9, 12012),
                  ((-4.5, -2.9, 0.7), (-2.7, -3.4, 1.2), 2.0, 1.6, 1.0, 12013)),
    "BaseRear": (((-2.6, 2.0, 0.8), (2.8, 2.5, 0.9), 2.2, 1.6, 1.0, 12021),
                 ((-1.6, 2.6, 1.9), (1.9, 2.9, 2.0), 1.7, 1.2, 0.9, 12022)),
    # upright splintered planks: broad, chunky slabs (width across the plank's face), leaning outward, tapering
    # to an angled top
    "SideLeft": (((-3.0, 0.0, 0.0), (-3.7, -0.3, 4.4), 2.6, 1.5, 0.5, 12031),
                 ((-3.4, -1.4, 0.0), (-3.8, -1.6, 2.4), 2.2, 1.5, 0.6, 12033)),
    "SideRight": (((2.5, -0.4, 0.0), (3.3, -0.6, 4.2), 2.6, 1.5, 0.5, 12041),),
    "Rear": (((1.4, 2.4, 0.0), (1.9, 2.8, 6.2), 1.7, 3.0, 0.5, 12051),
             ((-0.6, 2.7, 0.0), (-0.9, 3.0, 4.0), 1.5, 2.6, 0.55, 12053)),
}


def palette():
    # sheet swatches: amber light #FECD64, mid #FE7719, dark #D25117; wood #8D5D3D
    K.set_colour(A_LIGHT, "#FECD64", rough=0.3)
    K.set_colour(A_MID, "#FE7719", rough=0.3)
    K.set_colour(A_DARK, "#D25117", rough=0.3)
    K.set_colour(WOOD, "#8D5D3D", rough=0.9)
    K.set_colour(WOOD_DARK, "#84563A", rough=0.9)
    K.set_colour(WOOD_LIGHT, "#9C6845", rough=0.9)


def nodule(a, at_origin=False):
    """The amber nodule: an egg of about 40 broad facets; three ambers as broad facet regions (by noise)."""
    centre, radii, seed = NODULE
    if at_origin:
        centre = (0.0, 0.0, radii[2])
    rng = random.Random(seed)
    c = Vector(centre)
    pts = []
    n = 40
    for k in range(n):
        z = 1 - 2 * (k + 0.5) / n
        r = math.sqrt(1 - z * z) * (1.0 - 0.12 * z)          # a little fuller below the middle: an egg
        th = k * 2.39996 + rng.uniform(-0.12, 0.12)
        s = rng.uniform(0.95, 1.04)
        pts.append(c + Vector((math.cos(th) * r * radii[0], math.sin(th) * r * radii[1], z * radii[2])) * s)
    vs = [a.bm.verts.new(p) for p in pts]
    bmesh.ops.convex_hull(a.bm, input=vs)
    vs = [v for v in vs if v.is_valid and v.link_faces]
    bmesh.ops.recalc_face_normals(a.bm, faces=K.faces_of(vs))
    a._finish(vs, A_MID)
    nf = K.noise_field(scale=0.45, seed=seed)
    li, di = a._mi(A_LIGHT), a._mi(A_DARK)
    for f in K.faces_of(vs):
        v = nf(f.calc_center_median())
        if v > 0.22:                                     # mostly the mid amber, as on the sheet
            f.material_index = li
        elif v < -0.25:
            f.material_index = di
    return vs


def beam(a, p0, p1, w, d, taper, seed):
    """One weathered wood piece: a five-sided beam from p0 to p1 with uneven sides, splintered (unevenly cut) ends,
    tapering to `taper` of its width at p1 (upright splinters taper to a point-ish top)."""
    rng = random.Random(seed)
    p0, p1 = Vector(p0), Vector(p1)
    ax = (p1 - p0).normalized()
    u = ax.cross(Vector((0, 0, 1)) if abs(ax.z) < 0.9 else Vector((1, 0, 0))).normalized()
    v = ax.cross(u)
    radii = [rng.uniform(0.82, 1.08) for _ in range(5)]
    pts = []
    for end, sc in ((p0, 1.0), (p1, taper)):
        for k in range(5):
            t = 2 * math.pi * k / 5 + 0.3
            q = u * math.cos(t) * w / 2 * radii[k] * sc + v * math.sin(t) * d / 2 * radii[k] * sc
            pts.append(end + q + ax * rng.uniform(-0.25, 0.25))
    vs = [a.bm.verts.new(p) for p in pts]
    bmesh.ops.convex_hull(a.bm, input=vs)
    vs = [v for v in vs if v.is_valid and v.link_faces]
    bmesh.ops.recalc_face_normals(a.bm, faces=K.faces_of(vs))
    a._finish(vs, WOOD)
    nf = K.noise_field(scale=0.5, seed=seed)
    li, di = a._mi(WOOD_LIGHT), a._mi(WOOD_DARK)
    for f in K.faces_of(vs):
        x = nf(f.calc_center_median())
        if x > 0.3:
            f.material_index = li
        elif x < -0.3:
            f.material_index = di
    K.texture(a, vs, amp=0.04, scale=0.6, jitter=0.03, seed=seed)
    return vs


def woods(a, group, at_origin=False):
    out = []
    beams = WOOD_GROUPS[group]
    shift = Vector((0, 0, 0))
    if at_origin:
        shift = -Vector((sum(b[0][0] + b[1][0] for b in beams) / (2 * len(beams)),
                         sum(b[0][1] + b[1][1] for b in beams) / (2 * len(beams)), 0))
    for p0, p1, w, d, taper, seed in beams:
        out += beam(a, Vector(p0) + shift, Vector(p1) + shift, w, d, taper, seed)
    return out


def hero(a):
    nodule(a)
    for g in WOOD_GROUPS:
        woods(a, g)


NOTES = {
    "Amber": "amber resource: a big egg-shaped faceted amber nodule (three ambers as broad facet regions) nestled in "
             "weathered wood - splintered beams lying across its front and back, upright splinters at its sides "
             "and rear; one closed mesh, flat bottom",
    "AmberCrystalMain": "Amber Nodule (main crystal): faceted amber egg",
    "AmberWoodFront": "Wood Base (Front): two stacked splintered beams and an end block",
    "AmberWoodBack": "Wood Base (Rear): two stacked splintered beams",
    "AmberWoodLeft": "Side Wood (Left): two broad upright splintered planks",
    "AmberWoodRight": "Side Wood (Right): a broad upright splintered plank",
}


def build(render=True):
    M.coll(NUM, TITLE)
    palette()
    specs = [("Amber", "hero", hero, 4000, "hull"),
             ("AmberCrystalMain", "part", lambda a: nodule(a, True), 1000, "hull"),
             ("AmberWoodFront", "part", lambda a: woods(a, "BaseFront", True), 1000, "hull"),
             ("AmberWoodBack", "part", lambda a: woods(a, "BaseRear", True), 1000, "hull"),
             ("AmberWoodLeft", "part", lambda a: woods(a, "SideLeft", True), 1000, "hull"),
             ("AmberWoodRight", "part", lambda a: woods(a, "SideRight", True), 1000, "hull")]
    objs = [M.mk(SHEET, n, fn, subject=TITLE, role=r, notes=NOTES[n], budget=b, collision=c)
            for n, r, fn, b, c in specs]
    audits = []
    for o, (_, _, fn, _, _) in zip(objs, specs):
        M.union_loose(o)
        m004.floor_cut(o, z0=-M._build_offset(fn).z)    # the ground (build z = 0) in object coordinates
        audits.append(M.finish(o, union=False))
    M.display(NUM, objs, TITLE)
    out = {"audit": audits, "problems": K.check(objs)}
    if render:
        hero_o, parts = objs[0], objs[1:]
        saved = M.explode(parts, {})
        try:
            hx, hy = hero_o.location.x, hero_o.location.y
            for o, (dx, dy, z) in zip(parts, ((0, 0, 3.0), (0, -6, 0), (0, 5, 0), (-7, 0, 0), (7, 0, 0))):
                o.location = (hx + 40 + dx, hy + dy, z)
            out["views"] = M.views(NUM, [hero_o], extra={"exploded": (parts, -16, 14)})
        finally:
            M.restore(saved)
            M.display(NUM, objs, TITLE)
    return out
