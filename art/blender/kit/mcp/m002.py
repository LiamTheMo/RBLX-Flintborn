"""002 Flint (references/002.png): a pale limestone boulder with three sharp dark flint inserts set in shallow
recesses, and three pale base rocks.

    import importlib, m002; importlib.reload(m002); m002.build()

Parts as on the sheet: Limestone Shell (main body, with the recesses), Flint Insert (Large / Medium / Small),
Base Rocks (x3, delivered as one piece). The hero is the union of all of them.
"""
import math
import random

import bmesh
import bpy
from mathutils import Matrix, Vector

import kit_mcp as K
import kit_models as M
import m001

NUM, TITLE, SHEET = 2, "Flint", "M002"
LIME, LIME_WARM, FLINT, FLINT_EDGE, BASE = "m002_limestone", "m002_limestone_warm", "m002_flint", "m002_flint_edge", "m002_base_rock"

# few points: broad flat planes, an uneven footprint and a slightly peaked, off-centre crown (WorldModeling 12.1)
SHELL = [(0.0, 0.88, 6), (0.25, 1.0, 7), (0.6, 0.93, 6), (0.84, 0.62, 5), (1.0, 0.25, 3)]
SHELL_SIZE = (7.0, 6.4, 5.8)         # near-round footprint: reads as a chunky node (user, 2026-10-27)
# inserts: (name, centre on the shell surface direction (azimuth deg, height frac), length, width, height, roll)
# inserts: (name, azimuth deg (-90 = front), height frac, radius, height, roll). Spread round the dome so they
# show at the silhouette from the front, side, rear and top, as on the sheet.
INSERTS = (("Large", -160, 0.38, 1.35, 2.7, 0.5), ("Medium", -80, 0.78, 1.15, 2.4, -0.35),
           ("Small", -8, 0.44, 1.0, 2.1, 0.3))
BASE_ROCKS = ((-2.5, -2.1, 1.8, 1.6, 1.2), (0.6, -2.6, 1.5, 1.4, 1.0), (2.9, -1.1, 1.7, 1.5, 1.1),
              (-1.4, 2.6, 1.6, 1.4, 1.0))


def palette():
    K.set_colour(LIME, "#B3A093", rough=0.92)        # measured against the sheet front view
    K.set_colour(LIME_WARM, "#AD9988", rough=0.92)
    K.set_colour(FLINT, "#56586A", rough=0.55)
    K.set_colour(BASE, "#958A89", rough=0.92)


def shell(a):
    vs = K.hull_rock(a, SHELL_SIZE, seed=2011, mat=LIME, rings=SHELL, jitter=0.06, rot=0.25, lean=(0.1, 0.05),
                     keep_bottom=True)
    vs = chamfer(a, vs, 0.08)
    K.blend(a, vs, LIME, LIME_WARM, K.noise_field(scale=0.25, seed=2011), level=0.15, width=0.45, steps=2)
    K.texture(a, vs, amp=0.04, scale=0.3, jitter=0.035, seed=2011)
    return vs


def chamfer(a, vs, w):
    faces = K.faces_of(vs)
    edges = list({e for f in faces for e in f.edges})
    res = bmesh.ops.bevel(a.bm, geom=edges + vs, offset=w, offset_type="OFFSET", segments=1, profile=0.5,
                          affect="EDGES", clamp_overlap=True)
    nf = res.get("faces", [])
    allf = [f for f in set(faces) | set(nf) if f.is_valid]
    big = [f for f in allf if len(f.verts) > 4]
    if big:
        bmesh.ops.triangulate(a.bm, faces=big)
    return list({v for f in K.faces_of(vs) + [f for f in nf if f.is_valid] for v in f.verts if v.is_valid})


