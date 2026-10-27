"""W01 row 4: Pebble Scatter - small stones and slabs used to detail the ground.

Hero PebbleScatter (about 10 x 8 studs, under 2.5 tall): a flat slab, a wedge
rock with a moss cap, a round rock, a taller pebble and small stones, with leafy
clumps and white flowers packed against their bases. Parts: PebbleFlatSlab,
Pebble, PebbleWedgeRock, PebbleRoundRock, PebbleSmallStone. Variants:
PebbleScatterSparse (3 pieces), PebbleScatterMedium (5 pieces),
PebbleScatterDense (8+ pieces).

Every stone is hewn the same way as sheet 06: a superellipsoid volume cut by one
tangent plane per facet direction, which gives big chiselled planes. Each
material is ONE flat colour (stone w01_rock, moss w01_moss, clumps w01_leaf,
flowers flower_white/flower_yellow) with a small random Tint: the light tops and
dark sides of the reference are lighting, and the sheet's brown swatch is the
stones' shadow side, not a material.
Moss (one lime colour, w01_moss) is a lumpy pad draped on the stone: rings of
points ray-cast onto the surface (down onto the top, sideways onto a face for
the lobes that hang over an edge), lifted off it and hulled, so it follows the
stone and never overhangs.
Each leafy clump is a fat round dome of 6-7 overlapping faceted lobes (18 tris
each) with a crown of round 10-tri leaves fanning out of the top and a few at
the rim, daisies on top. Clumps are attached to a stone's foot by side angle,
so their inner lobes run into its base and they hug it with no gap.
No VFX: the reference shows none for loose stones.
"""

import math
import random

import bmesh
from mathutils import Matrix, Vector
from mathutils.bvhtree import BVHTree

SUBJECT = "PebbleScatter"
ROW = 4
PALETTE = {
    "w01_rock": ("#B29F98", 0.9, 0, 0),  # THE ONLY stone colour on the whole sheet: warm mauve-beige granite of every boulder, spire, cluster rock, slab and pebble (lit mid-tone; median of all rock pixels across the 4 hero cells is #B29F96-#B5A097). The swatches' blue-grey (#8E8E9E) and pale beige (#CAB2A8) are its shadow and lit sides, NOT materials: drop w01_boulder_beige, w01_boulder_blue, w01_rock_light, w01_rock_cool, w01_rock_warm, kit_rock(_light/_dark) and stone. Same value in every module that declares it (this replaces the old #8E7C78). Variety only via a small random Tint (<=1.25x spread), never by face direction.
    "w01_moss": ("#ADBB14", 0.9, 0, 0),  # Lime-yellow moss: moss caps, moss pads, streaks/smudges and thin decals on rock facets (median moss pixel #ADBB08; swatches 3 #8DA418 and 4 #D7CD29 are its shadow and lit sides). Replaces moss, moss_light, moss_dark.
    "w01_leaf": ("#7AAB1E", 0.8, 0, 0),  # Clover / round-leaf ground clumps banked at rock feet and in crevices: a greener, slightly deeper green than the moss so the two read apart. Replaces leaf, leaf_light and grass_light on this sheet (one key for all leafy clumps).
}
# Also used, from the shared flintkit PALETTE (existing keys, not redeclared):
#   "flower_white": ("#F5F2EA", 0.7, 0, 0),  # five-petal white daisy petals in the leaf clumps
#   "flower_yellow": ("#F2C230", 0.7, 0, 0),  # daisy centres

PI = math.pi
TAU = 2 * PI
GA = PI * (3 - math.sqrt(5))
Z = Vector((0, 0, 1))

# material indices of a stone bmesh, before it is appended into an Asset
MATS = ["w01_rock", "w01_moss"]
ROCK, MOSS = range(2)
LEAF = "w01_leaf"

# stone kinds: full extents at scale 1 and the hewing recipe
KINDS = {
    # long, low, hexagonal slab with one broad flat top and chamfered rims
    "slab": dict(size=(5.0, 3.2, 1.15), n=52, p=3.6, taper=0.16, sink=0.05, tilt=0.07, jitter=0.14,
                 top=((0.03, -0.05, 1.0), 0.8), lobes=((3, 0.05, 0.4), (2, 0.06, 1.2)),
                 chamfer=((9, 30, 0.8), (5, 5, 0.42))),
    # blocky stone, steep sides, top sloping down to the front (the wedge)
    "wedge": dict(size=(2.8, 2.3, 1.6), n=30, p=3.8, taper=0.22, sink=0.04, tilt=0.1, jitter=0.18,
                  top=((0.04, -0.27, 1.0), 0.74)),
    # rounded, faceted stone
    "round": dict(size=(1.5, 1.4, 1.25), n=44, p=2.1, taper=0.22, sink=0.14, tilt=0.12, jitter=0.16),
    # taller, domed pebble
    "pebble": dict(size=(1.4, 1.25, 1.05), n=38, p=2.3, taper=0.3, sink=0.12, tilt=0.12, jitter=0.16),
    # low stone with a flat top
    "small": dict(size=(1.2, 1.0, 0.8), n=32, p=2.6, taper=0.30, sink=0.08, tilt=0.1, jitter=0.14,
                  top=((0.0, -0.08, 1.0), 0.80)),
}

