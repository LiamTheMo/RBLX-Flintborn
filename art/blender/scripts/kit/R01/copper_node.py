"""R01 row 4, COPPER: a warm grey-brown host rock with big inset copper crystals.

CopperNode (hero) is a wide faceted mound of warm grey-brown rock (medium,
evenly sized facets, a flared skirt, the peak a little right of centre and a
lower left shoulder) with four chunky orange copper gems set into its faces
(top-left shoulder, front left, the big one front right, back right), mottled
teal patina spattered around and under each gem and on the gems' lower bevels,
and small base rocks at its foot. Parts: CopperNodeHostRock, CopperInsert (plus
the two smaller insert shapes the reference shows, CopperInsertSmall and
CopperInsertShard), CopperNodeBaseRock (plus CopperNodeBaseRockSmall). Drops:
CopperOre and CopperOreSmall (irregular faceted orange chunks with mottled
teal on one lower side). Depleted: CopperNodeDepleted (a low rubble base with
the host's footprint).

Rocks are the convex hull of evenly spread points on a superellipsoid, cut flat
at z=0 (bottom face removed), then each vertex is nudged in or out along its
normal so neighbouring facets meet at crisp angles. Copper gems are the hull of four rings (buried
base, girdle, crown, a short ridge on top); in the hero a shallow flat seat is
first chopped into the host under each gem, then the gem is placed along the
host's local averaged normal and sunk until its girdle is just under the
surface (about half the gem buried, no bulb), never bent to the rock. Patina is not a decal: the host (and each gem) is cut by a handful of
random planes across the surface around a spot, and the small cells that fall
inside a noisy radius are painted the ONE verdigris colour, which reads as
broken, ragged spatter with no floating cards (the ragged edge comes from the
cell shapes, never from a fade colour). Afterwards coplanar cells of the
same colour are merged back, so the cuts cost triangles only where teal meets
stone. Each material is one palette key (r01_cu_rock, copper, r01_cu_verdigris)
with a small random Tint per facet (+-4%); light tops and dark sides come from
the lighting, not from paint.
"""

import json
import math
import random

import bmesh
from mathutils import Matrix, Vector
from mathutils.bvhtree import BVHTree

SUBJECT = "CopperNode"
ROW = 4
# Host rock: the reference swatch is a warm grey-brown (#9C8576), a touch greyer
# so it doesn't read pink; one colour, the lighting shades the facets.
PALETTE = {
    "r01_cu_rock": ("#9A897D", 0.9, 0, 0),  # Copper node's warm grey-brown host rock AND its base rocks and depleted rubble (swatch #9C8576, nudged greyer so it never reads pink). Distinct material from r01_stone (browner); the two never share an asset.
    "r01_cu_verdigris": ("#5E9E94", 0.75, 0, 0),  # The single teal patina/verdigris spatter on copper host rock around the gems, on the gems' lower bevels and on copper ore drops (swatch #639593). One key: drop 'patina' and 'r01_cu_patina'.
    # Existing KIT_PALETTE key used as-is (not redeclared): "copper": ("#E2713A", 0.5, 0.35, 0)
}
ROCK = "r01_cu_rock"
CU, VERD = "copper", "r01_cu_verdigris"

# VFX colours sampled from the reference: copper orange + host grey-brown chips.
CHIPS = ["#E2713A", "#9C8576"]
DUST = ["#C2B2A6", "#9C8B80"]
DEPLETE_CHIPS = ["#9C8576", "#E2713A"]
GLINT = ["#FFE6C2", "#F7A061"]

# Host rock (studs). Front is -Y.
HOST = dict(size=(6.1, 3.9, 4.2), n=220, seed=43, p=3.15, jitter=0.015, zc=0.3, low=2.6, ring=18,
            taper=(0.1, 0.22), twist=0.35, tilt=0.3)
FLARE = (0.38, 0.12)       # lower 38% of the height pushed out by up to 12%: a flared skirt
LEAN_X = 0.08             # upper points drift toward +X: the peak sits right of centre
SHOULDER = 0.21            # the left (-X) upper side sits lower

