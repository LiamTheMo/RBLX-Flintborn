"""003 Iron (references/003.png): a grey host rock with thick steel iron chunks seated on flat facets, each
chunk ringed by a rust-orange depleted edge, and base rocks round the foot. No bevels.

    import importlib, m003; importlib.reload(m003); m003.build()

Parts as on the sheet: Host Rock, Iron Chunk (reusable), Base Rock (reusable); the hero is their union.
"""
import math
import random

import bmesh
import bpy
from mathutils import Matrix, Vector
from mathutils.bvhtree import BVHTree

import flintkit
import kit_mcp as K
import kit_models as M

NUM, TITLE, SHEET = 3, "Iron", "M003"
HOST, HOST_COOL, STEEL, RUST, BASE = "m003_host", "m003_host_cool", "m003_iron", "m003_rust", "m003_base_rock"

# broad squat dome, finely faceted like the sheet (about 60 hull points)
HOST_RINGS = [(0.0, 0.9, 10), (0.2, 1.0, 12), (0.45, 0.98, 12), (0.68, 0.88, 11), (0.86, 0.68, 9), (1.0, 0.4, 6)]
HOST_SIZE = (7.0, 6.4, 5.6)
# chunks: (azimuth deg, -90 = front; height frac; radius; thickness; roll)
CHUNKS = ((-135, 0.46, 1.95, 0.55, 0.3), (-58, 0.8, 1.45, 0.48, -0.4), (-48, 0.33, 1.4, 0.48, 0.6),
          (140, 0.52, 1.55, 0.5, 0.1), (35, 0.56, 1.5, 0.5, -0.3))
BASE_ROCKS = ((-3.3, -1.9, 1.9, 1.7, 1.3), (-1.0, -3.0, 1.4, 1.3, 0.9), (1.6, -3.0, 1.8, 1.6, 1.2),
              (3.5, -1.0, 1.6, 1.5, 1.1), (3.3, 1.6, 1.2, 1.1, 0.8), (0.4, 3.2, 1.7, 1.5, 1.1),
              (-3.0, 1.9, 1.3, 1.2, 0.9))
BASE_RINGS = [(0.0, 0.92, 6), (0.4, 1.0, 6), (0.75, 0.7, 5), (1.0, 0.25, 3)]


def palette():
    K.set_colour(HOST, "#7C7172", rough=0.92)
    K.set_colour(HOST_COOL, "#726C72", rough=0.92)
    K.set_colour(STEEL, "#9CA3B8", rough=0.35, metal=0.4)
    K.set_colour(RUST, "#A85A33", rough=0.85)
    K.set_colour(BASE, "#8A8080", rough=0.92)


def _probe_tree():
    t = flintkit.Asset("_probe", "probe")
    K.hull_rock(t, HOST_SIZE, seed=3011, mat=HOST, rings=HOST_RINGS, jitter=0.05, rot=0.3, keep_bottom=True)
    t.bm.faces.ensure_lookup_table()
    return t, BVHTree.FromBMesh(t.bm)


def seats():
    """Where each chunk sits: the surface point and normal at its azimuth/height on the host."""
    t, tree = _probe_tree()
    out = []
    for az, hf, R, T, roll in CHUNKS:
        a = math.radians(az)
        d = Vector((math.cos(a), math.sin(a), 0))
        z = HOST_SIZE[2] * hf
        hit = tree.ray_cast(Vector((0, 0, z)) + d * 20, -d, 60)
        n = (hit[1] + Vector((0, 0, 0.35 if hf > 0.6 else 0.1))).normalized()
        out.append((hit[0], n, R, T, roll))
    t.bm.free()
    return out


def host(a, flats=True):
    """The host rock, with a flat facet planed off wherever a chunk sits (the sheet's 'clearly defined flat
    surfaces on the host rock')."""
    vs = K.hull_rock(a, HOST_SIZE, seed=3011, mat=HOST, rings=HOST_RINGS, jitter=0.05, rot=0.3, keep_bottom=True)
    if flats:
        bm = a.bm
        for p, n, R, T, roll in seats():
            geom = list({x for f in K.faces_of(vs) for x in list(f.verts) + list(f.edges) + [f]})
            res = bmesh.ops.bisect_plane(bm, geom=geom, plane_co=p - n * 0.22, plane_no=n, clear_outer=True)
            cut = [e for e in res["geom_cut"] if isinstance(e, bmesh.types.BMEdge)]
            if cut:
                bmesh.ops.contextual_create(bm, geom=cut)
            vs = [v for v in vs if v.is_valid] + [v for v in res["geom_cut"] if isinstance(v, bmesh.types.BMVert)]
            vs = list({v for v in vs if v.is_valid})
        faces = K.faces_of(vs)
        for f in faces:
            f.material_index = a._mi(HOST)
        a._finish(vs, HOST)
    K.blend(a, vs, HOST, HOST_COOL, K.noise_field(scale=0.22, seed=3011), level=0.15, width=0.45, steps=2)
    K.texture(a, vs, amp=0.04, scale=0.3, jitter=0.04, seed=3011)
    return vs