# clumps use one leaf colour (w01_leaf) for lobes and leaves alike: the
# reference's lime tops and darker undersides are lighting, not a second green


# ---------------------------------------------------------------------------
# Hewn stones (adapted from build_06_rocks_runes_camp.hewn_bm)
# ---------------------------------------------------------------------------


def plane_cut(bm, n, co):
    """Keep the side of the plane opposite its normal and cap the hole."""
    geom = bm.verts[:] + bm.edges[:] + bm.faces[:]
    bmesh.ops.bisect_plane(bm, geom=geom, dist=1e-5, plane_co=co, plane_no=n, clear_outer=True)
    bnd = [e for e in bm.edges if e.is_boundary]
    if bnd:
        bmesh.ops.contextual_create(bm, geom=bnd)


def hewn(size, n=24, p=2.4, taper=0.0, sink=0.1, tilt=0.08, jitter=0.1, seed=0, top=None, lobes=(),
         chamfer=()):
    """Chiselled stone with full extents ~size, base on z=0, centred on the origin."""
    rng = random.Random(seed)
    sx, sy, sz = size
    rx, ry = sx / 2, sy / 2
    rz = sz / (2 - sink)
    zc = rz * (1 - sink)
    C = Vector((0, 0, zc))

    def F(P):
        tf = max(0.2, 1 - taper * max(0.0, P.z) / sz)
        x = P.x / (rx * tf)
        y = P.y / (ry * tf)
        z = (P.z - zc) / rz
        if lobes:
            th = math.atan2(y, x)
            w = 1 + sum(amp * math.cos(k * th - ph) for k, amp, ph in lobes)
            x, y = x / w, y / w
        return (abs(x) ** p + abs(y) ** p + abs(z) ** p) ** (1 / p)

    bm = bmesh.new()
    bmesh.ops.create_cube(bm, size=1.0)
    for v in bm.verts:
        v.co = Vector((v.co.x * sx * 1.3, v.co.y * sy * 1.3, (v.co.z + 0.5) * sz * 1.1))
    if top:
        nrm, h = top
        plane_cut(bm, Vector(nrm).normalized(), Vector((0, 0, h * sz)))
        for k, tdeg, r0 in chamfer:  # rings of tilted plates round the flat top
            for i in range(k):
                ph = TAU * (i + rng.uniform(-0.25, 0.25)) / k
                th = math.radians(tdeg * rng.uniform(0.8, 1.2))
                d = Vector((math.cos(ph), math.sin(ph), 0))
                nn = (Z * math.cos(th) + d * math.sin(th)).normalized()
                pt = Vector((d.x * rx * r0 * rng.uniform(0.92, 1.08), d.y * ry * r0 * rng.uniform(0.92, 1.08),
                             h * sz))
                plane_cut(bm, nn, pt)
    planes = []
    for i in range(n):
        z = 1 - 2 * (i + 0.5) / n
        if z < -0.35:
            continue
        rr = math.sqrt(max(0.0, 1 - z * z))
        th = GA * i + rng.uniform(-0.3, 0.3)
        d = Vector((rr * math.cos(th) * rx, rr * math.sin(th) * ry, z * rz)).normalized()
        lo, hi = 0.0, 3 * max(sx, sy, sz)
        for _ in range(36):
            t = (lo + hi) / 2
            if F(C + d * t) < 1:
                lo = t
            else:
                hi = t
        P = C + d * lo
        e = 1e-3
        g = Vector((F(P + Vector((e, 0, 0))) - F(P - Vector((e, 0, 0))),
                    F(P + Vector((0, e, 0))) - F(P - Vector((0, e, 0))),
                    F(P + Vector((0, 0, e))) - F(P - Vector((0, 0, e))))).normalized()
        g = (g + Vector((rng.uniform(-1, 1), rng.uniform(-1, 1), rng.uniform(-1, 1))) * tilt).normalized()
        P = P - g * rng.uniform(0, jitter) * min(rx, ry, rz)
        planes.append((g, P))
    rng.shuffle(planes)
    for g, P in planes:
        plane_cut(bm, g, P)
    bmesh.ops.dissolve_degenerate(bm, dist=0.05 * min(size), edges=bm.edges[:])
    bmesh.ops.dissolve_limit(bm, angle_limit=math.radians(2.0), verts=bm.verts[:], edges=bm.edges[:])
    for v in bm.verts:
        v.co.z = max(v.co.z, 0.0)
    # fit to the exact extents, centred, base on z=0
    xs = [v.co.x for v in bm.verts]
    ys = [v.co.y for v in bm.verts]
    zs = [v.co.z for v in bm.verts]
    s = (sx / (max(xs) - min(xs)), sy / (max(ys) - min(ys)), sz / (max(zs) - min(zs)))
    cx, cy = (max(xs) + min(xs)) / 2, (max(ys) + min(ys)) / 2
    for v in bm.verts:
        v.co = Vector(((v.co.x - cx) * s[0], (v.co.y - cy) * s[1], v.co.z * s[2]))
    # the buried underside is never seen: drop it
    bottom = [f for f in bm.faces if all(v.co.z < 1e-3 for v in f.verts)]
    bmesh.ops.delete(bm, geom=bottom, context="FACES_ONLY")
    bmesh.ops.recalc_face_normals(bm, faces=bm.faces[:])
    return bm