# Copper gems in the hero: (x, z, ray direction, width, height/width, roll deg).
# Each is placed where a ray along `dir` (from outside) meets the host, then sunk
# until its girdle ring is under the host surface (flat plates set into the faces).
INSERTS = [
    ("top_left", (-0.85, 3.0), (0.35, 1.0, -0.45), 2.15, 0.4, 15),
    ("front_left", (-0.85, 1.6), (0.1, 1.0, 0.0), 2.35, 0.42, 30),
    ("front_right", (1.35, 1.85), (-0.1, 1.0, 0.0), 2.75, 0.38, 100),
    ("back_right", (1.4, 2.6), (-0.1, -1.0, -0.1), 2.0, 0.4, 30),
]
GIRDLE_UNDER = 0.02        # girdle ring sits this far under the host surface (studs)
MAX_SINK = 0.62            # never sink more than this fraction of the gem height
SEAT_CUT = 0.1             # flat seat chopped into the host under each gem, depth as a fraction of its width
# Patina spatter on the host: (gem, offset (right, up) in gem widths, radius, cuts, fill).
# Clusters hug the gems, biased below and left of each; SPATTER_REACH caps how far
# from a gem's edge any teal cell may sit.
SPATTER = [
    ("front_left", (-0.4, -0.32), 0.6, 13, 0.6),     # the heaviest, below-left of the front-left gem
    ("front_left", (0.15, -0.45), 0.35, 8, 0.5),
    ("top_left", (-0.45, -0.3), 0.5, 11, 0.55),
    ("top_left", (0.3, -0.45), 0.32, 7, 0.5),
    ("front_right", (0.5, -0.2), 0.45, 10, 0.65),
    ("front_right", (-0.2, -0.45), 0.4, 9, 0.6),
    ("back_right", (-0.35, -0.45), 0.5, 10, 0.7),
]
SPATTER_REACH = 0.6
# Base rocks: (x, y, size, seed, yaw)
BASE_ROCKS = [
    ((-2.95, -1.65), (1.8, 1.55, 1.0), 61, 0.4),     # front-left, the bigger one
    ((3.05, -1.95), (1.3, 1.15, 0.72), 62, 1.2),    # front-right, smaller (forward so the hero camera sees it)
]
SMALL_BASE_ROCK = ((0.0, 0.0), (1.05, 0.95, 0.65), 63, 2.1)


# ---------------------------------------------------------------------------
# Small mesh toolkit: build pieces in loose bmeshes (face layers carry the
# palette key, tint and a group id), then copy them into the Asset.
# ---------------------------------------------------------------------------

KEYS = [ROCK, CU, VERD]


def new_bm():
    bm = bmesh.new()
    bm.faces.layers.int.new("mk")
    bm.faces.layers.float.new("tn")
    bm.faces.layers.int.new("grp")
    return bm


def setf(bm, f, key, tint):
    f[bm.faces.layers.int["mk"]] = KEYS.index(key)
    # snapped to a few levels, so each colour needs only a handful of palette rows
    f[bm.faces.layers.float["tn"]] = round(tint / 0.04) * 0.04


def getf(bm, f):
    return KEYS[f[bm.faces.layers.int["mk"]]], f[bm.faces.layers.float["tn"]]


def set_grp(bm, faces, g):
    lay = bm.faces.layers.int["grp"]
    for f in faces:
        f[lay] = g


def hull(bm, pts):
    """Convex hull of pts added to bm; returns its faces."""
    vs = [bm.verts.new(p) for p in pts]
    res = bmesh.ops.convex_hull(bm, input=vs, use_existing_faces=False)
    drop = list({g for g in res["geom_interior"] + res["geom_unused"] if isinstance(g, bmesh.types.BMVert)})
    if drop:
        bmesh.ops.delete(bm, geom=drop, context="VERTS")
    faces = [g for g in res["geom"] if isinstance(g, bmesh.types.BMFace) and g.is_valid]
    bmesh.ops.recalc_face_normals(bm, faces=faces)
    return faces


def drop_bottom(bm, faces=None, z=0.0):
    """Remove the flat ground-contact faces (never seen, ground hides them)."""
    bm.normal_update()
    faces = faces if faces is not None else bm.faces[:]
    bot = [f for f in faces if f.is_valid and f.normal.z < -0.95 and all(abs(v.co.z - z) < 1e-3 for v in f.verts)]
    if bot:
        bmesh.ops.delete(bm, geom=bot, context="FACES_ONLY")


