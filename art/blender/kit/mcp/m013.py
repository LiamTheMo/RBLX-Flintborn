"""013 Sulfur (references/013.png): chunky bevelled bright-yellow sulfur blocks sitting on two stacked flat slabs of
grey host rock, with small darker base rocks round the foot.

    import importlib, m013; importlib.reload(m013); m013.build()

Parts as on the sheet: Sulfur Chunk (reusable), Host Rock (Top), Host Rock (Base), Base Rock (reusable). The hero is
their union.
"""
import random

import bmesh
from mathutils import Matrix, Vector

import kit_mcp as K
import kit_models as M
import m004

NUM, TITLE, SHEET = 13, "Sulfur", "M013"
SULFUR, SULFUR_SHADOW, HOST, HOST_DARK, BASE = ("m013_sulfur", "m013_sulfur_shadow", "m013_host", "m013_host_dark",
                                               "m013_base")

# host slabs: (label, x, y, z, w, d, h, rot, seed): broad flat oval slabs with bevelled edges, the top one set back
SLAB = [(0.0, 0.94, 10), (0.25, 1.0, 11), (0.75, 0.99, 11), (1.0, 0.86, 10)]
SLABS = (("Base", 0.0, 0.0, 0.0, 10.2, 7.6, 1.9, 0.15, 13001), ("Top", 0.2, 0.3, 1.75, 9.0, 6.6, 1.7, -0.1, 13002))
TOP_Z = 1.75 + 1.7          # top of the upper slab
# sulfur chunks: (x, y, w, d, h, yaw, seed); bevelled blocks sunk a little into the top slab
CHUNKS = ((-0.3, 0.9, 3.6, 3.0, 2.9, 0.25, 13011), (-2.8, 0.2, 2.5, 2.3, 2.1, -0.3, 13012),
          (1.7, -0.9, 3.5, 2.9, 2.4, 0.1, 13013), (3.3, -2.0, 0.9, 0.8, 0.6, 0.6, 13014))
BASE_ROCKS = ((-4.9, -2.2, 2.0, 1.8, 1.4), (-1.6, -3.9, 1.8, 1.6, 1.2), (2.4, -3.8, 1.9, 1.7, 1.2),
              (4.9, -1.6, 1.7, 1.6, 1.1), (5.0, 1.9, 1.6, 1.5, 1.0), (1.2, 3.8, 1.7, 1.5, 1.1),
              (-2.9, 3.6, 1.6, 1.5, 1.0), (-5.2, 1.0, 1.5, 1.4, 1.0))
BASE_RINGS = [(0.0, 0.92, 6), (0.4, 1.0, 6), (0.75, 0.7, 5), (1.0, 0.25, 3)]


def palette():
    K.set_colour(SULFUR, "#F8DF3C", rough=0.6)
    K.set_colour(SULFUR_SHADOW, "#C9BC3E", rough=0.6)
    K.set_colour(HOST, "#8F8684", rough=0.92)
    K.set_colour(HOST_DARK, "#817876", rough=0.92)
    K.set_colour(BASE, "#776A66", rough=0.92)


def slab(a, label, at_origin=False):
    _, x, y, z, w, d, h, rot, seed = next(s for s in SLABS if s[0] == label)
    vs = K.hull_rock(a, (w, d, h), loc=(0, 0, 0) if at_origin else (x, y, z), seed=seed, mat=HOST, rings=SLAB,
                     jitter=0.05, rot=rot, keep_bottom=True)
    K.blend(a, vs, HOST, HOST_DARK, K.noise_field(scale=0.3, seed=seed), level=0.15, width=0.4, steps=1)
    K.texture(a, vs, amp=0.04, scale=0.4, jitter=0.03, seed=seed)
    return vs