def tint_layer(bm):
    return bm.loops.layers.float_color.get("Tint") or bm.loops.layers.float_color.new("Tint")


def put(bm, f, mi, t):
    tl = tint_layer(bm)
    f.material_index = mi
    f.smooth = False
    for lp in f.loops:
        lp[tl] = (t, t, t, 1.0)


def paint_stone(bm, rng):
    """One flat stone colour; the light tops and dark sides of the reference are
    lighting. Tint is a small random per-facet variation only."""
    for f in bm.faces:
        put(bm, f, ROCK, rng.uniform(0.94, 1.06))


def hull_bm(points):
    """Convex hull of points as a new bmesh (interior/unused points dropped)."""
    bm = bmesh.new()
    for p in points:
        bm.verts.new(p)
    res = bmesh.ops.convex_hull(bm, input=bm.verts[:])
    kill = [g for g in res["geom_interior"] + res["geom_unused"] if isinstance(g, bmesh.types.BMVert)]
    if kill:
        bmesh.ops.delete(bm, geom=list(set(kill)), context="VERTS")
    bmesh.ops.recalc_face_normals(bm, faces=bm.faces[:])
    bm.normal_update()
    return bm


# ---------------------------------------------------------------------------
# Moss draped on the stones
# ---------------------------------------------------------------------------


def pad(bvh, origin, ray, t1, t2, R, thick, rng, lobes=5, rings=None, min_dot=0.05):
    """Lumpy moss pad: rings of points cast along `ray` onto the stone, lifted
    off it along the hit normal (thick in the middle, a thin lip at the lobed
    rim), plus rim anchors just under the surface; hulled, buried faces dropped.
    Returns a bmesh painted with MATS indices, or None."""
    ray = ray.normalized()
    out = -ray
    rings = rings or ((0.0, 1, 1.0), (0.42, 6, 0.95), (0.76, 9, 0.7), (1.0, 12, 0.18))
    lob_ph = rng.uniform(0, TAU)
    pts, anchors = [], []
    for frac, cnt, lift in rings:
        ph = rng.uniform(0, TAU)
        for k in range(cnt):
            th = ph + TAU * (k + rng.uniform(-0.22, 0.22)) / cnt
            rr = frac * (1 + 0.24 * math.cos(lobes * th + lob_ph)) * rng.uniform(0.88, 1.08)
            o = origin + t1 * math.cos(th) * R[0] * rr + t2 * math.sin(th) * R[1] * rr
            hit = bvh.ray_cast(o, ray)
            if hit[0] is None:
                continue
            loc, nrm = hit[0], hit[1]
            if nrm.dot(out) < min_dot:
                continue
            pts.append(loc + nrm * thick * lift * rng.uniform(0.8, 1.25))
            if frac >= 0.99:
                anchors.append(loc - nrm * 0.03)
    if len(pts) < 5:
        return None
    bm = hull_bm(pts + anchors)
    akeys = {(round(p.x, 5), round(p.y, 5), round(p.z, 5)) for p in anchors}

    def is_anchor(v):
        return (round(v.co.x, 5), round(v.co.y, 5), round(v.co.z, 5)) in akeys

    buried = [f for f in bm.faces if all(is_anchor(v) for v in f.verts) or f.normal.dot(out) < -0.25]
    bmesh.ops.delete(bm, geom=buried, context="FACES_ONLY")
    loose = [v for v in bm.verts if not v.link_faces]
    if loose:
        bmesh.ops.delete(bm, geom=loose, context="VERTS")
    for v in bm.verts:
        v.co.z = max(v.co.z, 0.0)
    bm.normal_update()
    for f in bm.faces:  # one lime moss colour (the sheet's moss swatch), random Tint only
        put(bm, f, MOSS, rng.uniform(0.95, 1.05))
    return bm