def shape_points(size, n=40, seed=0, p=2.2, jitter=0.07, zc=0.4, taper=0.0, low=1.2, ring=10,
                 lean=(0.0, 0.0), twist=0.0, tilt=0.25):
    """Points on a superellipsoid of full extents `size`, base cut at z=0."""
    rng = random.Random(seed)
    sx, sy, sz = size
    rx, ry = sx / 2, sy / 2
    zcen = sz * zc
    rz_up, rz_lo = sz - zcen, zcen * low
    ga = math.pi * (3 - math.sqrt(5))
    tx, ty = taper if isinstance(taper, tuple) else (taper, taper)

    def place(x, y, z):
        Z = zcen + z * (rz_up if z > 0 else rz_lo)
        h = max(0.0, Z / sz)
        return Vector((x * rx * (1 - tx * h) + lean[0] * Z, y * ry * (1 - ty * h) + lean[1] * Z, Z))

    pts = []
    for i in range(n):
        z = 1 - 2 * (i + 0.5) / n
        r = math.sqrt(max(0.0, 1 - z * z))
        th = ga * i + twist + rng.uniform(-tilt, tilt)
        x, y = r * math.cos(th), r * math.sin(th)
        k = (abs(x) ** p + abs(y) ** p + abs(z) ** p) ** (-1 / p)
        s = k * (1 + rng.uniform(-jitter, jitter))
        P = place(x * s, y * s, z * s)
        if P.z > 0.08 * sz:
            pts.append(P)
    zz = min(0.999, zcen / rz_lo)
    rad = (1 - zz ** p) ** (1 / p)
    for j in range(ring):
        th = 2 * math.pi * (j + rng.uniform(-0.25, 0.25)) / ring + twist
        x, y = math.cos(th), math.sin(th)
        k = (abs(x) ** p + abs(y) ** p) ** (-1 / p)
        s = rad * k * (1 + rng.uniform(-jitter, jitter) * 0.7)
        P = place(x * s, y * s, -zz)
        P.z = 0.0
        pts.append(P)
    return pts


def crumple(bm, faces, amt, seed):
    """Push each hull vertex in or out along its normal by up to `amt` studs, so
    neighbouring facets meet at livelier angles and every edge reads crisp (a
    hand-cut low-poly look rather than an even soft dome). Ground verts stay on
    z=0 and only move sideways."""
    rng = random.Random(seed * 31 + 9)
    bm.normal_update()
    verts = sorted({v for f in faces if f.is_valid for v in f.verts}, key=lambda v: tuple(v.co))
    for v in verts:
        d = v.normal * rng.uniform(-amt, amt)
        if v.co.z < 1e-3:
            d.z = 0.0
        v.co += d
        v.co.z = max(0.0, v.co.z)


def paint_rock(bm, faces, seed, lift=1.0):
    """One rock colour; each facet gets a small random tint (three levels, +-0.04)
    so the stone reads mottled. Light tops and dark sides come from the lighting,
    never from paint."""
    rng = random.Random(seed * 7 + 3)
    for f in sorted(faces, key=lambda f: tuple(f.calc_center_median())):
        if f.is_valid:
            setf(bm, f, ROCK, rng.choice((0.96, 1.0, 1.0, 1.04)) * lift)


def rock_piece(bm, size, seed, loc=(0.0, 0.0), yaw=0.0, n=22, lift=1.0, **kw):
    opts = dict(p=2.4, jitter=0.14, zc=0.3, taper=0.22, low=1.6, ring=7, tilt=0.45)
    opts.update(kw)
    pts = shape_points(size, n=n, seed=seed, **opts)
    c, s = math.cos(yaw), math.sin(yaw)
    pts = [Vector((loc[0] + p.x * c - p.y * s, loc[1] + p.x * s + p.y * c, p.z)) for p in pts]
    faces = hull(bm, pts)
    crumple(bm, faces, 0.05 * min(size), seed)
    paint_rock(bm, faces, seed, lift)
    return faces


def host_points():
    k = dict(HOST)
    seed = k.pop("seed")
    size = k.pop("size")
    n = k.pop("n")
    pts = shape_points(size, n=n, seed=seed, **k)
    sx, sy, sz = size
    zf, amt = FLARE
    for p in pts:
        h = p.z / sz
        if h < zf:  # a flared skirt: the base is wider than the shoulder line
            s = 1 + amt * (1 - h / zf)
            p.x *= s
            p.y *= s
        p.x += LEAN_X * p.z
        if p.x < 0 and h > 0.45:  # lower left shoulder
            p.z -= SHOULDER * sz * (h - 0.45) * (-p.x / (sx / 2))
    return pts