def chunk(a, base, normal, R, T, roll, seed):
    """One iron chunk: a thick six-sided slab whose rust-orange side band (the depleted edge) rises to a
    faceted steel top with a low off-centre ridge. Solid geometry with simple thickness."""
    rng = random.Random(seed)
    n = Vector(normal).normalized()
    up = Vector((0, 0, 1))
    u = up - n * up.dot(n)
    u = u.normalized() if u.length > 1e-4 else Vector((1, 0, 0))
    u = Matrix.Rotation(roll, 3, n) @ u
    w = n.cross(u).normalized()
    c = Vector(base) - n * 0.32                       # bottom 0.1 below the planed facet (no coplanar faces)
    ring = []
    for k in range(6):
        t = 2 * math.pi * k / 6 + rng.uniform(-0.18, 0.18)
        ring.append(u * math.cos(t) * R * rng.uniform(0.85, 1.05) + w * math.sin(t) * R * 0.78 * rng.uniform(0.85, 1.05))
    pts = [c + q for q in ring]                                  # base on the host
    pts += [c + n * T * 0.55 + q * 0.86 for q in ring]           # top of the rust band, tapered inward
    pts += [c + n * T * 0.8 + q * 0.64 for q in ring]            # steel shoulder
    rot = Matrix.Rotation(math.pi / 6, 3, n)
    pts += [c + n * T * 0.93 + rot @ q * 0.36 for q in ring[::2]]  # inner facet ring: a gem-like steel top
    pts += [c + n * T + u * R * 0.12 + w * R * rng.uniform(-0.1, 0.1), c + n * T * 0.97 - u * R * 0.28]
    bm = a.bm
    vs = [bm.verts.new(p) for p in pts]
    bmesh.ops.convex_hull(bm, input=vs)
    vs = [v for v in vs if v.is_valid and v.link_faces]
    bmesh.ops.recalc_face_normals(bm, faces=K.faces_of(vs))
    a._finish(vs, RUST)
    # steel on the faceted top (above the rust band): a material change, the sheet's chunk vs its rim
    K.blend(a, vs, RUST, STEEL, lambda q: (q - c).dot(n) / T, level=0.62, width=0.1, mode="hard")
    K.texture(a, vs, amp=0.04, scale=0.8, jitter=0.035, seed=seed)
    return vs


def chunks(a, which=None, at_origin=False):
    out = []
    for k, (p, n, R, T, roll) in enumerate(seats()):
        if which is not None and k != which:
            continue
        if at_origin:
            out += chunk(a, Vector((0, 0, 0.22)), Vector((0, 0, 1)), R, T, 0.0, 3020 + k)
        else:
            out += chunk(a, p, n, R, T, roll, 3020 + k)
    return out


def base_rocks(a, which=None, at_origin=False):
    vs = []
    for i, (x, y, w, d, h) in enumerate(BASE_ROCKS):
        if which is not None and i != which:
            continue
        loc = (0, 0, 0) if at_origin else (x * 0.9, y * 0.9, 0)       # tucked against the host so all parts join
        v = K.hull_rock(a, (w, d, h), loc=loc, seed=3030 + i, mat=BASE, rings=BASE_RINGS, jitter=0.06,
                        rot=0.7 * i, keep_bottom=True)
        K.texture(a, v, amp=0.04, scale=0.5, jitter=0.04, seed=3030 + i)
        vs += v
    return vs


def hero(a):
    host(a)
    chunks(a)
    base_rocks(a)


NOTES = {
    "Iron": "iron resource: grey host rock with five thick steel iron chunks seated on planed flat facets, each "
            "ringed by a rust-orange depleted edge, and five base rocks round the foot; one closed mesh",
    "IronHostRock": "Host Rock (reusable): grey faceted dome with flat facets planed where the chunks sit",
    "IronChunk": "Iron Chunk (reusable): thick six-sided slab, rust-orange edge band under a faceted steel top",
    "IronBaseRock": "Base Rock (reusable): small grey faceted rock for the foot",
}


def build(render=True):
    M.coll(NUM, TITLE)
    palette()
    specs = [("Iron", "hero", hero, 4000, "hull"),
             ("IronHostRock", "part", host, 1000, "hull"),
             ("IronChunk", "part", lambda a: chunks(a, 0, True), 1000, "hull"),
             ("IronBaseRock", "part", lambda a: base_rocks(a, 0, True), 1000, "hull")]
    objs = [M.mk(SHEET, n, fn, subject=TITLE, role=r, notes=NOTES[n], budget=b, collision=c)
            for n, r, fn, b, c in specs]
    for o in objs:
        if any(m.name == "FB_" + STEEL for m in o.data.materials):
            o["kit_shading_ok"] = "steel top vs rust edge band: the sheet's Iron Chunk vs Depleted Edge (Chunk Rim)"
    audits = [M.finish(o, union=o.get("kit_role") == "hero") for o in objs]
    M.display(NUM, objs, TITLE)
    out = {"audit": audits, "problems": K.check(objs)}
    if render:
        hero_o, host_o, chunk_o, base_o = objs
        saved = M.explode(objs[1:], {})
        try:
            hx, hy = hero_o.location.x, hero_o.location.y
            host_o.location = (hx + 40, hy, 1.6)
            chunk_o.location = (hx + 40 - 5.2, hy - 1.0, 4.0)
            base_o.location = (hx + 40 - 3.0, hy - 4.0, 0)
            out["views"] = M.views(NUM, [hero_o], extra={"exploded": ([host_o, chunk_o, base_o], -14, 12)})
        finally:
            M.restore(saved)
            M.display(NUM, objs, TITLE)
    return out