def surface_point(az_deg, hfrac):
    """A point on the shell's outer surface at azimuth (deg, -90 = front) and height fraction, with its normal,
    found by casting at a test build of the shell."""
    from mathutils.bvhtree import BVHTree
    import flintkit
    t = flintkit.Asset("_probe", "probe")
    shell(t)
    t.bm.faces.ensure_lookup_table()
    tree = BVHTree.FromBMesh(t.bm)
    az = math.radians(az_deg)
    z = SHELL_SIZE[2] * hfrac
    d = Vector((math.cos(az), math.sin(az), 0))
    hit = tree.ray_cast(Vector((0, 0, z)) + d * 20, -d, 60)
    t.bm.free()
    return hit[0], hit[1]


def shard(a, base, normal, radius, height, roll, seed):
    """A chunky faceted flint crystal (about 24 facets): a five-sided base ring, a wider twisted waist and a
    short three-point crown to a lopsided tip, sunk 45% into the surface so it sits in a real recess."""
    rng = random.Random(seed)
    n = Vector(normal).normalized()
    up = Vector((0, 0, 1))
    along = up - n * up.dot(n)
    along = along.normalized() if along.length > 1e-4 else Vector((1, 0, 0))
    along = Matrix.Rotation(roll, 3, n) @ along
    side = n.cross(along).normalized()
    c = Vector(base) - n * height * 0.45
    pts = []
    for k in range(5):
        t = 2 * math.pi * k / 5 + rng.uniform(-0.2, 0.2)
        pts.append(c + (along * math.cos(t) + side * math.sin(t)) * radius * rng.uniform(0.85, 1.0))
    for k in range(5):
        t = 2 * math.pi * (k + 0.5) / 5 + rng.uniform(-0.15, 0.15)
        pts.append(c + n * height * 0.42 + (along * math.cos(t) + side * math.sin(t)) * radius * rng.uniform(0.95, 1.1))
    for k in range(3):
        t = 2 * math.pi * k / 3 + rng.uniform(-0.3, 0.3)
        pts.append(c + n * height * 0.78 + (along * math.cos(t) + side * math.sin(t)) * radius * 0.5)
    pts.append(c + n * height + along * radius * 0.25 + side * radius * rng.uniform(-0.15, 0.15))
    bm = a.bm
    vs = [bm.verts.new(p) for p in pts]
    bmesh.ops.convex_hull(bm, input=vs)
    vs = [v for v in vs if v.is_valid and v.link_faces]
    bmesh.ops.recalc_face_normals(bm, faces=K.faces_of(vs))
    a._finish(vs, FLINT)
    # one flint colour; the sheet's lighter top faces are lighting (a crown band was flagged as painted light)
    K.texture(a, vs, amp=0.05, scale=0.8, jitter=0.04, seed=seed)
    return vs


def inserts(a, which=("Large", "Medium", "Small"), at_origin=False):
    out = []
    for k, (name, az, hf, R, H, roll) in enumerate(INSERTS):
        if name not in which:
            continue
        if at_origin:
            out += shard(a, Vector((0, 0, H * 0.45)), Vector((0, 0, 1)), R, H, 0.0, 2020 + k)
        else:
            p, nrm = surface_point(az, hf)
            out += shard(a, p, nrm, R, H, roll, 2020 + k)
    return out


def base_rocks(a, at_origin=False):
    vs = []
    for i, (x, y, w, d, h) in enumerate(BASE_ROCKS):
        loc = (x * 0.6, y * 0.0, 0) if at_origin else (x, y, 0)
        v = K.hull_rock(a, (w, d, h), loc=loc, seed=2030 + i, mat=BASE, rings=m001.SUPPORT, jitter=0.06,
                        rot=0.7 * i, keep_bottom=True)
        K.texture(a, v, amp=0.04, scale=0.5, jitter=0.035, seed=2030 + i)
        vs += v
    return vs


def hero(a):
    shell(a)
    inserts(a)
    base_rocks(a)


def shell_part(a):
    """The Limestone Shell alone, with a shallow recess where each insert sits (the inserts are subtracted)."""
    shell(a)
    inserts(a)                       # removed again after the build (see build): leaves their pockets