def edge_z(bvh, c, dirv, zmax):
    """Height of a stone's top edge above point c, seen from direction dirv."""
    z = zmax
    while z > 0.05:
        hit = bvh.ray_cast(c + dirv * 20 + Z * z, -dirv)
        if hit[0] is not None and hit[1].dot(dirv) > 0.5:  # the side face, not the top
            return z
        z -= 0.03
    return None


def mosses_for(bm, spec, rng, size):
    """Build the moss pads of one stone. spec items:
    ("top", u, v, rx, ry, thick)       cast down; u, v in fractions of the half extents
    ("drape", deg, off, rw, rh, thick) a lobe hanging over the edge on the side at
                                       angle deg (270 = front), off studs along it."""
    bvh = BVHTree.FromBMesh(bm)
    out = []
    for it in spec:
        if it[0] == "top":
            _, u, v, rx, ry, th = it
            o = Vector((u * size[0] / 2, v * size[1] / 2, size[2] + 3))
            X, Y = Vector((1, 0, 0)), Vector((0, 1, 0))
            pb = pad(bvh, o, -Z, X, Y, (rx, ry), th, rng)
            if pb:
                out.append(pb)
            for _ in range(2 if min(rx, ry) > 0.6 else 1 if min(rx, ry) > 0.3 else 0):  # chunky lumps
                ang = rng.uniform(0, TAU)
                rr = rng.uniform(0.1, 0.45)
                lo = o + X * math.cos(ang) * rx * rr + Y * math.sin(ang) * ry * rr
                lr = rng.uniform(0.35, 0.5)
                lb = pad(bvh, lo, -Z, X, Y, (rx * lr, ry * lr), th * 1.35, rng, lobes=3,
                         rings=((0.0, 1, 0.95), (0.5, 7, 0.92), (1.0, 9, 0.3)))
                if lb:
                    out.append(lb)
        else:
            _, deg, off, rw, rh, th = it
            a = math.radians(deg)
            dirv = Vector((math.cos(a), math.sin(a), 0))
            tang = Vector((-dirv.y, dirv.x, 0))
            c = tang * off
            ze = edge_z(bvh, c, dirv, size[2] + 0.1)
            if ze is None:
                continue
            hit = bvh.ray_cast(c + dirv * 20 + Z * ze, -dirv)
            # cast diagonally (down and in) so one lobe covers the rim, its
            # chamfer and the face below it without a gap
            ray = (-dirv - Z * 0.8).normalized()
            t2 = ray.cross(tang).normalized()
            if t2.z < 0:
                t2 = -t2
            o = hit[0] - Z * rh * 0.35 - ray * 10
            pb = pad(bvh, o, ray, tang, t2, (rw, rh), th, rng, lobes=3,
                     rings=((0.0, 1, 1.0), (0.5, 6, 0.85), (1.0, 9, 0.2)), min_dot=0.15)
            if pb:
                out.append(pb)
    return out


# ---------------------------------------------------------------------------
# Asset assembly
# ---------------------------------------------------------------------------


def paint(a, faces, mat, tint=1.0, var=0.05):
    mi = a._mi(mat)
    for f in faces:
        f.material_index = mi
        f.smooth = False
        t = tint * (1.0 + a.rng.uniform(-var, var))
        for loop in f.loops:
            loop[a.tint_layer] = (t, t, t, 1.0)


def append_bm(a, bm):
    tl = bm.loops.layers.float_color.get("Tint")
    vmap = {v: a.bm.verts.new(v.co) for v in bm.verts}
    for f in bm.faces:
        try:
            nf = a.bm.faces.new([vmap[v] for v in f.verts])
        except ValueError:
            continue
        t = f.loops[0][tl][0] if tl else 1.0
        paint(a, [nf], MATS[f.material_index], t, 0.0)
    bm.free()