def host_rock(bm):
    faces = hull(bm, host_points())
    crumple(bm, faces, 0.14, HOST["seed"])
    paint_rock(bm, faces, HOST["seed"])
    drop_bottom(bm, faces)
    return [f for f in faces if f.is_valid]


# ---------------------------------------------------------------------------
# Copper gems
# ---------------------------------------------------------------------------

GIRDLE = 0.38      # girdle ring height (fraction of h); in the hero it sits at the host surface


def gem_points(w, h, seed, squash=0.82, n=6):
    """A chunky copper gem of width w and height h, flat base at z=0: base ring,
    wide girdle, crown ring and a short ridge on top."""
    rng = random.Random(seed)
    r = w / 2

    # one irregular hex outline, scaled for each ring: every bevel is a clean planar quad
    outline = []
    for i in range(n):
        a = 2 * math.pi * i / n + rng.uniform(-0.28, 0.28)
        rr = r * (1 + rng.uniform(-0.18, 0.18))
        outline.append((rr * math.cos(a), rr * math.sin(a) * squash))
    pts = []
    for k, z in ((0.8, 0.0), (1.0, h * GIRDLE), (0.62, h * 0.86)):
        pts += [Vector((x * k, y * k, z)) for x, y in outline]
    a = rng.uniform(-0.4, 0.4)
    for s in (-1, 1):  # a short ridge on top so the crown reads as a low faceted pyramid
        pts.append(Vector((s * r * 0.3 * math.cos(a), s * r * 0.3 * math.sin(a) * squash, h)))
    for p in pts:
        p.z = max(0.0, p.z)
    return pts


def small_points(w, seed):
    """Small pointed gem (the reference's middle insert)."""
    rng = random.Random(seed)
    r, h = w / 2, w * 1.0
    pts = []
    for k, rad, z, rot in ((5, r * 0.45, 0.0, 0.0), (5, r, h * 0.45, 0.5), (4, r * 0.5, h * 0.85, 0.2)):
        for i in range(k):
            a = 2 * math.pi * (i + rot) / k + rng.uniform(-0.1, 0.1)
            pts.append(Vector((rad * math.cos(a), rad * math.sin(a), z)))
    pts.append(Vector((0.05 * w, 0.0, h)))
    return pts


def shard_points(w, seed):
    """Tall hex prism with a slanted top (the reference's right-hand insert)."""
    rng = random.Random(seed)
    r, h = w / 2, w * 1.45
    pts = []
    for z, rad in ((0.0, r * 0.85), (h * 0.7, r)):
        for i in range(6):
            a = 2 * math.pi * i / 6 + rng.uniform(-0.08, 0.08)
            pts.append(Vector((rad * math.cos(a), rad * math.sin(a) * 0.8, z)))
    for i in range(6):
        a = 2 * math.pi * i / 6
        x = r * 0.62 * math.cos(a)
        pts.append(Vector((x, r * 0.62 * math.sin(a) * 0.8, h * 0.84 + h * 0.14 * (x / r + 1) * 0.5)))
    return pts


def paint_gem(bm, faces, seed):
    """One copper colour with a small random tint per facet (lighting shades it)."""
    rng = random.Random(seed * 13 + 5)
    for f in sorted(faces, key=lambda f: tuple(f.calc_center_median())):
        setf(bm, f, CU, rng.choice((0.96, 1.0, 1.04)))


def gem(bm, pts, seed, M=Matrix.Identity(4), cap=True, grp=0):
    """Hull a gem's points, transform it by M, paint it; returns its faces."""
    faces = hull(bm, pts)
    bm.normal_update()
    if not cap:  # buried base, never seen
        base = [f for f in faces if f.normal.z < -0.95]
        bmesh.ops.delete(bm, geom=base, context="FACES_ONLY")
        faces = [f for f in faces if f.is_valid]
    verts = list({v for f in faces for v in f.verts})
    bmesh.ops.transform(bm, matrix=M, verts=verts)
    set_grp(bm, faces, grp)
    paint_gem(bm, faces, seed)
    return faces


def frame(point, normal, roll=0.0):
    n = Vector(normal).normalized()
    x = Vector((0, 0, 1)).cross(n)
    if x.length < 1e-4:
        x = Vector((1, 0, 0))
    x.normalize()
    y = n.cross(x).normalized()
    R = Matrix((x, y, n)).transposed().to_4x4()
    return Matrix.Translation(Vector(point)) @ R @ Matrix.Rotation(roll, 4, "Z")