def chunk(a, i, at_origin=False):
    """One sulfur chunk: a bevelled block (a box whose corners are cut, about 26 broad faces), a little uneven; a
    few faces in the sulfur shadow tone (broad patches by noise, not by facing)."""
    x, y, w, d, h, yaw, seed = CHUNKS[i]
    rng = random.Random(seed)
    base = Vector((0, 0, 0)) if at_origin else Vector((x, y, TOP_Z - 0.35))
    rot = Matrix.Rotation(0.0 if at_origin else yaw, 3, "Z")
    b = 0.22                                                 # bevel, as a share of each side
    pts = []
    for sx in (-1, 1):
        for sy in (-1, 1):
            for sz in (0, 1):
                cx, cy, cz = sx * w / 2, sy * d / 2, sz * h
                jz = -1 if sz else 1
                for p in ((cx - sx * w * b, cy, cz), (cx, cy - sy * d * b, cz), (cx, cy, cz + jz * h * b)):
                    q = Vector(p) + Vector((rng.uniform(-1, 1), rng.uniform(-1, 1), rng.uniform(-1, 1))) * 0.06 * h
                    pts.append(base + rot @ q)
    vs = [a.bm.verts.new(p) for p in pts]
    bmesh.ops.convex_hull(a.bm, input=vs)
    vs = [v for v in vs if v.is_valid and v.link_faces]
    bmesh.ops.recalc_face_normals(a.bm, faces=K.faces_of(vs))
    a._finish(vs, SULFUR)
    nf = K.noise_field(scale=0.6, seed=seed)
    si = a._mi(SULFUR_SHADOW)
    for f in K.faces_of(vs):
        if nf(f.calc_center_median()) > 0.35:
            f.material_index = si
    return vs


def base_rocks(a, which=None, at_origin=False):
    out = []
    for i, (x, y, w, d, h) in enumerate(BASE_ROCKS):
        if which is not None and i not in which:
            continue
        seed = 13031 + i
        vs = K.hull_rock(a, (w, d, h), loc=(0, 0, 0) if at_origin else (x, y, 0), seed=seed, mat=BASE,
                         rings=BASE_RINGS, jitter=0.07, rot=0.5 * i, keep_bottom=True)
        K.texture(a, vs, amp=0.04, scale=0.5, jitter=0.04, seed=seed)
        out += vs
    return out


def hero(a):
    for s in SLABS:
        slab(a, s[0])
    for i in range(len(CHUNKS)):
        chunk(a, i)
    base_rocks(a)


NOTES = {
    "Sulfur": "sulfur resource: three chunky bevelled bright-yellow sulfur blocks and a small nugget sitting on two "
              "stacked flat slabs of grey host rock, with small darker base rocks round the foot; one closed mesh",
    "SulfurChunk": "Sulfur Chunk (reusable): bevelled bright-yellow block",
    "SulfurHostTop": "Host Rock (Top): broad flat oval slab, bevelled edges",
    "SulfurHostBase": "Host Rock (Base): broad flat oval slab, bevelled edges",
    "SulfurBaseRock": "Base Rock (reusable): small dark faceted rock",
}


def build(render=True):
    M.coll(NUM, TITLE)
    palette()
    specs = [("Sulfur", "hero", hero, 4000, "hull"),
             ("SulfurChunk", "part", lambda a: chunk(a, 0, True), 1000, "hull"),
             ("SulfurHostTop", "part", lambda a: slab(a, "Top", True), 1000, "hull"),
             ("SulfurHostBase", "part", lambda a: slab(a, "Base", True), 1000, "hull"),
             ("SulfurBaseRock", "part", lambda a: base_rocks(a, (0,), True), 1000, "hull")]
    objs = [M.mk(SHEET, n, fn, subject=TITLE, role=r, notes=NOTES[n], budget=b, collision=c)
            for n, r, fn, b, c in specs]
    audits = []
    for o, (_, _, fn, _, _) in zip(objs, specs):
        if o.get("kit_role") == "hero":
            M.union_loose(o)
            m004.floor_cut(o, z0=-M._build_offset(fn).z)
        audits.append(M.finish(o, union=False))
    M.display(NUM, objs, TITLE)
    out = {"audit": audits, "problems": K.check(objs)}
    if render:
        hero_o, parts = objs[0], objs[1:]
        saved = M.explode(parts, {})
        try:
            hx, hy = hero_o.location.x, hero_o.location.y
            for o, (dx, dy, z) in zip(parts, ((0, 0, 6.5), (0, 0, 3.5), (0, 0, 0), (6.5, -3.5, 0))):
                o.location = (hx + 40 + dx, hy + dy, z)
            out["views"] = M.views(NUM, [hero_o], extra={"exploded": (parts, -16, 14)})
        finally:
            M.restore(saved)
            M.display(NUM, objs, TITLE)
    return out