NOTES = {
    "Flint": "flint resource: pale limestone boulder with three sharp dark flint shards (large, medium, small) set in "
             "shallow recesses on its front faces, and three pale base rocks at the foot; parts unioned into one "
             "closed mesh",
    "FlintLimestoneShell": "Limestone Shell (main body) alone, with the three shallow insert recesses",
    "FlintInsertLarge": "Flint Insert (Large): chunky dark faceted crystal",
    "FlintInsertMedium": "Flint Insert (Medium): chunky dark faceted crystal",
    "FlintInsertSmall": "Flint Insert (Small): chunky dark faceted crystal (exported as FlintInsertSmallM002: R01 owns the plain name)",
    "FlintBaseRocks": "Base Rocks (x3): three small pale rocks for the foot, one piece",
}


def subtract_inserts(o):
    """Turn the shell+inserts build into the shell with recesses: split the shells, subtract each insert."""
    others = M.split_loose(o)
    # the largest shell is the limestone; split_loose keeps shell 0 (built first) in o
    for p in others:
        m = o.modifiers.new("D", "BOOLEAN")
        m.operation, m.solver, m.object = "DIFFERENCE", "EXACT", p
        with M._override(o):
            bpy.ops.object.modifier_apply(modifier=m.name)
        bpy.data.objects.remove(p, do_unlink=True)
    # the pocket walls came over with the insert's material: they are limestone (the warmer, shaded tone)
    mats = [m.name for m in o.data.materials]
    if "FB_" + FLINT in mats:
        fi = mats.index("FB_" + FLINT)
        if "FB_" + LIME_WARM not in mats:
            o.data.materials.append(bpy.data.materials["FB_" + LIME_WARM])
            mats.append("FB_" + LIME_WARM)
        wi = mats.index("FB_" + LIME_WARM)
        for poly in o.data.polygons:
            if poly.material_index == fi:
                poly.material_index = wi
    K.drop_unused_slots(o)


def build(render=True):
    M.coll(NUM, TITLE)
    palette()
    specs = [("Flint", "hero", hero, 4000, "hull"),
             ("FlintLimestoneShell", "part", shell_part, 1000, "hull"),
             ("FlintInsertLarge", "part", lambda a: inserts(a, ("Large",), True), 1000, "hull"),
             ("FlintInsertMedium", "part", lambda a: inserts(a, ("Medium",), True), 1000, "hull"),
             ("FlintInsertSmall", "part", lambda a: inserts(a, ("Small",), True), 1000, "hull"),
             ("FlintBaseRocks", "part", lambda a: base_rocks(a, True), 1000, "none")]
    objs = [M.mk(SHEET, n, fn, subject=TITLE, role=r, notes=NOTES[n], budget=b, collision=c)
            for n, r, fn, b, c in specs]
    subtract_inserts(objs[1])
    audits = [M.finish(o, union=o.get("kit_role") == "hero" or o.name == "FlintBaseRocks" and False) for o in objs]
    M.display(NUM, objs, TITLE)
    out = {"audit": audits, "problems": K.check(objs)}
    if render:
        hero_o, shell_o = objs[0], objs[1]
        parts = objs[1:]
        saved = M.explode(parts, {})
        try:
            hx, hy = hero_o.location.x, hero_o.location.y
            shell_o.location = (hx + 40, hy, 2.6)
            for o, (name, az, hf, *_r) in zip(objs[2:5], INSERTS):
                p, nrm = surface_point(az, hf)
                q = p + nrm * 3.6
                o.location = (hx + 40 + q.x, hy + q.y, 2.6 + q.z - 0.6)
            objs[5].location = (hx + 40, hy - 0.5, 0)
            out["views"] = M.views(NUM, [hero_o], extra={"exploded": (parts, -14, 12)})
        finally:
            M.restore(saved)
    return out