def tangents(n):
    """(right, up) on a surface with normal n: right is horizontal, up climbs."""
    right = Vector((0, 0, 1)).cross(n)
    if right.length < 1e-4:
        right = Vector((1, 0, 0))
    right.normalize()
    return right, n.cross(right).normalized()


def seat(tree, x, z, d, w):
    """Where a gem of width w sits: the hit of a ray along d through (x, ., z),
    and the host's normal averaged over the gem's footprint."""
    d = Vector(d).normalized()
    o = Vector((x, 0.0, z)) - d * 30.0
    hit, n0, _i, _ = tree.ray_cast(o, d)
    if hit is None:
        return None, None
    right, up = tangents(n0)
    acc = Vector(n0) * 2.0
    for i in range(8):
        a = 2 * math.pi * i / 8
        q = hit + (right * math.cos(a) + up * math.sin(a)) * w * 0.42
        h2, n2, _j, _ = tree.ray_cast(q + n0 * 3.0, -n0)
        if h2 is not None:
            acc += n2
    return hit, acc.normalized()


# ---------------------------------------------------------------------------
# Patina spatter: cut the faces around a spot into small cells, paint some
# ---------------------------------------------------------------------------


def faces_near(bm, grp, centre, radius, n):
    lay = bm.faces.layers.int["grp"]
    out = []
    for f in bm.faces:
        if f[lay] != grp or f.normal.dot(n) < 0.15:
            continue
        if any((v.co - centre).length < radius for v in f.verts) or \
                (f.calc_center_median() - centre).length < radius:
            out.append(f)
    return out


def spatter(bm, grp, centre, n, radius, cuts, fill, rng, below=None, near=None):
    """Cut the faces of group `grp` near `centre` with `cuts` random planes across
    the surface, then paint the cells inside a noisy radius teal (three tones).
    `below` = (point, down vector, min): only cells past that line on a gem."""
    n = Vector(n).normalized()
    right, up = tangents(n)
    a0 = rng.uniform(0, math.pi)
    for k in range(cuts):
        a = a0 + k * 2.39996 + rng.uniform(-0.3, 0.3)  # spread-out random directions: irregular, organic cells
        pn = right * math.cos(a) + up * math.sin(a)
        co = centre + pn * rng.uniform(-0.75, 0.75) * radius
        bm.normal_update()
        fs = faces_near(bm, grp, centre, radius * 1.1, n)
        if not fs:
            continue
        geom = fs + list({e for f in fs for e in f.edges}) + list({v for f in fs for v in f.verts})
        bmesh.ops.bisect_plane(bm, geom=geom, plane_co=co, plane_no=pn, dist=1e-4)
    bm.normal_update()
    painted = []
    wob = [rng.uniform(0.75, 1.25) for _ in range(6)]  # a lumpy, non-round outline
    for f in sorted(faces_near(bm, grp, centre, radius * 1.1, n), key=lambda f: tuple(f.calc_center_median())):
        c = f.calc_center_median()
        v = c - centre
        v -= n * v.dot(n)
        if below is not None:
            p0, down, lim = below
            if (c - p0).dot(down) < lim:
                continue
        if near is not None:  # every vertex of a teal cell stays close to its gem: no long streaks
            p0, lim = near
            if max((x.co - p0).length for x in f.verts) > lim:
                continue
        ang = math.atan2(v.dot(up), v.dot(right)) % (2 * math.pi)
        rr = radius * wob[int(ang / (2 * math.pi) * 6) % 6]
        d = v.length / rr
        if d > 1.0:
            continue
        # a cell may not reach far past the noisy outline (keeps big facets out of the spatter)
        if max(((x.co - centre) - n * (x.co - centre).dot(n)).length for x in f.verts) > rr * 1.35:
            continue
        if f.calc_area() / max(f.calc_perimeter() ** 2, 1e-9) < 0.036:  # a thin sliver reads as a scratch, not a blotch
            continue
        # solid core, ragged broken rim
        if d > 0.45 and rng.random() > fill * (1.0 - (d - 0.45) / 0.75):
            continue
        # one verdigris colour; the ragged edge comes from the cell shapes, never a fade colour
        setf(bm, f, VERD, rng.choice((0.96, 1.0, 1.04)))
        painted.append(f)
    return painted


# ---------------------------------------------------------------------------
# Asset output
# ---------------------------------------------------------------------------


