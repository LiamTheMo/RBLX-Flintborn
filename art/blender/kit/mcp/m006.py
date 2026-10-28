"""006 Copper (references/006.png): a pale stone host rock with chunky bright copper inserts standing proud of it,
teal oxidation on the inserts and smudged onto the host around them, and two base rocks.

    import importlib, m006; importlib.reload(m006); m006.build()

Parts as on the sheet: Host Rock (main chunk), Copper Insert A (large), B (medium), C (small), Base Rock A (left),
Base Rock B (right). The hero is their union.
"""
import math
import random

import bmesh
from mathutils import Vector
from mathutils.bvhtree import BVHTree

import flintkit
import kit_mcp as K
import kit_models as M

NUM, TITLE, SHEET = 6, "Copper", "M006"
HOST, HOST_COOL, COPPER, OXIDE, BASE = "m006_stone", "m006_stone_cool", "m006_copper", "m006_oxidation", "m006_base_rock"

HOST_RINGS = [(0.0, 0.9, 10), (0.2, 1.0, 12), (0.45, 0.98, 12), (0.68, 0.88, 11), (0.86, 0.66, 9), (1.0, 0.36, 6)]
HOST_SIZE = (7.0, 6.4, 5.8)
# inserts: (label, azimuth deg (-90 = front), height frac, radius, seed); A/B/C are the reusable parts, the hero
# repeats them round the host as on the sheet's front, rear and top views
INSERTS = (("A", -40, 0.48, 1.35, 6011), ("B", -125, 0.36, 1.1, 6012), ("C", -110, 0.86, 0.85, 6013),
           ("B", 150, 0.42, 1.0, 6014), ("C", 60, 0.78, 0.8, 6015), ("A", 95, 0.2, 1.05, 6016))
BASE_ROCKS = (("A", -3.4, -1.5, 2.2, 1.9, 1.3, 6031), ("B", 3.3, -1.6, 2.0, 1.8, 1.2, 6032))
BASE_RINGS = [(0.0, 0.92, 6), (0.4, 1.0, 6), (0.75, 0.7, 5), (1.0, 0.25, 3)]


def palette():
    K.set_colour(HOST, "#958274", rough=0.92)        # measured against the sheet host render #978679
    K.set_colour(HOST_COOL, "#8C7E78", rough=0.92)
    K.set_colour(COPPER, "#D45A1E", rough=0.55, metal=0.2)
    K.set_colour(OXIDE, "#3F8B80", rough=0.8)
    K.set_colour(BASE, "#958C8B", rough=0.92)


def host_tree():
    t = flintkit.Asset("_probe", "probe")
    K.hull_rock(t, HOST_SIZE, seed=6001, mat=HOST, rings=HOST_RINGS, jitter=0.05, rot=0.3, keep_bottom=True)
    t.bm.faces.ensure_lookup_table()
    return t, BVHTree.FromBMesh(t.bm)


def seats():
    t, tree = host_tree()
    out = []
    for label, az, hf, R, seed in INSERTS:
        a = math.radians(az)
        d = Vector((math.cos(a), math.sin(a), 0))
        hit = tree.ray_cast(Vector((0, 0, HOST_SIZE[2] * hf)) + d * 20, -d, 60)
        out.append((label, hit[0], (hit[1] + Vector((0, 0, 0.2))).normalized(), R, seed))
    t.bm.free()
    return out


def host(a, oxide=True):
    vs = K.hull_rock(a, HOST_SIZE, seed=6001, mat=HOST, rings=HOST_RINGS, jitter=0.05, rot=0.3, keep_bottom=True)
    K.blend(a, vs, HOST, HOST_COOL, K.noise_field(scale=0.22, seed=6001), level=0.15, width=0.45, steps=2)
    if oxide:
        # teal oxidation smudged onto the host round each insert (a real colour region): the big facets are split
        # into coplanar pieces first (silhouette unchanged) so the smudges stay small; a stone/teal half-mix ring
        # softens their edge
        K.tag_part(a, vs, "host")
        vs = K.refine(a, K.part(a, "host"), 1)
        pts = [(p, R) for _, p, n, R, _ in seats()]
        nf = K.noise_field(scale=1.2, seed=6002)

        def field(c):
            return max(1.0 - (c - p).length / (R * 1.35) for p, R in pts) + nf(c) * 0.35
        K.blend(a, vs, HOST, OXIDE, field, level=0.35, width=0.3, mode="half")
    K.texture(a, vs, amp=0.04, scale=0.3, jitter=0.035, seed=6001)
    return vs


