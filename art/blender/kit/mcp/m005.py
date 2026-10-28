"""005 Quartz (references/005.png): a cave-crystal cluster: one large quartz crystal and four side crystals fanning
out of a mound of rounded faceted base rocks.

    import importlib, m005; importlib.reload(m005); m005.build()

Parts as on the sheet: Main Crystal (reusable), Side Crystal (reusable), Base Rock. The hero is their union.
"""
import math
import random

import bmesh
from mathutils import Matrix, Vector

import kit_mcp as K
import kit_models as M
import m004

NUM, TITLE, SHEET = 5, "Quartz", "M005"
MAIN, SIDE, ROCK, ROCK_COOL = "m005_crystal", "m005_crystal_side", "m005_rock", "m005_rock_cool"

# crystals: (label, x, y, radius, height, lean x, lean y, twist, seed, base z)
CRYSTALS = (("Main", 0.2, 0.6, 2.25, 9.0, 0.0, 0.06, 0.0, 5011, 1.7),
            ("SideL", -2.7, 0.2, 1.45, 6.0, -0.42, 0.0, 0.4, 5012, 1.4),
            ("SideR", 2.9, 0.3, 1.4, 5.6, 0.42, 0.04, -0.3, 5013, 1.4),
            ("SideFL", -2.0, -1.9, 1.15, 4.4, -0.3, -0.35, 0.2, 5014, 1.2),
            ("SideFR", 2.4, -1.8, 1.1, 4.2, 0.35, -0.3, 0.7, 5015, 1.2))
ROCKS = ((0.0, 0.3, 4.8, 4.2, 2.9, 5031), (-3.0, -0.4, 3.4, 3.0, 2.3, 5032), (3.1, -0.3, 3.2, 2.9, 2.2, 5033),
         (-1.0, -2.6, 3.2, 2.7, 2.1, 5034), (1.7, -2.6, 3.0, 2.6, 1.9, 5035), (-0.6, 2.8, 3.0, 2.6, 2.0, 5036),
         (2.3, 2.2, 2.6, 2.3, 1.8, 5037), (-2.8, 2.0, 2.5, 2.2, 1.7, 5038), (-4.2, -2.0, 1.6, 1.4, 1.1, 5039),
         (4.2, -1.9, 1.5, 1.4, 1.0, 5040))
ROCK_RINGS = [(0.0, 0.9, 7), (0.35, 1.0, 7), (0.7, 0.78, 6), (1.0, 0.36, 4)]


def palette():
    K.set_colour(MAIN, "#E6D8CD", rough=0.45)        # toward the sheet swatch #F1E1D4
    K.set_colour(SIDE, "#B9ABA4", rough=0.45)
    K.set_colour(ROCK, "#7E716D", rough=0.92)        # the sheet swatch is #7A6E6B
    K.set_colour(ROCK_COOL, "#776E6E", rough=0.92)


