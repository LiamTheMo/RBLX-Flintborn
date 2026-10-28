"""010 Gold (references/010.png): a tall brown faceted host rock with chunky bright-yellow gold nuggets standing
proud of it in shallow seats, and small grey base rocks round its foot.

    import importlib, m010; importlib.reload(m010); m010.build()

Parts as on the sheet: Host Rock, Gold Nugget (Large), (Medium), (Small), Base Rock (Small, reusable). The hero is
their union. Built like 006 Copper (nuggets seated by ray casts onto the host). The R02 kit sheet owns
`GoldHostRock` and `GoldBaseRock`, so those parts are `GoldHost` and `GoldRockSmall`.
"""
import math
import random

import bmesh
from mathutils import Vector
from mathutils.bvhtree import BVHTree

import flintkit
import kit_mcp as K
import kit_models as M

NUM, TITLE, SHEET = 10, "Gold", "M010"
HOST, HOST_DARK, GOLD, GOLD_DEEP, BASE = "m010_host", "m010_host_dark", "m010_gold", "m010_gold_deep", "m010_base"

# a lumpy dome nearly as tall as it is wide: full shoulders narrowing to a peaked, faceted crown
HOST_RINGS = [(0.0, 0.9, 12), (0.16, 1.0, 14), (0.36, 0.98, 14), (0.56, 0.88, 13), (0.74, 0.7, 11),
              (0.88, 0.46, 8), (1.0, 0.16, 4)]
HOST_SIZE = (8.6, 7.6, 7.6)
# nuggets: (label, azimuth deg (-90 = front), height frac, radius, seed); L/M/S are the reusable parts
NUGGETS = (("L", -72, 0.4, 1.75, 10011), ("M", -138, 0.5, 1.4, 10012), ("S", -28, 0.78, 1.15, 10013),
           ("M", 122, 0.55, 1.3, 10014), ("S", 32, 0.62, 1.1, 10015), ("M", 72, 0.26, 1.25, 10016))
BASE_ROCKS = ((-3.5, -2.3, 2.9, 2.4, 1.8, 10031), (3.5, -2.4, 2.7, 2.3, 1.7, 10032),
              (-3.0, 2.3, 1.9, 1.7, 1.1, 10033), (3.2, 2.1, 2.0, 1.8, 1.2, 10034))
BASE_RINGS = [(0.0, 0.92, 6), (0.4, 1.0, 6), (0.75, 0.7, 5), (1.0, 0.25, 3)]


def palette():
    # sheet swatches: host #9F7C68, gold #F7CC3A, dark #76605A; the host is set halfway to the darker sheet render
    # (#AA836C lit crown against our #D49F7F)
    K.set_colour(HOST, "#8F705F", rough=0.92)
    K.set_colour(HOST_DARK, "#806456", rough=0.92)
    K.set_colour(GOLD, "#F7CC3A", rough=0.45, metal=0.3)
    K.set_colour(GOLD_DEEP, "#EBB72A", rough=0.45, metal=0.3)
    K.set_colour(BASE, "#9A8A82", rough=0.92)


def host_tree():
    t = flintkit.Asset("_probe", "probe")
    K.hull_rock(t, HOST_SIZE, seed=10001, mat=HOST, rings=HOST_RINGS, jitter=0.11, rot=0.4, keep_bottom=True)
    t.bm.faces.ensure_lookup_table()
    return t, BVHTree.FromBMesh(t.bm)


def seats():
    t, tree = host_tree()
    out = []
    for label, az, hf, R, seed in NUGGETS:
        a = math.radians(az)
        d = Vector((math.cos(a), math.sin(a), 0))
        hit = tree.ray_cast(Vector((0, 0, HOST_SIZE[2] * hf)) + d * 20, -d, 60)
        out.append((label, hit[0], (hit[1] + Vector((0, 0, 0.15))).normalized(), R, seed))
    t.bm.free()
    return out


def host(a):
    vs = K.hull_rock(a, HOST_SIZE, seed=10001, mat=HOST, rings=HOST_RINGS, jitter=0.11, rot=0.4, keep_bottom=True)
    K.blend(a, vs, HOST, HOST_DARK, K.noise_field(scale=0.22, seed=10001), level=0.15, width=0.45, steps=2)
    K.texture(a, vs, amp=0.04, scale=0.3, jitter=0.035, seed=10001)
    return vs