def round_leaf(a, base, d, L, mat, W=None, droop=0.22, cup=0.16):
    """Round low-poly leaf (10 tris): a fan of six facets round a raised centre
    over a flat underside, its tip drooping."""
    bm = a.bm
    d = Vector(d).normalized()
    side = d.cross(Z)
    if side.length < 1e-4:
        side = Vector((1, 0, 0))
    side.normalize()
    u = side.cross(d).normalized()
    if u.z < 0:
        u = -u
    W = W if W is not None else L * 0.54
    base = Vector(base)

    def at(t, s, lift=0.0):
        return base + d * L * t + side * W * s + u * (lift - droop * L * t * t)

    B = bm.verts.new(at(0.0, 0.0))
    L1, R1 = bm.verts.new(at(0.32, 0.86)), bm.verts.new(at(0.32, -0.86))
    L2, R2 = bm.verts.new(at(0.76, 0.8)), bm.verts.new(at(0.76, -0.8))
    T = bm.verts.new(at(1.0, 0.0))
    M = bm.verts.new(at(0.52, 0.0, cup * W + 0.015))
    vs = (B, L1, L2, T, R2, R1, M)
    for v in vs:
        v.co.z = max(v.co.z, 0.0)
    top = [bm.faces.new(f) for f in ((B, L1, M), (L1, L2, M), (L2, T, M), (T, R2, M), (R2, R1, M), (R1, B, M))]
    under = [bm.faces.new((B, R1, R2, T, L2, L1))]
    bmesh.ops.recalc_face_normals(bm, faces=top + under)
    t = 1.0 + a.rng.uniform(-0.07, 0.07)
    paint(a, top, mat, t, 0.03)
    paint(a, under, mat, t, 0.03)
    return vs


def flower(a, c, R=0.2, n=(0, -0.25, 1.0)):
    """Flat five-petal white flower with a yellow centre."""
    bm = a.bm
    n = Vector(n).normalized()
    t1 = n.cross(Z if abs(n.z) < 0.95 else Vector((1, 0, 0))).normalized()
    if t1.length < 1e-4:
        t1 = Vector((1, 0, 0))
    t2 = n.cross(t1)
    c = Vector(c)
    rot0 = a.rng.uniform(0, TAU)
    ring = []
    w = TAU / 5
    for i in range(5):
        for off, rr in ((-0.5, 0.35), (-0.22, 1.0), (0.22, 1.0)):
            ang = rot0 + (i + off) * w
            ring.append(bm.verts.new(c + (math.cos(ang) * t1 + math.sin(ang) * t2) * R * rr + n * 0.1 * R * rr))
    top = bm.verts.new(c + n * 0.03)
    bot = bm.verts.new(c - n * 0.05)
    faces = []
    m = len(ring)
    for i in range(m):
        j = (i + 1) % m
        faces.append(bm.faces.new((top, ring[i], ring[j])))
        faces.append(bm.faces.new((bot, ring[j], ring[i])))
    paint(a, faces, "flower_white", 1.0, 0.03)
    a.cyl(R * 0.32, R * 0.08, R * 0.2, 5, cap=False, loc=tuple(c + n * 0.02),
          rot=n.to_track_quat("Z", "Y").to_euler(), mat="flower_yellow", tint=1.0)


def inside(rocks, p):
    """Point inside any stone: an upward ray crosses its (open-bottomed) shell an
    odd number of times."""
    for bvh in rocks:
        o = Vector(p)
        hits = 0
        for _ in range(6):
            loc = bvh.ray_cast(o, Z)[0]
            if loc is None:
                break
            hits += 1
            o = loc + Z * 1e-4
        if hits % 2:
            return True
    return False


def oriented_face(a, verts, inner):
    """New face whose normal points away from the point `inner`."""
    f = a.bm.faces.new(verts)
    f.normal_update()
    if f.normal.dot(f.calc_center_median() - inner) < 0:
        f.normal_flip()
    return f


def lobe(a, c, r, h, rng, mat, seg=6):
    """One rounded leafy lobe (18 tris): a faceted dome standing on the ground,
    a skirt ring at z=0, a mid ring turned half a step and an apex."""
    rot = rng.uniform(0, TAU)
    skirt, mid = [], []
    for k in range(seg):
        th = rot + TAU * k / seg
        rr = r * rng.uniform(0.9, 1.08)
        skirt.append(a.bm.verts.new((c.x + math.cos(th) * rr, c.y + math.sin(th) * rr, 0.0)))
        th2 = rot + TAU * (k + 0.5) / seg
        rr2 = r * 0.8 * rng.uniform(0.92, 1.08)
        mid.append(a.bm.verts.new((c.x + math.cos(th2) * rr2, c.y + math.sin(th2) * rr2,
                                   h * 0.6 * rng.uniform(0.92, 1.08))))
    apex = a.bm.verts.new((c.x + rng.uniform(-0.12, 0.12) * r, c.y + rng.uniform(-0.12, 0.12) * r, h))
    inner = Vector((c.x, c.y, h * 0.3))
    faces = []
    for k in range(seg):
        j = (k + 1) % seg
        faces.append(oriented_face(a, (apex, mid[k], mid[j]), inner))
        faces.append(oriented_face(a, (skirt[k], skirt[j], mid[k]), inner))
        faces.append(oriented_face(a, (mid[k], skirt[j], mid[j]), inner))
    paint(a, faces, mat, rng.uniform(0.94, 1.06), 0.03)