def compact(bm):
    """Merge coplanar neighbours that share colour and tint: the spatter cuts only
    need to survive where they separate teal from rock, everything else folds
    back into the original facet (fewer triangles, same look)."""
    mk, tn = bm.faces.layers.int["mk"], bm.faces.layers.float["tn"]
    for f in bm.faces:
        f.material_index = f[mk] * 64 + int(round(f[tn] / 0.04))
    bmesh.ops.dissolve_limit(bm, angle_limit=math.radians(0.5), use_dissolve_boundaries=False,
                             verts=bm.verts[:], edges=bm.edges[:], delimit={"MATERIAL"})


def to_asset(fk, name, bm):
    """Copy a loose bmesh into an Asset (one mesh, palette materials, Tint), finish
    it and return (obj, offset) where offset is what finish() subtracted."""
    compact(bm)
    a = fk.Asset(name, "Kit", seed=sum(map(ord, name)))
    xs = [v.co.x for v in bm.verts]
    ys = [v.co.y for v in bm.verts]
    zs = [v.co.z for v in bm.verts]
    off = Vector(((min(xs) + max(xs)) / 2, (min(ys) + max(ys)) / 2, min(zs)))
    vmap = {v: a.bm.verts.new(v.co) for v in bm.verts}
    for f in bm.faces:
        try:
            nf = a.bm.faces.new([vmap[v] for v in f.verts])
        except ValueError:
            continue
        key, t = getf(bm, f)
        nf.material_index = a._mi(key)
        nf.smooth = False
        for lp in nf.loops:
            lp[a.tint_layer] = (t, t, t, 1.0)
    bm.free()
    return a.finish(), off


def front_point(obj, x, z, out=0.12):
    me = obj.data
    tree = BVHTree.FromPolygons([v.co.copy() for v in me.vertices], [tuple(p.vertices) for p in me.polygons])
    hit, _n, _i, _d = tree.ray_cast(Vector((x, -100.0, z)), Vector((0, 1, 0)))
    y = hit.y if hit is not None else min(v.co.y for v in me.vertices)
    return (x, y - out, z)


def emitters(kit, kind, chips, dust):
    em = json.loads(json.dumps(kit.vfx.KINDS[kind]["emitters"]))
    for e in em:
        e["color"] = list(chips if e["name"] == "Chips" else dust)
    return em


GLINT_BOX = 0.25    # glint emitter box (studs); the socket sits GLINT_OUT off the gem's crown
GLINT_OUT = 0.24


def glint_emitters(kit):
    em = json.loads(json.dumps(kit.vfx.KINDS["ore_glint"]["emitters"]))
    for e in em:
        e["color"] = list(GLINT)
        e["shape"] = [GLINT_BOX, GLINT_BOX, GLINT_BOX]
    return em


# ---------------------------------------------------------------------------
# Assets
# ---------------------------------------------------------------------------


def gem_sink(tree, pts, hit, m, h, roll):
    """How deep to set a gem so its girdle ring (the widest ring, pts[n:2n]) sits
    just under the host surface all the way round: on a curved face the girdle's
    edge would otherwise stand proud of the rock as a bulb. At least half the gem
    height, at most MAX_SINK of it."""
    n = (len(pts) - 2) // 3
    girdle = pts[n:2 * n]
    sink = h * 0.5
    for _ in range(2):
        M = frame(hit - m * sink, m, roll)
        worst = -1e9
        for p in girdle:
            q = M @ p
            s, _n, _i, _d = tree.ray_cast(q + m * 3.0, -m)
            prot = (q - s).dot(m) if s is not None else 0.3
            worst = max(worst, prot)
        sink = min(h * MAX_SINK, sink + max(0.0, worst + GIRDLE_UNDER))
    return sink