def crystal(a, label, origin=None):
    """One quartz crystal: a six-sided prism (slightly uneven widths) with a short flat-bottomed root and a
    six-faced pyramidal cap to a point; broad simple facets. Some prism faces carry the darker side tone
    (broad patches by noise, not by facing)."""
    _, x, y, R, H, lx, ly, tw, seed, z0 = next(c for c in CRYSTALS if c[0] == label)
    rng = random.Random(seed)
    if origin is not None:
        x, y, lx, ly, z0 = origin[0], origin[1], 0.0, 0.0, 1.2
    base = Vector((x, y, z0 - 1.2))
    axis = Vector((lx, ly, 1.0)).normalized()
    m = Matrix.Rotation(math.acos(max(-1.0, min(1.0, axis.z))), 3,
                        Vector((-axis.y, axis.x, 0)).normalized() if abs(axis.z) < 0.9999 else Vector((1, 0, 0)))
    m = m @ Matrix.Rotation(tw, 3, "Z")
    radii = [R * rng.uniform(0.88, 1.08) for _ in range(6)]
    pts = []
    for h, f in ((0.0, 0.8), (0.12, 1.0), (0.7, 1.0)):
        for k in range(6):
            t = 2 * math.pi * k / 6
            pts.append(base + m @ Vector((math.cos(t) * radii[k] * f, math.sin(t) * radii[k] * f * 0.9, H * h)))
    pts.append(base + m @ Vector((R * 0.06, 0.0, H)))
    bm = a.bm
    vs = [bm.verts.new(p) for p in pts]
    bmesh.ops.convex_hull(bm, input=vs)
    vs = [v for v in vs if v.is_valid and v.link_faces]
    bmesh.ops.recalc_face_normals(bm, faces=K.faces_of(vs))
    a._finish(vs, MAIN)
    nf = K.noise_field(scale=0.35, seed=seed)
    si = a._mi(SIDE)
    for f in K.faces_of(vs):
        if nf(f.calc_center_median()) > 0.1:
            f.material_index = si
    K.texture(a, vs, amp=0.03, scale=0.5, jitter=0.025, seed=seed)
    return vs


def rocks(a):
    out = []
    for x, y, w, d, h, seed in ROCKS:
        vs = K.hull_rock(a, (w, d, h), loc=(x, y, 0), seed=seed, mat=ROCK, rings=ROCK_RINGS, jitter=0.06,
                         rot=0.37 * seed % 3.0, keep_bottom=True)
        K.blend(a, vs, ROCK, ROCK_COOL, K.noise_field(scale=0.3, seed=seed), level=0.15, width=0.4, steps=1)
        K.texture(a, vs, amp=0.04, scale=0.4, jitter=0.04, seed=seed)
        out += vs
    return out


def hero(a):
    rocks(a)
    for c in CRYSTALS:
        crystal(a, c[0])


NOTES = {
    "Quartz": "quartz cave crystal: one large pale hexagonal crystal with a pointed cap and four smaller side crystals "
              "fanning out of a mound of rounded dark faceted base rocks; one closed mesh",
    "QuartzMainCrystal": "Main Crystal (reusable): large six-sided prism with a pyramidal cap, flat root",
    "QuartzSideCrystal": "Side Crystal (reusable): smaller six-sided crystal, flat root",
    "QuartzBaseRock": "Base Rock: mound of rounded faceted dark rocks, flat bottom",
}


def build(render=True):
    M.coll(NUM, TITLE)
    palette()
    specs = [("Quartz", "hero", hero, 4000, "hull"),
             ("QuartzMainCrystal", "part", lambda a: crystal(a, "Main", origin=(0, 0)), 1000, "hull"),
             ("QuartzSideCrystal", "part", lambda a: crystal(a, "SideL", origin=(0, 0)), 1000, "hull"),
             ("QuartzBaseRock", "part", rocks, 1000, "hull")]
    objs = [M.mk(SHEET, n, fn, subject=TITLE, role=r, notes=NOTES[n], budget=b, collision=c)
            for n, r, fn, b, c in specs]
    audits = []
    for o in objs:
        if o.get("kit_role") == "hero":
            M.union_loose(o)
            m004.floor_cut(o)
        audits.append(M.finish(o, union=False))
    M.display(NUM, objs, TITLE)
    out = {"audit": audits, "problems": K.check(objs)}
    if render:
        hero_o, main_o, side_o, rock_o = objs
        saved = M.explode(objs[1:], {})
        try:
            hx, hy = hero_o.location.x, hero_o.location.y
            main_o.location = (hx + 40, hy + 0.6, 4.5)
            side_o.location = (hx + 40 + 4.5, hy, 3.5)
            rock_o.location = (hx + 40, hy, 0)
            out["views"] = M.views(NUM, [hero_o], extra={"exploded": ([main_o, side_o, rock_o], -14, 12)})
        finally:
            M.restore(saved)
            M.display(NUM, objs, TITLE)
    return out