def nugget(a, base, normal, R, seed):
    """One gold nugget: a chunky faceted lump (about 14 broad facets), much wider across the surface than out of
    it, sunk into the host so it sits proud of its seat with a broad flattish face; a few facets in the deeper
    gold."""
    rng = random.Random(seed)
    n = Vector(normal).normalized()
    u = n.orthogonal().normalized()
    w = n.cross(u)
    c = Vector(base) + n * R * 0.2
    pts = []
    N = 14
    for k in range(N):
        zz = 1 - 2 * (k + 0.5) / N
        r = math.sqrt(1 - zz * zz)
        th = k * 2.39996 + rng.uniform(-0.15, 0.15)
        v = u * math.cos(th) * r * 1.12 + w * math.sin(th) * r * 1.0 + n * zz * 0.62
        pts.append(c + v * R * rng.uniform(0.8, 1.12))      # irregular, cut-crystal-like lump
    bm = a.bm
    vs = [bm.verts.new(p) for p in pts]
    bmesh.ops.convex_hull(bm, input=vs)
    vs = [v for v in vs if v.is_valid and v.link_faces]
    bmesh.ops.recalc_face_normals(bm, faces=K.faces_of(vs))
    a._finish(vs, GOLD)
    nf = K.noise_field(scale=1.0, seed=seed)
    di = a._mi(GOLD_DEEP)
    for f in K.faces_of(vs):
        if nf(f.calc_center_median()) > 0.25:
            f.material_index = di
    K.texture(a, vs, amp=0.03, scale=0.8, jitter=0.03, seed=seed)
    return vs


def nuggets(a, label=None, at_origin=False):
    out = []
    for lab, p, n, R, seed in seats():
        if label is not None:
            if lab != label:
                continue
            if at_origin:
                return nugget(a, Vector((0, 0, R * 0.55)), Vector((0, 0, 1)), R, seed)
        out += nugget(a, p, n, R, seed)
    return out


def base_rocks(a, which=None, at_origin=False):
    vs = []
    for i, (x, y, w, d, h, seed) in enumerate(BASE_ROCKS):
        if which is not None and i not in which:
            continue
        v = K.hull_rock(a, (w, d, h), loc=(0, 0, 0) if at_origin else (x, y, 0), seed=seed, mat=BASE,
                        rings=BASE_RINGS, jitter=0.06, rot=0.6 * i, keep_bottom=True)
        K.texture(a, v, amp=0.04, scale=0.5, jitter=0.04, seed=seed)
        vs += v
    return vs


def hero(a):
    host(a)
    nuggets(a)
    base_rocks(a)


NOTES = {
    "Gold": "gold resource: tall brown faceted host rock with six chunky bright-yellow gold nuggets standing proud "
            "in shallow seats (three sizes, round the rock) and four small grey base rocks round the foot; one "
            "closed mesh",
    "GoldHost": "Host Rock: tall brown faceted dome, flat bottom",
    "GoldNuggetLarge": "Gold Nugget (Large): chunky faceted bright-yellow nugget",
    "GoldNuggetMedium": "Gold Nugget (Medium)",
    "GoldNuggetSmall": "Gold Nugget (Small)",
    "GoldRockSmall": "Base Rock (Small, reusable): small grey faceted rock",
}


def build(render=True):
    M.coll(NUM, TITLE)
    palette()
    specs = [("Gold", "hero", hero, 4000, "hull"),
             ("GoldHost", "part", host, 1000, "hull"),
             ("GoldNuggetLarge", "part", lambda a: nuggets(a, "L", True), 1000, "hull"),
             ("GoldNuggetMedium", "part", lambda a: nuggets(a, "M", True), 1000, "hull"),
             ("GoldNuggetSmall", "part", lambda a: nuggets(a, "S", True), 1000, "hull"),
             ("GoldRockSmall", "part", lambda a: base_rocks(a, (0,), True), 1000, "hull")]
    objs = [M.mk(SHEET, n, fn, subject=TITLE, role=r, notes=NOTES[n], budget=b, collision=c)
            for n, r, fn, b, c in specs]
    audits = [M.finish(o, union=o.get("kit_role") == "hero") for o in objs]
    M.display(NUM, objs, TITLE)
    out = {"audit": audits, "problems": K.check(objs)}
    if render:
        hero_o, host_o = objs[0], objs[1]
        parts = objs[1:]
        saved = M.explode(parts, {})
        try:
            hx, hy = hero_o.location.x, hero_o.location.y
            host_o.location = (hx + 40, hy, 1.0)
            for i, o in enumerate(objs[2:5]):
                o.location = (hx + 40 + (-6.0, 6.0, 5.5)[i], hy - 1.5, (5.5, 4.0, 7.5)[i])
            objs[5].location = (hx + 40 - 3.0, hy - 4.0, 0)
            out["views"] = M.views(NUM, [hero_o], extra={"exploded": (parts, -14, 12)})
        finally:
            M.restore(saved)
            M.display(NUM, objs, TITLE)
    return out