def clump(a, x, y, s=1.0, flowers=0, seed=0, rocks=(), mat=LEAF):
    """Fat round leafy clump about 1.4*s across and 0.8*s tall: a tall centre
    lobe ringed by 5-6 overlapping lower lobes (so it reads as one round dome),
    a crown of round leaves fanning up and out of the top and a few splaying
    out at the rim (the rosette of the reference), daisies on top. Lobes may
    run into a stone so the clump hugs its base; a lobe or leaf that would end
    up wholly inside a stone is skipped."""
    rng = random.Random(seed)
    domes = [(Vector((x, y, 0)), 0.42 * s, 0.74 * s)]
    n = 5 if s < 0.9 else 6
    a0 = rng.uniform(0, TAU)
    for i in range(n):
        az = a0 + TAU * (i + rng.uniform(-0.15, 0.15)) / n
        d = 0.38 * s * rng.uniform(0.85, 1.1)
        domes.append((Vector((x + math.cos(az) * d, y + math.sin(az) * d, 0)),
                      0.33 * s * rng.uniform(0.9, 1.1), 0.5 * s * rng.uniform(0.85, 1.15)))
    kept = []
    for c, r, h in domes:
        if rocks and inside(rocks, Vector((c.x, c.y, h * 0.85))):
            continue
        lobe(a, c, r, h, rng, mat)
        kept.append((c, r, h))

    def leaf_ok(base, dv, L):
        return not rocks or not (inside(rocks, base + dv * L * 0.5) or inside(rocks, base + dv * L))

    for i in range(5):  # crown: leaves fanning up and out of the top of the dome
        az = a0 + 0.4 + TAU * i / 5 + rng.uniform(-0.25, 0.25)
        hd = Vector((math.cos(az), math.sin(az), 0))
        base = Vector((x, y, 0)) + hd * 0.08 * s + Z * 0.6 * s
        pitch = math.radians(rng.uniform(22, 38))
        dv = hd * math.cos(pitch) + Z * math.sin(pitch)
        L = 0.46 * s * rng.uniform(0.9, 1.1)
        if leaf_ok(base, dv, L):
            round_leaf(a, base, dv, L, mat, cup=0.3, droop=0.3)
    for i in range(3):  # leaves splaying out low at the rim
        az = a0 + TAU * (i + 0.5) / 3 + rng.uniform(-0.3, 0.3)
        hd = Vector((math.cos(az), math.sin(az), 0))
        base = Vector((x, y, 0)) + hd * 0.5 * s + Z * 0.16 * s
        pitch = math.radians(rng.uniform(10, 24))
        dv = hd * math.cos(pitch) + Z * math.sin(pitch)
        L = 0.42 * s * rng.uniform(0.9, 1.1)
        if leaf_ok(base, dv, L):
            round_leaf(a, base, dv, L, mat, cup=0.3, droop=0.15)

    def height(px, py):
        best = 0.0
        for c, r, h in kept:
            dd = math.hypot(px - c.x, py - c.y) / r
            if dd < 1:
                best = max(best, h * (1 - dd ** 3.5))
        return best

    R = 0.32 * min(1.2, max(0.85, s))
    for i in range(flowers):
        az = a0 + 0.7 + TAU * i / max(1, flowers)
        rr = 0.1 * s if flowers == 1 else 0.24 * s
        px, py = x + math.cos(az) * rr, y + math.sin(az) * rr - 0.06 * s
        c = Vector((px, py, max(height(px, py), 0.62 * s) + 0.1 * s))
        flower(a, c, R=R, n=(rng.uniform(-0.25, 0.05), -0.45, 1.0))


def floor_clamp(a):
    for v in a.bm.verts:
        if v.co.z < 0.0:
            v.co.z = 0.0


def rim_point(bvh, c, ang, z, reach=20.0):
    """Where a horizontal ray from outside, aimed at the stone's axis c (x, y), meets it."""
    d = Vector((math.cos(ang), math.sin(ang), 0))
    hit = bvh.ray_cast(Vector((c.x, c.y, z)) + d * reach, -d)
    return (hit[0], d) if hit[0] is not None else (None, d)