def hero_bm(with_inserts=True, with_base=True):
    """Host rock + gems + patina + base rocks. Returns (bm, glint points)."""
    bm = new_bm()
    host_rock(bm)
    glints = []
    if with_inserts:
        bm.faces.index_update()
        tree = BVHTree.FromBMesh(bm)
        rng = random.Random(404)
        # chop a shallow flat seat into the host under each gem (host verts past a
        # plane along the gem normal are pulled back onto it), so a wide gem sits
        # flush in a flat face instead of standing proud where the dome curves away
        for i, (name, (x, z), d, w, hf, roll) in enumerate(INSERTS):
            hit, m = seat(tree, x, z, d, w)
            if hit is None:
                continue
            p0 = hit - m * SEAT_CUT * w
            for v in bm.verts:
                if (v.co - hit).length > w * 1.1:
                    continue
                k = (v.co - p0).dot(m)
                if k > 0:
                    v.co -= m * k
                    v.co.z = max(0.0, v.co.z)
        bm.normal_update()
        tree = BVHTree.FromBMesh(bm)
        seats = {}
        for i, (name, (x, z), d, w, hf, roll) in enumerate(INSERTS):
            hit, m = seat(tree, x, z, d, w)
            if hit is None:
                continue
            seats[name] = (hit, m, w)
        # spatter the host first (only host faces are cut), then add the gems over it
        for name, (ox, oy), rad, cuts, fill in SPATTER:
            if name not in seats:
                continue
            hit, m, w = seats[name]
            right, up = tangents(m)
            c = hit + (right * ox + up * oy) * w
            h2, n2, _j, _ = tree.ray_cast(c + m * 2.0, -m)
            if h2 is not None:
                spatter(bm, 0, h2, n2, rad, cuts, fill, rng, near=(hit, w * 0.5 + SPATTER_REACH))
        for i, (name, (x, z), d, w, hf, roll) in enumerate(INSERTS):
            if name not in seats:
                continue
            hit, m, w = seats[name]
            h = w * hf
            pts = gem_points(w, h, 500 + i)
            sink = gem_sink(tree, pts, hit, m, h, math.radians(roll))
            M = frame(hit - m * sink, m, math.radians(roll))
            g = i + 1
            faces = gem(bm, pts, 500 + i, M, cap=False, grp=g)
            # teal on the gem's lower bevels
            right, up = tangents(m)
            down = -up
            spatter(bm, g, hit + m * (h - sink) * 0.3 + down * w * 0.32, (m + down).normalized(), w * 0.3, 8,
                     0.65, rng, below=(hit, down, w * 0.16))
            glints.append(hit + m * (h - sink + GLINT_OUT))
    if with_base:
        for loc, size, seed, yaw in BASE_ROCKS:
            f = rock_piece(bm, size, seed, loc, yaw)
            set_grp(bm, f, 9)
            drop_bottom(bm, f)
    return bm, glints


def build(kit):
    fk = kit.flintkit
    vfx = kit.vfx
    out = []

    # -- hero ------------------------------------------------------------------
    bm, glints = hero_bm()
    hero, off = to_asset(fk, "CopperNode", bm)
    hit = front_point(hero, 0.25, 2.6)
    vfx.add(hero, "harvest_hit", hit, color=CHIPS, emitters=emitters(kit, "harvest_hit", CHIPS, DUST))
    vfx.add(hero, "harvest_deplete", (0.0, 0.0, 0.25), color=DEPLETE_CHIPS,
            emitters=emitters(kit, "harvest_deplete", DEPLETE_CHIPS, DUST))
    for p in glints:
        vfx.add(hero, "ore_glint", tuple(p - off), scale=1.0, color=GLINT, emitters=glint_emitters(kit))
    kit.tag(hero, "hero", collision="hull",
            notes=("Copper node, mined standing up. VFX: harvest_hit on the front strike face at mid height "
                   "(orange copper + grey-brown rock chips and dust on each tool strike); harvest_deplete at the "
                   "base centre (big chip burst when the node empties, then swap to CopperNodeDepleted); "
                   "ore_glint just off the crown of each of the four copper gems (warm orange twinkles, copper "
                   "is metallic; small emitter box so no glint spawns inside the gem)."))
    out.append(hero)

    # -- parts -----------------------------------------------------------------
    bm = new_bm()
    host_rock(bm)
    obj, _ = to_asset(fk, "CopperNodeHostRock", bm)
    out.append(kit.tag(obj, "part", collision="hull",
                       notes="The bare host rock, without copper or patina, for kit-bashing."))

    for name, pts, seed in (("CopperInsert", gem_points(1.7, 1.2, 511, squash=0.82, n=6), 511),
                            ("CopperInsertSmall", small_points(0.85, 504), 504),
                            ("CopperInsertShard", shard_points(0.75, 505), 505)):
        bm = new_bm()
        f = gem(bm, pts, seed, cap=True, grp=1)
        bm.normal_update()
        lo = min(v.co.z for v in bm.verts)
        hi = max(v.co.z for v in bm.verts)
        spatter(bm, 1, Vector((0.15, -0.3, lo + (hi - lo) * 0.3)), Vector((0.3, -1, -0.2)),
                (hi - lo) * 0.45, 4, 0.7, random.Random(seed))
        obj, _ = to_asset(fk, name, bm)
        out.append(kit.tag(obj, "part", collision="none",
                           notes="Copper gem insert, flat base at z=0: sink about 40-50% of it into a "
                                 "rock face along the face normal (it rides on the host's collision). "
                                 "Add an ore_glint socket just off its crown when placed."))

    for name, (loc, size, seed, yaw), coll in (("CopperNodeBaseRock", BASE_ROCKS[0], "hull"),
                                               ("CopperNodeBaseRockSmall", SMALL_BASE_ROCK, "none")):
        bm = new_bm()
        f = rock_piece(bm, size, seed, (0.0, 0.0), yaw)
        drop_bottom(bm, f)
        obj, _ = to_asset(fk, name, bm)
        out.append(kit.tag(obj, "part", collision=coll, notes="Small base rock for the node's foot."))

    # -- drops -----------------------------------------------------------------
    for name, dims, seed in (("CopperOre", (1.4, 1.25, 1.05), 71),
                             ("CopperOreSmall", (1.2, 1.05, 1.0), 74)):
        out.append(kit.tag(ore_chunk(fk, name, dims, seed), "drop", collision="box",
                           notes="Copper ore item the player gets: faceted orange chunk with teal patina."))

    # -- depleted --------------------------------------------------------------
    out.append(kit.tag(depleted(fk), "depleted", collision="hull",
                       notes="Shown after the node is mined out; same footprint as CopperNode."))
    return out