def insert(a, base, normal, R, seed):
    """One copper insert: a chunky faceted nugget (about 16 broad facets), sunk a third into the host so it sits
    proud with a clear contact edge; teal oxidation on some facets."""
    rng = random.Random(seed)
    n = Vector(normal).normalized()
    u = n.orthogonal().normalized()
    w = n.cross(u)
    c = Vector(base) + n * R * 0.25
    pts = []
    N = 18
    for k in range(N):
        # evenly spread points (Fibonacci sphere) on a slightly lumpy ellipsoid, longer across the surface than out
        # of it: a chunky nugget with broad facets of similar size, as the sheet's insert detail
        zz = 1 - 2 * (k + 0.5) / N
        r = math.sqrt(1 - zz * zz)
        th = k * 2.39996 + rng.uniform(-0.15, 0.15)
        v = u * math.cos(th) * r * 1.15 + w * math.sin(th) * r * 0.95 + n * zz * 0.8
        pts.append(c + v * R * rng.uniform(0.9, 1.04))
    bm = a.bm
    vs = [bm.verts.new(p) for p in pts]
    bmesh.ops.convex_hull(bm, input=vs)
    vs = [v for v in vs if v.is_valid and v.link_faces]
    bmesh.ops.recalc_face_normals(bm, faces=K.faces_of(vs))
    a._finish(vs, COPPER)
    nf = K.noise_field(scale=1.1, seed=seed)
    oi = a._mi(OXIDE)
    for f in K.faces_of(vs):
        if nf(f.calc_center_median()) > 0.22:
            f.material_index = oi
    K.texture(a, vs, amp=0.04, scale=0.8, jitter=0.03, seed=seed)
    return vs


def inserts(a, label=None, at_origin=False):
    out = []
    for lab, p, n, R, seed in seats():
        if label is not None:
            if lab != label:
                continue
            if at_origin:
                return insert(a, Vector((0, 0, R * 0.55)), Vector((0, 0, 1)), R, seed)
        out += insert(a, p, n, R, seed)
    return out


def base_rock(a, label=None, at_origin=False):
    vs = []
    for lab, x, y, w, d, h, seed in BASE_ROCKS:
        if label is not None and lab != label:
            continue
        v = K.hull_rock(a, (w, d, h), loc=(0, 0, 0) if at_origin else (x, y, 0), seed=seed, mat=BASE,
                        rings=BASE_RINGS, jitter=0.06, rot=0.6, keep_bottom=True)
        K.texture(a, v, amp=0.04, scale=0.5, jitter=0.04, seed=seed)
        vs += v
    return vs


def hero(a):
    host(a)
    inserts(a)
    base_rock(a)


NOTES = {
    "Copper": "copper resource: pale stone host rock with six chunky bright copper inserts standing proud (three "
              "sizes, round the rock), teal oxidation on the inserts and smudged onto the host round them, and two "
              "grey base rocks; one closed mesh",
    "CopperHostRock": "Host Rock (main chunk): pale faceted dome with teal oxidation where the inserts sit",
    "CopperInsertA": "Copper Insert A (large): chunky faceted copper nugget with teal oxidation facets",
    "CopperInsertB": "Copper Insert B (medium)",
    "CopperInsertC": "Copper Insert C (small)",
    "CopperBaseRockA": "Base Rock A (left): small grey faceted rock",
    "CopperBaseRockB": "Base Rock B (right): small grey faceted rock",
}


def build(render=True):
    M.coll(NUM, TITLE)
    palette()
    specs = [("Copper", "hero", hero, 4000, "hull"),
             ("CopperHostRock", "part", host, 1000, "hull"),
             ("CopperInsertA", "part", lambda a: inserts(a, "A", True), 1000, "hull"),
             ("CopperInsertB", "part", lambda a: inserts(a, "B", True), 1000, "hull"),
             ("CopperInsertC", "part", lambda a: inserts(a, "C", True), 1000, "hull"),
             ("CopperBaseRockA", "part", lambda a: base_rock(a, "A", True), 1000, "hull"),
             ("CopperBaseRockB", "part", lambda a: base_rock(a, "B", True), 1000, "hull")]
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
            host_o.location = (hx + 40, hy, 1.6)
            for i, o in enumerate(objs[2:5]):
                o.location = (hx + 40 + (-5.0, -5.5, 5.5)[i], hy - 1.5, (6.5, 3.0, 4.5)[i])
            objs[5].location = (hx + 40 - 3.6, hy - 2.6, 0)
            objs[6].location = (hx + 40 + 3.6, hy - 2.6, 0)
            out["views"] = M.views(NUM, [hero_o], extra={"exploded": (parts, -14, 12)})
        finally:
            M.restore(saved)
            M.display(NUM, objs, TITLE)
    return out