def assemble(name, items, seed=0):
    """items: ("stone", kind, x, y, yaw_deg, scale, seed, mosses, clumps) or
    ("clump", x, y, size, flowers, seed). A stone's clumps are
    (world_angle_deg, size, flowers): each sits on the stone's foot on that side
    (270 = front), its centre a little outside the rim so its inner lobes run
    into the base. Stones go first so the clumps can avoid them."""
    import flintkit as fk  # noqa: E402  (on sys.path via build_kit)
    a = fk.Asset(name, "Rocks", seed=seed)
    rocks = []
    clumps = []
    for it in items:
        if it[0] != "stone":
            continue
        _, kind, x, y, yaw, sc, sd, mosses = it[:8]
        k = dict(KINDS[kind])
        base = k.pop("size")
        sc3 = sc if isinstance(sc, (tuple, list)) else (sc, sc, sc)
        size = tuple(b * s for b, s in zip(base, sc3))
        if max(size) < 0.8:  # chips: a handful of facets is all that reads
            k["n"] = 14
        bm = hewn(size, seed=sd, **k)
        rng = random.Random(sd * 7 + 3)
        pads = mosses_for(bm, mosses, rng, size)
        M = Matrix.Translation(Vector((x, y, 0))) @ Matrix.Rotation(math.radians(yaw), 4, "Z")
        for b in [bm] + pads:
            bmesh.ops.transform(b, matrix=M, verts=b.verts[:])
            b.normal_update()
        paint_stone(bm, rng)
        bvh = BVHTree.FromBMesh(bm)
        rocks.append(bvh)
        for j, (ang, cs, fl) in enumerate(it[8] if len(it) > 8 else ()):
            p, dv = rim_point(bvh, Vector((x, y)), math.radians(ang), 0.12)
            if p is not None:
                q = p + dv * 0.22 * cs
                clumps.append((q.x, q.y, cs, fl, sd * 10 + j))
        for b in pads:
            append_bm(a, b)
        append_bm(a, bm)
    for it in items:
        if it[0] == "clump":
            clumps.append(it[1:])
    for x, y, s, fl, sd in clumps:
        clump(a, x, y, s, fl, sd, rocks=rocks)
    floor_clamp(a)
    bmesh.ops.remove_doubles(a.bm, verts=a.bm.verts, dist=1e-5)
    return a.finish()


# ---------------------------------------------------------------------------
# Layouts (studs; front is -Y, left is -X)
# ---------------------------------------------------------------------------

# stone: ("stone", kind, x, y, yaw_deg, scale, seed, [moss pads], [clumps (world_angle_deg, size, flowers)])
#   moss pads: ("top", u, v, rx, ry, thick) | ("drape", side_deg, offset, rw, rh, thick)
# clump: ("clump", x, y, size, flowers, seed)

# the slab carries only one small patch, on its left end (the reference's
# wedge rock has the one real moss cap)
SLAB_MOSS = [("top", -0.8, -0.1, 0.45, 0.4, 0.12),      # small pad on the left end of the top
             ("drape", 180, 0.0, 0.3, 0.24, 0.09)]      # spilling down the left end

# the wedge's cap is a cluster of overlapping pads of different thickness, so it
# reads as a lumpy, irregular cushion, thickest in the middle
WEDGE_MOSS = [("top", -0.12, 0.1, 0.82, 0.7, 0.22),     # main cushion over most of the top
              ("top", 0.36, 0.3, 0.46, 0.4, 0.25),      # fat lump back-right
              ("top", 0.05, -0.32, 0.52, 0.34, 0.17),   # tongue toward the front edge
              ("drape", 270, -0.3, 0.36, 0.28, 0.1),    # broad tongue down the front face
              ("drape", 225, 0.0, 0.3, 0.26, 0.09)]     # spilling over the front-left corner

# The slab is turned a little diagonal and the wedge sits back, so the side
# view (from +X) shows the slab long with the pebble and wedge peeking over it.
HERO = [
    ("stone", "slab", -1.6, -0.7, -18, (1.06, 1.12, 1.08), 401, SLAB_MOSS,
     [(184, 1.25, 0), (236, 1.0, 1), (288, 0.95, 1), (126, 1.3, 2)]),
    ("stone", "pebble", -0.4, 2.6, 20, (1.75, 1.75, 1.95), 402, []),
    ("stone", "wedge", 3.1, 2.0, 8, 1.0, 403, WEDGE_MOSS, [(230, 0.9, 1)]),
    ("stone", "round", 2.4, -2.9, -25, (1.45, 1.4, 1.4), 404, [], [(160, 0.85, 0), (25, 0.9, 1)]),
    ("stone", "small", 1.7, 1.0, 30, 0.45, 405, []),
    ("stone", "small", 4.2, -0.9, -10, 0.42, 406, []),
]