def ore_chunk(fk, name, dims, seed):
    """An irregular faceted copper lump: the hull of a few jittered points on a
    squashed ellipsoid (no box symmetry), flat-ish underside, mottled teal on
    one lower side."""
    rng = random.Random(seed)
    sx, sy, sz = dims
    pts = []
    n = 18
    ga = math.pi * (3 - math.sqrt(5))
    for i in range(n):
        z = 1 - 2 * (i + 0.5) / n
        r = math.sqrt(1 - z * z)
        th = ga * i + rng.uniform(-0.3, 0.3)
        s = rng.uniform(0.84, 1.1)
        pts.append(Vector((r * math.cos(th) * sx / 2 * s, r * math.sin(th) * sy / 2 * s,
                           (max(-0.55, z) + 0.55) / 1.55 * sz * s)))
    bm = new_bm()
    faces = hull(bm, pts)
    # scale to the exact spec extents (the sampled points never reach the poles)
    xs, ys, zs = ([v.co[k] for v in bm.verts] for k in range(3))
    S = Matrix.Diagonal((sx / (max(xs) - min(xs)), sy / (max(ys) - min(ys)), sz / (max(zs) - min(zs)), 1.0))
    bmesh.ops.translate(bm, vec=Vector((-(min(xs) + max(xs)) / 2, -(min(ys) + max(ys)) / 2, -min(zs))),
                        verts=bm.verts)
    bmesh.ops.transform(bm, matrix=S, verts=bm.verts)
    bm.normal_update()
    paint_gem(bm, bm.faces[:], seed)
    # mottled teal only on the lower-left (-X, front) side: two irregular blotches, one low
    side = Vector((-0.85, -0.6, -0.35)).normalized()
    hit = Vector((-sx * 0.36, -sy * 0.28, sz * 0.3))
    spatter(bm, 0, hit, side, (sx + sy) * 0.17, 8, 0.85, rng)
    spatter(bm, 0, hit + Vector((0.22, -0.12, -0.22)), side, (sx + sy) * 0.11, 5, 0.85, rng)
    obj, _ = to_asset(fk, name, bm)
    return obj


def depleted(fk):
    bm = new_bm()
    f = rock_piece(bm, (5.4, 4.5, 1.7), 81, (0.05, 0.0), 0.1, n=30, p=2.3, jitter=0.08, zc=0.25,
                   taper=0.3, low=1.5, ring=10, tilt=0.3)
    drop_bottom(bm, f)
    for loc, size, seed, yaw in ((((-2.75, -0.9), (1.45, 1.3, 0.9), 82, 0.5)),
                                 (((2.8, -0.65), (1.15, 1.0, 0.75), 83, 1.4)),
                                 (((2.25, 1.8), (0.9, 0.8, 0.55), 84, 2.0))):
        f = rock_piece(bm, size, seed, loc, yaw)
        drop_bottom(bm, f)
    obj, _ = to_asset(fk, "CopperNodeDepleted", bm)
    return obj