SPARSE = [
    ("stone", "slab", -1.6, -0.6, -18, (0.55, 0.75, 0.95), 411, [("top", 0.7, 0.2, 0.22, 0.18, 0.06)],
     [(200, 0.85, 0), (290, 0.7, 0)]),
    ("stone", "wedge", 0.7, 1.7, 10, (0.8, 0.75, 0.8), 412, [("top", 0.3, 0.3, 0.3, 0.25, 0.08)]),
    ("stone", "round", 2.6, -0.5, -30, (1.2, 1.15, 1.05), 413, [], [(240, 0.65, 0)]),
    ("stone", "small", 0.2, -2.2, 15, 0.42, 414, []),
    ("stone", "small", -0.9, 1.6, 0, 0.3, 415, []),
    ("stone", "small", 3.8, -1.9, 40, 0.22, 416, []),
]

MEDIUM = [
    ("stone", "slab", -0.5, 0.2, -12, (0.82, 0.85, 1.0), 421, [("top", 0.65, 0.4, 0.3, 0.2, 0.08)],
     [(180, 1.15, 1), (240, 0.9, 0), (120, 0.95, 0)]),
    ("stone", "pebble", 0.3, 3.0, 15, (1.2, 1.15, 1.25), 422, []),
    ("stone", "round", -2.2, -2.7, 20, (1.05, 1.0, 0.9), 424, []),
    ("stone", "wedge", 2.9, 0.4, -5, (0.62, 0.6, 0.65), 425, [], [(330, 0.85, 0)]),
    ("stone", "round", 1.3, -2.8, -10, (1.25, 1.1, 0.85), 426, [], [(60, 0.8, 1)]),
    ("stone", "small", 2.0, 2.3, 10, 0.3, 427, []),
    ("stone", "small", -1.5, -1.6, 30, 0.25, 428, []),
]

DENSE = [
    ("stone", "slab", -0.6, 0.2, -10, (0.95, 0.95, 1.1), 431, [("top", 0.7, 0.55, 0.28, 0.2, 0.08)],
     [(175, 1.25, 1), (215, 1.0, 0), (255, 0.95, 1), (130, 1.05, 0)]),
    ("stone", "pebble", 0.4, 3.1, 25, (1.45, 1.4, 1.45), 432, [], [(150, 1.0, 1)]),
    ("stone", "small", -1.3, 2.7, 10, 0.55, 433, []),
    ("stone", "small", 2.9, 1.8, -25, 0.6, 434, [], [(30, 1.0, 1)]),
    ("stone", "wedge", 2.9, -0.6, -12, (0.8, 0.75, 0.85), 435, [], [(320, 0.9, 1), (200, 0.8, 0)]),
    ("stone", "round", 0.6, -2.8, 10, (1.6, 1.35, 1.1), 436, [], [(250, 0.8, 0)]),
    ("stone", "round", 4.3, -1.9, -20, (0.9, 0.85, 0.8), 437, []),
    ("stone", "small", -3.4, -2.2, 0, 0.45, 438, [], [(300, 0.7, 1)]),
    ("stone", "small", -2.4, -2.9, 30, 0.35, 439, []),
]


def build(kit):
    out = []
    hero = assemble("PebbleScatter", HERO, seed=4)
    out.append(kit.tag(hero, "hero", collision="none",
                       notes="slab, wedge, round rock, pebble, small stones; moss, leafy clumps, white flowers"))
    for name, items, sd, note in (("PebbleScatterSparse", SPARSE, 41, "3 pieces"),
                                  ("PebbleScatterMedium", MEDIUM, 42, "5 pieces"),
                                  ("PebbleScatterDense", DENSE, 43, "8+ pieces")):
        out.append(kit.tag(assemble(name, items, seed=sd), "variant", collision="none", notes=note))
    parts = [
        ("PebbleFlatSlab", [("stone", "slab", 0, 0, 0, 1.0, 441, [])], "hull", ""),
        ("Pebble", [("stone", "pebble", 0, 0, 0, 1.0, 442, [])], "none", ""),
        ("PebbleWedgeRock", [("stone", "wedge", 0, 0, 0, 1.0, 443, WEDGE_MOSS)], "none",
         "knee high (2.8 x 2.3 x 1.6): map placement may override collision to hull when it stands alone"),
        ("PebbleRoundRock", [("stone", "round", 0, 0, 0, 1.0, 444, [])], "none", ""),
        ("PebbleSmallStone", [("stone", "small", 0, 0, 0, 1.0, 445, [])], "none", ""),
    ]
    for name, items, col, note in parts:
        out.append(kit.tag(assemble(name, items, seed=sum(map(ord, name))), "part", collision=col, notes=note))
    return out
