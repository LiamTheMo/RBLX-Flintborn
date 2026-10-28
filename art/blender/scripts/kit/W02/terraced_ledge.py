"""W02 row 2: TERRACED LEDGE, "two broad flat walkable levels".

A 32 x 32 terrace on the shared W02 height module: a lower grass shelf on the
front half with its top at z=12 and an upper ledge on the back half with its top
at z=24 (CliffWall's top, so the two join). Each tier's front is a band of tall,
narrow, vertical faceted rock columns (convex hulls of jittered rings, 3-6 studs
wide) in the CliffWall tones, with pointed leaning shards at the foot of the
lower band. The upper tier is inset and its left end steps back, so the lower
grass wraps round it; a tall filler rock closes the inside corner of the step.

Both decks use the shared W02 grass cap: 0.6 of grass over a 0.4 w02_earth band,
a scalloped lip overhanging the rock 0.3-0.8, toned patches, round bush clumps
at the corners and edges, pale pebbles and white / yellow flower dots. Grass
streaks drip down the rock faces. The back (+Y) face is the shared flat
w02_connector plate (inset 0.5) with 1.5 x 0.5 x 0.4 tabs at 8-stud spacing.

Assets: TerracedLedge (hero); parts TerracedLedgeUpperCap,
TerracedLedgeLowerShelf, TerracedLedgeCornerFillerRock,
TerracedLedgeMainCliffBase; variants TerracedLedgeShallow, TerracedLedgeWide,
TerracedLedgeRampEnd. No VFX: the reference shows none.

Colours: ONE base colour per material (the runner's rule). All rock is
w02_ledge_rock (the reference's lit mid-tone), grass w02_grass, bushes, streaks
and tufts w02_bush, the ramp w02_path; light and dark come from the leaning,
tilted column facets and Roblox's lighting. The backing quads buried in the
columns are culled.

Top-view layout: the lower grass stops `gap` in front of the upper tier, a low
plinth of pale rock blocks fills that strip, and the upper grass starts
`front_in` behind the tier line, so a ~6-stud rock band separates the two
decks into two rectangles (the lower one with a tab running back into the
stepped-back notch, where the pointed filler rock stands).
"""

import bisect
import math
import random

import bmesh
from mathutils import Vector
from mathutils.geometry import delaunay_2d_cdt

SUBJECT = "TerracedLedge"
ROW = 2
# The W02 sheet palette, verbatim (shared by every W02 module).
PALETTE = {
    "w02_rock": ("#958482", 0.9, 0, 0),
    "w02_rock_light": ("#BBA090", 0.9, 0, 0),
    "w02_rock_cool": ("#686A7C", 0.9, 0, 0),
    "w02_rock_deep": ("#525A6E", 0.9, 0, 0),
    "w02_grass": ("#A9BE26", 0.95, 0, 0),
    "w02_grass_light": ("#C2D23A", 0.95, 0, 0),
    "w02_grass_dark": ("#789428", 0.95, 0, 0),
    "w02_earth": ("#9F6A47", 0.95, 0, 0),
    "w02_path": ("#E2A86E", 0.95, 0, 0),
    "w02_path_dark": ("#C48A52", 0.95, 0, 0),
    "w02_slab": ("#BFAEA8", 0.9, 0, 0),
    "w02_connector": ("#8A858A", 0.95, 0, 0),
    "w02_bush": ("#4F8A3B", 0.8, 0, 0),
    "w02_bush_light": ("#7DAF3E", 0.8, 0, 0),
    "w02_bush_dark": ("#30602C", 0.8, 0, 0),
    # terraced_ledge extra, sampled from the W02 row-2 reference: the lit
    # mid-tone of the column faces (front faces #A5928F-#BA9D8F). ONE colour
    # for all rock (the runner's rule): the reference's peach tops and blue-grey
    # crevices are lighting, so the shared light/cool/deep shades are not used.
    "w02_ledge_rock": ("#B09A92", 0.9, 0, 0),
}

# One base colour per material: every rock role maps to the one rock key, the
# grass, bush and path shades to their single base colour. Light and dark come
# from the facets and Roblox's lighting.
ROCK = LIGHT = COOL = DEEP = "w02_ledge_rock"
GRASS, EARTH = "w02_grass", "w02_earth"
GRASS_L = GRASS
PATH, CONN = "w02_path", "w02_connector"
PATH_D = PATH
BUSH = BUSH_L = BUSH_D = "w02_bush"
GRASS_D = BUSH           # streaks / tufts: the darker leafy green (not a shade of the grass hue)
TWO_TONE_OK = ("different materials, not shades: w02_ledge_rock (rock) vs w02_connector (flat man-made back "
               "plate) vs flower_white (flower dots); w02_grass (turf) vs flower_yellow (flower dots); "
               "w02_path (walkable dirt ramp) vs w02_earth (soil band under the grass caps)")
FLOWERS = ("flower_white", "flower_yellow")
Z = Vector((0, 0, 1))
TAU = 2 * math.pi


# ---------------------------------------------------------------------------
# mesh helpers
# ---------------------------------------------------------------------------


def paint(a, faces, mat, tint=1.0, var=0.03):
    mi = a._mi(mat)
    for f in faces:
        if not f.is_valid:
            continue
        f.material_index = mi
        f.smooth = False
        t = tint * (1.0 + a.rng.uniform(-var, var))
        for lp in f.loops:
            lp[a.tint_layer] = (t, t, t, 1.0)


def hull(a, pts, merge=3.0):
    """Convex hull of pts into the asset; returns its faces (normals outward)."""
    bm = a.bm
    vs = [bm.verts.new(p) for p in pts]
    res = bmesh.ops.convex_hull(bm, input=vs, use_existing_faces=False)
    junk = list({g for g in res["geom_interior"] + res["geom_unused"]
                 if isinstance(g, bmesh.types.BMVert) and g.is_valid})
    if junk:
        bmesh.ops.delete(bm, geom=junk, context="VERTS")
    vs = [v for v in vs if v.is_valid]
    faces = list({f for v in vs for f in v.link_faces})
    bmesh.ops.recalc_face_normals(bm, faces=faces)
    if merge:
        bmesh.ops.dissolve_limit(bm, angle_limit=math.radians(merge), verts=vs,
                                 edges=list({e for v in vs for e in v.link_edges}))
        vs = [v for v in vs if v.is_valid]
        faces = list({f for v in vs for f in v.link_faces})
    bm.normal_update()
    return faces


def face(a, verts, out=None):
    """New face; flipped so its normal points along `out` (if given)."""
    try:
        f = a.bm.faces.new(verts)
    except ValueError:
        return None
    f.normal_update()
    if out is not None and f.normal.dot(out) < 0:
        f.normal_flip()
    return f


class Piece:
    """A convex rock chunk: its faces and bounding planes (hidden-face cull and
    ray casts for streaks). n_out: the wall's outward direction (back faces of
    wall columns are dropped)."""

    def __init__(self, faces, kind="rock", n_out=None, keep_back=True):
        self.faces = faces
        self.kind = kind
        self.n_out = n_out
        self.keep_back = keep_back
        self.planes = [(f.normal.copy(), f.calc_center_median()) for f in faces]
        vs = [v.co for f in faces for v in f.verts]
        self.lo = Vector((min(v.x for v in vs), min(v.y for v in vs), min(v.z for v in vs))) if vs else None
        self.hi = Vector((max(v.x for v in vs), max(v.y for v in vs), max(v.z for v in vs))) if vs else None

    def contains(self, p, eps=0.02):
        if self.lo is None or not (self.lo.x <= p.x <= self.hi.x and self.lo.y <= p.y <= self.hi.y
                                   and self.lo.z <= p.z <= self.hi.z):
            return False
        return all(n.dot(p - c) < -eps for n, c in self.planes)

    def ray(self, o, d):
        t0, t1, n0 = -1e9, 1e9, None
        for n, c in self.planes:
            nd = n.dot(d)
            dist = n.dot(c - o)
            if abs(nd) < 1e-9:
                if dist < 0:
                    return None
                continue
            t = dist / nd
            if nd < 0:
                if t > t0:
                    t0, n0 = t, n
            elif t < t1:
                t1 = t
        if n0 is None or t0 > t1 or t0 < 0:
            return None
        return t0, n0


# ---------------------------------------------------------------------------
# 2D helpers
# ---------------------------------------------------------------------------


def V2(p):
    return Vector((p[0], p[1]))


def fillet(corners, r, step=0.8, closed=False):
    """Polyline with its interior corners rounded by arcs of radius r."""
    C = [V2(c) for c in corners]
    n = len(C)
    out = []
    for i in range(n):
        if not closed and (i == 0 or i == n - 1):
            out.append(C[i])
            continue
        P, A, B = C[i], C[i - 1], C[(i + 1) % n]
        d1, d2 = (A - P).normalized(), (B - P).normalized()
        th = math.acos(max(-1.0, min(1.0, d1.dot(d2))))
        if r <= 0 or th > math.pi - 1e-3 or th < 1e-3:
            out.append(P)
            continue
        t = min(r / math.tan(th / 2), 0.45 * (A - P).length, 0.45 * (B - P).length)
        rr = t * math.tan(th / 2)
        p1, p2 = P + d1 * t, P + d2 * t
        cen = P + (d1 + d2).normalized() * (rr / math.sin(th / 2))
        a1 = math.atan2(p1.y - cen.y, p1.x - cen.x)
        a2 = math.atan2(p2.y - cen.y, p2.x - cen.x)
        da = (a2 - a1 + math.pi) % TAU - math.pi
        k = max(2, int(abs(da) * rr / step) + 1)
        for s in range(k + 1):
            ang = a1 + da * s / k
            out.append(cen + Vector((math.cos(ang), math.sin(ang))) * rr)
    return out


class Path2:
    """Arc-length parametrised open polyline."""

    def __init__(self, pts):
        self.P = [V2(p) for p in pts]
        self.cum = [0.0]
        for k in range(len(self.P) - 1):
            self.cum.append(self.cum[-1] + (self.P[k + 1] - self.P[k]).length)
        self.L = self.cum[-1]

    def at(self, s):
        s = max(0.0, min(self.L, s))
        k = max(0, min(len(self.P) - 2, bisect.bisect_right(self.cum, s) - 1))
        seg = self.cum[k + 1] - self.cum[k]
        t = (s - self.cum[k]) / seg if seg > 1e-9 else 0.0
        return self.P[k].lerp(self.P[k + 1], t)

    def tan(self, s, h=0.6):
        d = self.at(s + h) - self.at(s - h)
        return d.normalized() if d.length > 1e-9 else Vector((1, 0))


def resample_closed(P, step):
    P = [V2(p) for p in P]
    out = []
    for k in range(len(P)):
        a, b = P[k], P[(k + 1) % len(P)]
        n = max(1, int(round((b - a).length / step)))
        for s in range(n):
            out.append(a + (b - a) * (s / n))
    return out


def normals_closed(P):
    """Outward normals of a CCW polygon."""
    n = len(P)
    out = []
    for i in range(n):
        t = P[(i + 1) % n] - P[i - 1]
        t = t.normalized() if t.length > 1e-9 else Vector((1, 0))
        out.append(Vector((t.y, -t.x)))
    return out


def inside(P, x, y):
    c = False
    n = len(P)
    for i in range(n):
        a, b = P[i - 1], P[i]
        if (a.y > y) != (b.y > y):
            xi = a.x + (y - a.y) * (b.x - a.x) / (b.y - a.y)
            if x < xi:
                c = not c
    return c


def edge_dist(P, x, y):
    p = Vector((x, y))
    best = 1e9
    for i in range(len(P)):
        a, b = P[i - 1], P[i]
        d = b - a
        t = max(0.0, min(1.0, (p - a).dot(d) / max(d.dot(d), 1e-12)))
        best = min(best, (a + d * t - p).length)
    return best


def fz(f, x, y):
    return f(x, y) if callable(f) else f


# ---------------------------------------------------------------------------
# rock
# ---------------------------------------------------------------------------


def tone(a, faces, rng, u=None, dom=None):
    """Orientation-free rock tones: the reference rock is a pale warm peach /
    mauve grey, so each chunk gets one dominant warm tone (about 62% peach
    w02_rock_light, 38% mauve w02_rock) that most of its faces keep, a sprinkle
    of the other warm tone and a few blue-grey w02_rock_cool facets (~10% of
    the area, mostly on the recessed crevice sides that face along the wall,
    both sides alike). w02_rock_deep is kept for the hidden backing only.
    Roblox's sun does the shading."""
    q = rng.random()
    dom = dom or (LIGHT if q < 0.52 else ROCK)
    other = ROCK if dom == LIGHT else LIGHT
    for f in sorted([f for f in faces if f.is_valid], key=lambda f: tuple(f.calc_center_median())):
        n = f.normal
        r = rng.random()
        side = abs(n.x * u.x + n.y * u.y) / max(1e-6, math.hypot(n.x, n.y)) if u is not None else 0.0
        if abs(n.z) < 0.5 and side > 0.85 and r < 0.18:
            m = COOL
        elif r < 0.8:
            m = dom
        elif r < 0.97:
            m = other
        else:
            m = COOL
        paint(a, [f], m, rng.uniform(0.96, 1.04), 0.0)


def column(b, c, u, w, d, z0, z1, rng, bulge=1.0, lean=0.3, keep_back=False, dom=None):
    """One tall faceted rock column. c: centre of its front line (x, y); u: unit
    tangent along the wall (the face looks to its right, n = (u.y, -u.x)); d:
    depth into the wall. z0 / z1 floats or fn(x, y) (the top is chamfered)."""
    n = Vector((u.y, -u.x))
    hw = w / 2

    def xy(lu, lv):
        return Vector((c.x + u.x * lu + n.x * lv, c.y + u.y * lu + n.y * lv))

    cr = rng.uniform(-0.4, 0.4) * hw
    ch = min(0.85, 0.2 * w) * rng.uniform(0.8, 1.2)
    H = fz(z1, c.x, c.y) - fz(z0, c.x, c.y)
    nlev = 3 if H < 7 else 4                               # few rings: big tilted facets
    k_h = min(1.0, H / 8.0)
    blean = lean + rng.uniform(0.2, 0.8) * k_h             # each column's top leans back its own way
    slean = rng.uniform(-0.8, 0.8) * k_h                   # ... and sideways
    pts = []
    for k in range(nlev):
        t = k / (nlev - 1)
        mid = 0 < k < nlev - 1
        sc = 1.0 + (rng.uniform(0.0, 0.1) if mid else 0.0) - 0.1 * t
        bl = rng.uniform(0.2, bulge) if mid else bulge * rng.uniform(0.2, 0.5)
        crk = cr + rng.uniform(-0.45, 0.45) * hw
        sh = rng.uniform(-0.45, 0.45) if mid else 0.0      # rings wander sideways: diagonal facets
        cs = rng.uniform(0.35, 0.7)                        # how far the side chamfers cut back
        ring = [(-hw * sc * 0.92, -d), (hw * sc * 0.92, -d), (hw * sc, -cs),
                (-hw * sc, -cs * rng.uniform(0.7, 1.2)), (crk, bl),
                (crk + (hw * sc - crk) * 0.55, bl * rng.uniform(0.3, 0.7) - 0.1),
                (crk - (crk + hw * sc) * 0.5, bl * rng.uniform(0.3, 0.7) - 0.1)]
        dz = rng.uniform(-0.5, 0.5) * min(1.0, H / 6) if mid else 0.0
        for lu, lv in ring:
            lu += rng.uniform(-0.15, 0.15) + sh + slean * t
            lv += rng.uniform(-0.1, 0.1) - blean * t
            p = xy(lu, lv)
            zb, zt = fz(z0, p.x, p.y), fz(z1, p.x, p.y) - ch
            pts.append(Vector((p.x, p.y, zb + (zt - zb) * t + dz)))
    # uneven top: tilted across the column (only ever downward, so it stays
    # under the grass cap) with a chipped front corner on most columns
    tilt = rng.uniform(-0.55, 0.55) * k_h
    chip = rng.choice((2, 3))
    chip_d = rng.uniform(0.4, 1.0) * k_h if rng.random() < 0.65 else 0.0
    for i, (lu, lv) in enumerate(((-hw + ch, -d + 0.2), (hw - ch, -d + 0.2), (hw - ch * 0.9, -ch * 0.8),
                                  (-hw + ch * 0.9, -ch * 0.8), (cr, -ch * 0.5 + bulge * 0.3))):
        p = xy(lu + slean, lv - blean)
        zt = fz(z1, p.x, p.y) + tilt * lu / hw - abs(tilt) - (chip_d if i == chip else 0.0)
        pts.append(Vector((p.x, p.y, zt + rng.uniform(-0.05, 0.05))))
    faces = hull(b.a, pts, 5.0)
    tone(b.a, faces, rng, u, dom=dom)
    pc = Piece(faces, "rock", Vector((n.x, n.y, 0.0)), keep_back)
    b.pieces.append(pc)
    b.cols.append(pc)
    return pc


def band(b, corners, z0, z1, seed, wr=(3.8, 6.2), depth=3.6, out=(0.3, 1.6), radius=2.2,
         min_h=0.9, drop=(0.35, 0.85), keep_back=False, occlude=True, closed=False, lean=0.3, low=0.5,
         proud=(0.8, 1.4), dom=None):
    """Rock columns along a polyline (face to the right of travel), tops just
    under the grass cap. Returns the path."""
    rng = random.Random(seed)
    pts = fillet(corners + ([corners[0]] if closed else []), radius)
    path = Path2(pts)
    L = path.L
    s = 0.0
    while s < L - 0.3:
        w = rng.uniform(*wr)
        if L - s - w < 1.8:
            w = L - s
        sc = s + w / 2
        c = path.at(sc)
        u = path.tan(sc)
        n = Vector((u.y, -u.x))
        s += w
        cc = c + n * rng.uniform(*out)
        dr = rng.uniform(*drop)
        ln = lean
        if rng.random() < low:            # a proud column stepping down: its pale top rims the grass
            dr += rng.uniform(0.8, 2.0)
            cc = cc + n * rng.uniform(*proud)
            ln = 0.1
        top = (lambda x, y, dr=dr: fz(z1, x, y) - dr)
        if top(cc.x, cc.y) - fz(z0, cc.x, cc.y) < min_h:
            continue
        column(b, cc, u, w * 1.06, depth + 1.0, z0, top, rng, keep_back=keep_back, lean=ln, dom=dom)
    if occlude:
        occluder(b, path, z0, z1, inset=1.5)
    return path


def occluder(b, path, z0, z1, inset=1.5, seg=1.6, tiers=(0.0, 0.45, 0.8, 1.0)):
    """Hidden backing wall inside the columns, so no gap ever shows the hollow
    inside. It is cut into small quads so the ones fully inside a column are
    culled later and only the true crevice gaps keep w02_rock_deep."""
    a = b.a
    k = max(1, int(round(path.L / seg)))
    rows = []
    for i in range(k + 1):
        s = path.L * i / k
        p = path.at(s)
        u = path.tan(s)
        q = p - Vector((u.y, -u.x)) * inset
        # bottom lifted 0.1 off the columns' base plane so buried quads test as inside
        zb, zt = fz(z0, q.x, q.y) + 0.1, fz(z1, q.x, q.y) - 0.9
        zt = max(zb + 0.05, zt)
        rows.append(([a.bm.verts.new((q.x, q.y, zb + (zt - zb) * t)) for t in tiers], u))
    faces = []
    for i in range(k):
        (c0, u), (c1, _) = rows[i], rows[i + 1]
        for j in range(len(tiers) - 1):
            f = face(a, (c0[j], c1[j], c1[j + 1], c0[j + 1]), Vector((u.y, -u.x, 0)))
            if f:
                faces.append(f)
    paint(a, faces, DEEP, 1.0, 0.03)
    b.pieces.append(Piece(faces, "occ"))


def shard(b, c, n2, h, w, rng):
    """Pointed leaning shard rock at a wall foot (leans back into the wall)."""
    n2 = Vector(n2).normalized()
    u = Vector((-n2.y, n2.x))
    c = Vector(c)
    rot = rng.uniform(0, TAU)
    pts = []
    for k in range(5):
        ang = rot + TAU * k / 5 + rng.uniform(-0.25, 0.25)
        p = c + u * math.cos(ang) * w * 0.5 + n2 * math.sin(ang) * w * 0.38
        pts.append(Vector((p.x, p.y, 0.0)))
    for k in range(3):
        ang = rot + TAU * k / 3 + 0.5
        p = c + (u * math.cos(ang) * w * 0.3 + n2 * math.sin(ang) * w * 0.22) - n2 * w * 0.18
        pts.append(Vector((p.x, p.y, h * rng.uniform(0.45, 0.6))))
    tip = c - n2 * w * 0.35 + u * rng.uniform(-0.25, 0.25) * w
    pts.append(Vector((tip.x, tip.y, h)))
    t2 = tip + u * rng.choice((-1, 1)) * w * 0.22 + n2 * 0.15
    pts.append(Vector((t2.x, t2.y, h * rng.uniform(0.8, 0.9))))
    faces = hull(b.a, pts, 3.0)
    tone(b.a, faces, rng, u)
    b.pieces.append(Piece(faces, "rock"))


def stone(b, c, size, rng, mat=LIGHT, n=9, flat=0.25):
    """Pale rounded stone / pebble sitting at c (x, y, z)."""
    sx, sy, sz = size
    yaw = rng.uniform(0, TAU)
    cs, sn = math.cos(yaw), math.sin(yaw)
    pts = []
    ga = math.pi * (3 - math.sqrt(5))
    for i in range(n):
        zz = -0.2 + 1.2 * (i + 0.5) / n
        rr = math.sqrt(max(0.0, 1 - min(1, zz) ** 2))
        th = ga * i + rng.uniform(-0.3, 0.3)
        x, y = rr * math.cos(th) * sx / 2, rr * math.sin(th) * sy / 2
        z = min(max(0.0, zz), 1 - flat) * sz
        pts.append(Vector((c[0] + x * cs - y * sn, c[1] + x * sn + y * cs, c[2] + z)))
    faces = hull(b.a, pts, 4.0)
    dead = [f for f in faces if f.normal.z < -0.9]
    if dead:
        bmesh.ops.delete(b.a.bm, geom=dead, context="FACES_ONLY")
    faces = [f for f in faces if f.is_valid]
    for f in faces:
        paint(b.a, [f], mat, rng.uniform(0.96, 1.04), 0.0)
    return faces


# ---------------------------------------------------------------------------
# grass
# ---------------------------------------------------------------------------


class Deck:
    """A grass top: its outline (2D, CCW) and height for scattering."""

    def __init__(self, T, H):
        self.T = T
        self.H = H

    def h(self, x, y):
        return fz(self.H, x, y)


def grass_cap(b, P, H, lip, seed, hang=(0.3, 0.8), lam=3.2, step=0.8,
              layers=((0.6, GRASS, 1.0), (1.0, EARTH, 1.0)), under=1.0, flat_bottom=False):
    """Shared W02 grass cap over the nominal rock edge P (CCW): a flat top,
    scalloped lip offset 0.3-0.8 outward where lip(p), side bands (grass then
    earth), and an underside back in to the rock (or a flat bottom)."""
    a = b.a
    rng = random.Random(seed)
    R = resample_closed(P, step)
    N = normals_closed(R)
    n = len(R)
    ph = rng.uniform(0, lam)
    s = 0.0
    offs, lips = [], []
    for i, p in enumerate(R):
        if i:
            s += (R[i] - R[i - 1]).length
        L = lip(p)
        if L:
            k = abs(math.sin(math.pi * (s + ph) / lam)) ** 0.5
            o = hang[0] + (hang[1] - hang[0]) * k * rng.uniform(0.85, 1.0)
        else:
            o = 0.0
        offs.append(o)
        lips.append(L)
    T = [R[i] + N[i] * offs[i] for i in range(n)]
    Hf = (lambda x, y: fz(H, x, y))
    # top: constrained Delaunay of the outline
    res = delaunay_2d_cdt(T, [(i, (i + 1) % n) for i in range(n)], [], 0, 1e-5)
    vco, tris, orig = res[0], res[2], res[3]
    vmap = {}

    def V(k):
        if k not in vmap:
            p = vco[k]
            vmap[k] = a.bm.verts.new((p.x, p.y, Hf(p.x, p.y)))
        return vmap[k]

    top_of = {}
    for k, o in enumerate(orig):
        for i in o:
            if i < n:
                top_of[i] = k
    tops = []
    for tri in tris:
        cx = sum(vco[k].x for k in tri) / len(tri)
        cy = sum(vco[k].y for k in tri) / len(tri)
        if not inside(T, cx, cy):
            continue
        f = face(a, [V(k) for k in tri], Z)
        if f:
            tops.append(f)
    paint(a, tops, GRASS, 1.0, 0.025)
    Tv = [V(top_of[i]) for i in range(n)]
    # side bands
    rows = [Tv]
    for li, (dep, mat, tint) in enumerate(layers):
        row = []
        for i in range(n):
            j = 0.85 + 0.3 * rng.random() if li == 0 and lips[i] else 1.0
            o = 0.05 if li == 0 else -0.02
            p = T[i] + N[i] * (o if lips[i] else 0.0)
            row.append(a.bm.verts.new((p.x, p.y, Hf(T[i].x, T[i].y) - dep * j)))
        rows.append(row)
    sides = []
    for li in range(len(layers)):
        r0, r1 = rows[li], rows[li + 1]
        mat, tint = layers[li][1], layers[li][2]
        fs = []
        for i in range(n):
            j = (i + 1) % n
            if not (lips[i] or lips[j] or flat_bottom):
                continue
            nn = (N[i] + N[j]).normalized()
            f = face(a, (r0[i], r0[j], r1[j], r1[i]), Vector((nn.x, nn.y, 0)))
            if f:
                fs.append(f)
        paint(a, fs, mat, tint, 0.04)
        sides += fs
    last = rows[-1]
    dep = layers[-1][0]
    if flat_bottom:
        res = delaunay_2d_cdt(T, [(i, (i + 1) % n) for i in range(n)], [], 0, 1e-5)
        bf = []
        for tri in res[2]:
            cx = sum(res[0][k].x for k in tri) / 3
            cy = sum(res[0][k].y for k in tri) / 3
            if not inside(T, cx, cy):
                continue
            ks = []
            for k in tri:
                ii = [i for i in res[3][k] if i < n]
                ks.append(last[ii[0]] if ii else None)
            if None in ks:
                continue
            f = face(a, ks, -Z)
            if f:
                bf.append(f)
        paint(a, bf, layers[-1][1], 1.0, 0.02)
    else:
        inner = []
        for i in range(n):
            p = R[i] - N[i] * under
            inner.append(a.bm.verts.new((p.x, p.y, Hf(R[i].x, R[i].y) - dep)) if lips[i] else None)
        fs = []
        for i in range(n):
            j = (i + 1) % n
            if not (lips[i] and lips[j]):
                continue
            f = face(a, (last[i], last[j], inner[j], inner[i]), -Z)
            if f:
                fs.append(f)
        paint(a, fs, EARTH, 1.0, 0.04)
    b.pieces.append(Piece([f for f in tops + sides if f.is_valid], "grass"))
    d = Deck(T, H)
    b.decks.append(d)
    return d


def patches(b, deck, seed, count, rad=(1.1, 2.6), seg=9, avoid=()):
    """Soft lighter / darker grass patches lying on a deck."""
    a = b.a
    rng = random.Random(seed)
    xs = [p.x for p in deck.T]
    ys = [p.y for p in deck.T]
    placed = 0
    for _ in range(count * 25):
        if placed >= count:
            break
        cx, cy = rng.uniform(min(xs), max(xs)), rng.uniform(min(ys), max(ys))
        r = rng.uniform(*rad)
        if not inside(deck.T, cx, cy) or edge_dist(deck.T, cx, cy) < r + 0.5:
            continue
        if any(math.hypot(cx - x, cy - y) < r + ar for x, y, ar in avoid):
            continue
        p1 = rng.uniform(0, TAU)
        ring = []
        for k in range(seg):
            ang = TAU * k / seg
            re = r * (1 + 0.22 * math.sin(2 * ang + p1) + 0.1 * math.sin(3 * ang - p1))
            ring.append((cx + math.cos(ang) * re * 1.25, cy + math.sin(ang) * re * 0.85))
        z = deck.h(cx, cy) + 0.03
        cv = a.bm.verts.new((cx, cy, z))
        vs = [a.bm.verts.new((x, y, deck.h(x, y) + 0.03)) for x, y in ring]
        fs = [face(a, (cv, vs[k], vs[(k + 1) % seg]), Z) for k in range(seg)]
        light = placed % 2 == 0          # alternate a touch lighter / darker (small Tint step, one colour)
        paint(a, [f for f in fs if f], GRASS, 1.06 if light else 0.94, 0.015)
        placed += 1


def blob(b, c, r, rng, sq=0.85, n=12, mat=BUSH):
    pts = []
    ga = math.pi * (3 - math.sqrt(5))
    for i in range(n):
        zz = 1 - 2 * (i + 0.5) / n
        rr = math.sqrt(max(0.0, 1 - zz * zz))
        th = ga * i + rng.uniform(-0.3, 0.3)
        k = r * rng.uniform(0.86, 1.08)
        z = max(-0.35, zz) * k * sq
        pts.append(Vector((c[0] + rr * math.cos(th) * k, c[1] + rr * math.sin(th) * k, c[2] + z)))
    faces = hull(b.a, pts, 0)
    for f in faces:
        paint(b.a, [f], mat, rng.uniform(0.95, 1.05), 0.0)
    return faces


def bush(b, c, r, rng, lobes=None):
    """Round leafy bush clump: a main dome with 2-4 smaller lobes round it."""
    x, y, z = c
    r *= BUSH_SCALE
    lobes = lobes if lobes is not None else rng.randint(3, 5)
    fs = blob(b, (x, y, z + r * 0.5), r * 0.72, rng, mat=BUSH if rng.random() < 0.5 else BUSH_L)
    rot = rng.uniform(0, TAU)
    for k in range(lobes):
        ang = rot + TAU * k / lobes + rng.uniform(-0.3, 0.3)
        rr = r * rng.uniform(0.45, 0.6)
        q = (x + math.cos(ang) * r * 0.58, y + math.sin(ang) * r * 0.58, z + rr * 0.55)
        u = rng.random()
        fs += blob(b, q, rr, rng, n=10, mat=BUSH_L if u < 0.5 else (BUSH if u < 0.85 else BUSH_D))
    # undersides resting on the ground / deck are never seen: drop them
    dead = [f for f in fs if f.is_valid and f.normal.z < -0.6 and f.calc_center_median().z < z + 0.4 * r]
    if dead:
        bmesh.ops.delete(b.a.bm, geom=dead, context="FACES_ONLY")


BUSH_SCALE = 1.75


def flower(b, x, y, z, mat, s=1.0):
    a = b.a
    """Flower dot: a low 5-petal dome about 0.6 studs across, sitting proud of
    the grass so it reads as a bright dot from the iso and top views."""
    c = a.bm.verts.new((x, y, z + 0.3 * s))
    rot = a.rng.uniform(0, TAU)
    ring = [a.bm.verts.new((x + math.cos(rot + TAU * k / 5) * 0.32 * s,
                            y + math.sin(rot + TAU * k / 5) * 0.32 * s, z + 0.12 * s)) for k in range(5)]
    fs = [face(a, (c, ring[k], ring[(k + 1) % 5]), Z) for k in range(5)]
    paint(a, [f for f in fs if f], mat, 1.0, 0.02)


def tuft(b, x, y, z, rng, h=0.9, n=4):
    """Grass tuft: a few thin leaning blades (3-sided spikes, open bottom)."""
    a = b.a
    rot = rng.uniform(0, TAU)
    for k in range(n):
        ang = rot + TAU * k / n + rng.uniform(-0.3, 0.3)
        d = Vector((math.cos(ang), math.sin(ang), 0))
        hh = h * rng.uniform(0.7, 1.15)
        p0 = Vector((x, y, z)) + d * 0.15
        tip = a.bm.verts.new(p0 + d * hh * 0.45 + Vector((0, 0, hh)))
        base = [a.bm.verts.new(p0 + Vector((math.cos(ang + TAU * j / 3), math.sin(ang + TAU * j / 3), 0)) * 0.2)
                for j in range(3)]
        fs = []
        for j in range(3):
            v0, v1 = base[j], base[(j + 1) % 3]
            mid = (v0.co + v1.co) / 2 - p0
            fs.append(face(a, (v0, v1, tip), Vector((mid.x, mid.y, 0.2))))
        paint(a, [f for f in fs if f], GRASS_D if k % 2 else GRASS, 1.0, 0.04)


def scatter(b, deck, seed, pebbles=6, flowers=10, avoid=(), margin=1.0):
    """Pale pebbles and white / yellow flower dots on a deck."""
    rng = random.Random(seed)
    xs = [p.x for p in deck.T]
    ys = [p.y for p in deck.T]
    spots = list(avoid)

    def spot(r):
        for _ in range(60):
            x, y = rng.uniform(min(xs), max(xs)), rng.uniform(min(ys), max(ys))
            if not inside(deck.T, x, y) or edge_dist(deck.T, x, y) < margin:
                continue
            if any(math.hypot(x - sx, y - sy) < r + sr for sx, sy, sr in spots):
                continue
            spots.append((x, y, r))
            return x, y
        return None

    for _ in range(pebbles):
        p = spot(0.6)
        if p:
            s = rng.uniform(0.35, 0.75)
            stone(b, (p[0], p[1], deck.h(*p) - 0.05), (s * 1.2, s, s * 0.7), rng, n=7)
    for i in range(flowers):
        p = spot(0.35)
        if p:
            flower(b, p[0], p[1], deck.h(*p), FLOWERS[0] if i % 3 else FLOWERS[1], rng.uniform(0.85, 1.2))
            if rng.random() < 0.45:  # little pairs, like the painted dots
                q = (p[0] + rng.uniform(-0.6, 0.6), p[1] + rng.uniform(-0.6, 0.6))
                if inside(deck.T, *q):
                    flower(b, q[0], q[1], deck.h(*q), FLOWERS[0], 0.8)


def streak(b, x, y, n2, ztop, L, w, rng):
    """Dark grass streak dripping down the rock face below a lip at (x, y)."""
    a = b.a
    n2 = Vector(n2).normalized()
    rows = []
    for t, wf in ((0.0, 1.0), (0.5, 0.7), (1.0, 0.0)):
        z = ztop - L * t
        o = Vector((x + n2.x * 5, y + n2.y * 5, z))
        d = Vector((-n2.x, -n2.y, 0))
        best = None
        for p in b.cols:
            hit = p.ray(o, d)
            if hit and (best is None or hit[0] < best[0]):
                best = hit
        if best is None or best[0] > 7.5:
            return False
        q = o + d * best[0] + best[1] * 0.07
        rows.append((q, best[1], wf * w))
    vs = []
    for q, nn, ww in rows:
        side = Z.cross(nn)
        side = side.normalized() if side.length > 1e-6 else Vector((1, 0, 0))
        if ww > 0:
            vs.append((a.bm.verts.new(q - side * ww / 2), a.bm.verts.new(q + side * ww / 2)))
        else:
            vs.append((a.bm.verts.new(q),))
    out = Vector((n2.x, n2.y, 0))
    fs = [face(a, (vs[0][0], vs[0][1], vs[1][1], vs[1][0]), out), face(a, (vs[1][0], vs[1][1], vs[2][0]), out)]
    paint(a, [f for f in fs if f], GRASS_D, rng.uniform(0.96, 1.04), 0.0)
    return True


def connector(b, W, D, Hu, plate_top=None):
    """Shared W02 back connector: flat matte plate inset 0.5 on +Y with tabs."""
    a = b.a
    top = plate_top if plate_top is not None else Hu - 0.5
    hw = W / 2 - 0.5
    fs = a.box((2 * hw, 0.4, top), loc=(0, D / 2 - 0.2, 0), mat=CONN, base=True, tint=1.0)
    z = 4.0
    while z + 0.75 < top:
        for sx in (-1, 1):
            a.box((0.5, 0.4, 1.5), loc=(sx * (hw + 0.25), D / 2 - 0.2, z), mat=CONN, tint=1.0)
        z += 8.0
    return fs


# ---------------------------------------------------------------------------
# assembly
# ---------------------------------------------------------------------------


class Builder:
    def __init__(self, kit, name, seed):
        self.kit = kit
        self.a = kit.flintkit.Asset(name, "Terrain", seed=seed, tint_var=0.03)
        self.rng = random.Random(seed)
        self.pieces = []
        self.cols = []
        self.decks = []

    def finish(self, role, collision, budget, notes, bound=None):
        a = self.a
        rocks = [p for p in self.pieces if p.kind == "rock"]
        dead = set()
        for p in self.pieces:
            for f in p.faces:
                if not f.is_valid:
                    continue
                for q in rocks:
                    if q is not p and all(q.contains(v.co) for v in f.verts):
                        dead.add(f)
                        break
                else:
                    if p.kind == "occ":
                        # backing quads buried across two touching columns: every
                        # corner, edge midpoint and the centre lies in some rock
                        vs = [v.co for v in f.verts]
                        pts = vs + [(vs[i] + vs[i - 1]) / 2 for i in range(len(vs))] + [f.calc_center_median()]
                        if all(any(q.contains(c) for q in rocks) for c in pts):
                            dead.add(f)
        for p in self.cols:
            for f in p.faces:
                if not f.is_valid or f in dead:
                    continue
                if f.normal.z < -0.9:
                    dead.add(f)
                elif not p.keep_back and f.normal.dot(p.n_out) < -0.6:
                    dead.add(f)
        if dead:
            bmesh.ops.delete(a.bm, geom=list(dead), context="FACES_ONLY")
        for v in a.bm.verts:
            if v.co.z < 0.0:
                v.co.z = 0.0
            if bound:
                v.co.x = max(-bound[0], min(bound[0], v.co.x))
                v.co.y = max(bound[1], min(bound[2], v.co.y))
        a.bm.normal_update()
        dead = [f for f in a.bm.faces if f.normal.z < -0.97 and f.calc_center_median().z < 0.03]
        if dead:
            bmesh.ops.delete(a.bm, geom=dead, context="FACES_ONLY")
        loose = [v for v in a.bm.verts if not v.link_faces]
        if loose:
            bmesh.ops.delete(a.bm, geom=loose, context="VERTS")
        obj = a.finish()
        obj["kit_two_tone_ok"] = TWO_TONE_OK
        return self.kit.tag(obj, role, collision=collision, budget=budget, notes=notes)


class Spec:
    """Terrace layout (studs). Lower deck at Hl on the front, upper deck at Hu
    on the back from ys; the upper tier spans xl..xr and its left end (x <
    step_x) steps back by step_d."""

    def __init__(self, W=32.0, D=32.0, Hl=12.0, Hu=24.0, ys=0.0, xl=-12.2, step_x=-8.0,
                 step_d=3.5, seed=1, ramp=None, edge=3.4, up_out=(0.6, 1.3), up_proud=(0.6, 1.1), cap_in=1.0,
                 gap=3.2, front_in=2.8):
        self.W, self.D, self.Hl, self.Hu, self.ys = W, D, Hl, Hu, ys
        self.xl, self.step_x, self.step_d = xl, step_x, step_d
        self.seed = seed
        self.up_out, self.up_proud = up_out, up_proud
        self.ramp = ramp is not None
        self.cap_in = cap_in
        self.gap = gap                # lower grass stops this far in front of the upper tier line
        self.front_in = front_in      # upper grass starts this far behind the upper tier line
        self.E = W / 2 - edge         # nominal rock edge on the sides (columns stand proud of it,
        self.F = -D / 2 + edge        # so their pale tops rim the grass in the top view)
        self.yb = D / 2 - 0.4         # plate front
        self.yc = D / 2 - 2.2         # the upper tier widens to full width behind here
        self.yF = ys + 0.5            # the upper tier's front line
        self.xe = self.E if ramp is None else ramp["x0"]  # the deck's +X edge

    def upper_path(self):
        s = self
        xe = s.xe
        right = [(xe, s.yF), (xe, s.yb)]
        left = [(-s.E, s.yb), (-s.E, s.yc), (s.xl, s.yc - 1.0)]
        if s.step_d > 0:
            left += [(s.xl, s.ys + s.step_d), (s.step_x, s.ys + s.step_d), (s.step_x, s.yF)]
        else:
            left += [(s.xl, s.yF)]
        return left + right

    def lower_cap_poly(self):
        """The lower grass: a rectangle that stops `gap` in front of the upper
        tier (the low rock plinth fills the strip), plus a tab running back
        into the stepped-back notch at the left end."""
        s = self
        gx, gf = -s.E + s.cap_in, s.F + s.cap_in       # grass edge sits inside the rim columns
        xg = s.xe if s.ramp else s.xe - s.cap_in
        yr = s.ys - s.gap
        if s.step_d > 0:
            ytl = s.ys + s.step_d + 0.8
            pts = [(gx, ytl), (gx, gf), (xg, gf), (xg, yr), (s.step_x + 0.8, yr), (s.step_x + 0.8, ytl)]
        else:
            pts = [(gx, yr), (gx, gf), (xg, gf), (xg, yr)]
        return [V2(p) for p in pts]

    def lower_lip(self, p):
        s = self
        gx, gf = -s.E + s.cap_in, s.F + s.cap_in
        xg = s.xe if s.ramp else s.xe - s.cap_in
        ytop = s.ys + s.step_d if s.step_d > 0 else s.ys - s.gap - 0.05
        return ((abs(p.x - gx) < 0.05 and p.y < ytop) or (abs(p.x - xg) < 0.05 and p.y < s.ys - s.gap - 0.05)
                or abs(p.y - gf) < 0.05)

    def upper_lip(self, p):
        return p.y < self.yb - 0.05

    def upper_cap_poly(self, d=1.1):
        """The upper grass outline: the band path pulled in by front_in on the
        front-facing edges and by d on the sides (not on the back), so a broad
        band of pale column tops separates the two decks in the top view."""
        P = [V2(p) for p in self.upper_path()]
        n = len(P)
        lines = []
        for i in range(n):
            a, c = P[i], P[(i + 1) % n]
            e = c - a
            on_back = abs(a.y - self.yb) < 1e-6 and abs(c.y - self.yb) < 1e-6
            nn = Vector((e.y, -e.x)).normalized() if e.length > 1e-9 else Vector((0, 0))
            dd = 0.0 if on_back else (self.front_in if nn.y < -0.7 else d)
            lines.append((a - nn * dd, e))
        out = []
        for i in range(n):
            (p1, e1), (p2, e2) = lines[i - 1], lines[i]
            cr = e1.x * e2.y - e1.y * e2.x
            if abs(cr) < 0.05 * max(1e-9, e1.length * e2.length):
                out.append(p2)
                continue
            w = p2 - p1
            t = (w.x * e2.y - w.y * e2.x) / cr
            out.append(p1 + e1 * t)
        return out


# outer lower band: the columns stand well proud of the grass lip, many stepping
# down, so their pale tops rim the deck in the top view (as on the reference)
DROP = (1.05, 1.5)           # column tops sit below the 1.0 grass + earth cap, so the earth line shows
RIM = dict(out=(0.6, 1.4), low=0.6, proud=(0.6, 1.2), drop=DROP)


def upper_band(b, s, path=None):
    """The upper tier's rock band in two runs: the left side and the notch of
    the stepped-back end stay close to the wall (so the lower grass wrapping
    round them stays open), the front and right columns stand proud of the
    upper lip so a strip of column tops separates the two decks from above."""
    path = path if path is not None else s.upper_path()
    k = 5 if s.step_d > 0 else 2
    sd = s.seed
    if s.step_d > 0:
        band(b, path[:4], s.Hl - 0.6, s.Hu, sd * 10 + 2, out=(0.2, 0.6), low=0.4, proud=(0.3, 0.6), drop=DROP)
        # the notch walls behind the filler rock: mauve, so the peach filler reads apart
        band(b, path[3:k + 1], s.Hl - 0.6, s.Hu, sd * 10 + 8, out=(0.2, 0.5), low=0.3, proud=(0.3, 0.5), drop=DROP,
             dom=ROCK, radius=1.2)
    else:
        band(b, path[:k + 1], s.Hl - 0.6, s.Hu, sd * 10 + 2, out=(0.2, 0.6), low=0.4, proud=(0.3, 0.6), drop=DROP)
    band(b, path[k:], s.Hl - 0.6, s.Hu, sd * 10 + 7, out=s.up_out, low=0.7, proud=s.up_proud,
         drop=DROP, lean=0.1)


def plinth(b, s):
    """A low run of pale rock blocks at the foot of the upper tier's front,
    filling the strip between the lower grass and the upper columns: from
    above it joins the upper column tops into one broad rock band, so the two
    decks read as two separate rectangles."""
    if s.gap < 1.0:
        return
    x0 = (s.step_x - 0.6) if s.step_d > 0 else (-s.E - 0.4)
    x1 = s.xe - 0.2 if s.ramp else s.xe + 0.4
    yP = s.ys - s.gap + 0.9
    band(b, [(x0, yP), (x1, yP)], s.Hl - 1.0, s.Hl + 2.4, s.seed * 10 + 9, wr=(2.8, 4.4), depth=s.gap,
         out=(0.0, 0.3), radius=1.0, min_h=0.5, drop=(0.0, 0.8), occlude=False, lean=0.15, low=0.0,
         dom=LIGHT)


def terrace(b, s, ramp=None):
    """Rock bands, grass caps and the connector of a two-level terrace."""
    sd = s.seed
    E, F, yb = s.E, s.F, s.yb
    if ramp is None:
        # lower band: left side (back to front), front, right side (front to back);
        # the upper band stands on the lower deck
        band(b, [(-E, yb), (-E, F), (E, F), (E, yb)], 0.0, s.Hl, sd * 10 + 1, **RIM)
        upper_band(b, s)
    else:
        # the +X walls stand on the ramp instead of the ground / lower deck
        rz, xe = ramp["z"], s.xe
        band(b, [(-E, yb), (-E, F), (xe, F)], 0.0, s.Hl, sd * 10 + 1, **RIM)
        band(b, [(xe, F), (xe, s.ys + 0.5)], lambda x, y: max(0.0, rz(y) - 0.6), s.Hl, sd * 10 + 5, min_h=1.2)
        up = s.upper_path()
        upper_band(b, s, up[:-1])
        band(b, up[-2:], lambda x, y: max(s.Hl, rz(y)) - 0.6, s.Hu, sd * 10 + 6, min_h=1.2)
    plinth(b, s)
    lower = grass_cap(b, s.lower_cap_poly(), s.Hl, s.lower_lip, sd * 10 + 3)
    up = s.upper_cap_poly()
    upper = grass_cap(b, up, s.Hu, s.upper_lip, sd * 10 + 4)
    connector(b, s.W, s.D, s.Hu)
    return lower, upper


def foot(b, s, seed, shards, clumps, rubble, tufts=()):
    """Pointed shards, bush clumps, rubble and grass tufts round the lower
    band's foot. shards: (x, y, side, h, w); side 'f' front, 'l' left, 'r' right."""
    rng = random.Random(seed)
    dirs = {"f": (0, -1), "l": (-1, 0), "r": (1, 0)}
    for x, y, side, h, w in shards:
        shard(b, (x, y), dirs[side], h * 1.45, w * 1.4, rng)
    for x, y, r in clumps:
        bush(b, (x, y, 0.0), r, rng)
    for x, y, sz in rubble:
        stone(b, (x, y, -0.05), (sz * 1.3, sz, sz * 0.8), rng, mat=LIGHT if rng.random() < 0.65 else ROCK)
    for x, y in tufts:
        tuft(b, x, y, 0.0, rng)


def edge_foot(s, seed, n_rubble=10, n_tufts=10, front=True, left=True, right=True):
    """Rubble stones and tufts spread along the foot of the outer walls
    (x, y, size) / (x, y), skipping nothing: the reference litters every side."""
    rng = random.Random(seed)
    hx, hy = s.W / 2, s.D / 2
    sides = [k for k, on in (("f", front), ("f", front), ("l", left), ("r", right)) if on]

    def pt(side, t):
        if side == "f":
            return (-hx + 1.0 + t * (2 * hx - 2.0), -hy + rng.uniform(0.5, 1.1))
        if side == "l":
            return (-hx + rng.uniform(0.5, 1.1), -hy + 2.0 + t * (2 * hy - 5.0))
        return (hx - rng.uniform(0.5, 1.1), -hy + 2.0 + t * (2 * hy - 5.0))

    rubble, tufts = [], []
    for i in range(n_rubble):
        side = sides[i % len(sides)][0]
        x, y = pt(side, (i + rng.uniform(0.2, 0.8)) / n_rubble)
        rubble.append((x, y, rng.uniform(0.75, 1.3)))
    for i in range(n_tufts):
        side = sides[(i + 1) % len(sides)][0]
        tufts.append(pt(side, (i + rng.uniform(0.1, 0.9)) / n_tufts))
    return rubble, tufts


def dress_deck(b, deck, seed, bushes, rocks=(), pebbles=6, flowers=10, patch_n=6):
    rng = random.Random(seed)
    avoid = []
    for x, y, r in bushes:
        bush(b, (x, y, deck.h(x, y) - 0.05), r, rng)
        avoid.append((x, y, r + 0.3))
    for x, y, sz in rocks:
        stone(b, (x, y, deck.h(x, y) - 0.1), sz, rng, n=12, flat=0.15)
        avoid.append((x, y, max(sz[0], sz[1]) * 0.6))
    patches(b, deck, seed + 1, patch_n, avoid=avoid)
    scatter(b, deck, seed + 2, pebbles, flowers, avoid=avoid)


def streaks(b, spots, seed):
    """spots: (x, y, side, ztop, L)."""
    rng = random.Random(seed)
    dirs = {"f": (0, -1), "l": (-1, 0), "r": (1, 0)}
    for x, y, side, zt, L in spots:
        w = rng.uniform(1.0, 1.5)
        # a column top can sit lower than the lip: slide down / sideways until the
        # streak lands on rock
        for dz, dx in ((0.4, 0.0), (1.2, 0.0), (1.2, 1.2), (1.2, -1.2), (2.2, 0.6), (2.2, -0.6), (3.0, 0.0)):
            u = (-dirs[side][1], dirs[side][0])
            if streak(b, x + u[0] * dx, y + u[1] * dx, dirs[side], zt - dz, L, w, rng):
                break


def filler_rock(b, c, size, seed, slope_dir=(0.0, -1.0), z0=0.0):
    """Tall wedge rock: a faceted column whose top slopes down toward slope_dir,
    standing at height z0 (the lower deck in the assembled terrace). It keeps
    the warm peach tone so it stands out from the mauve columns behind it."""
    rng = random.Random(seed)
    sx, sy, h = size
    sd = Vector(slope_dir).normalized()
    pts = []
    for k, (fzr, fr) in enumerate(((0.0, 1.0), (0.3, 0.97), (0.55, 0.9), (0.78, 0.8))):
        rot = rng.uniform(0, TAU)
        for i in range(7):
            ang = rot + TAU * i / 7 + rng.uniform(-0.25, 0.25)
            x, y = math.cos(ang) * sx / 2 * fr, math.sin(ang) * sy / 2 * fr
            zz = fzr * h * (1 - 0.35 * max(0.0, (x * sd.x + y * sd.y) / (sx / 2)))
            pts.append(Vector((c[0] + x, c[1] + y, z0 + zz)))
    for i in range(4):
        ang = TAU * i / 4 + rng.uniform(-0.3, 0.3) + 0.4
        x, y = math.cos(ang) * sx * 0.3, math.sin(ang) * sy * 0.3
        d = (x * sd.x + y * sd.y) / (sx * 0.3)
        pts.append(Vector((c[0] + x, c[1] + y, z0 + h * (0.8 - 0.17 * d) + rng.uniform(-0.1, 0.1))))
    # pointed top, set toward the high (back) side of the wedge
    pk = Vector(c[:2]) - sd * sx * 0.12
    pts.append(Vector((pk.x, pk.y, z0 + h)))
    faces = hull(b.a, pts, 3.0)
    tone(b.a, faces, rng, Vector((-sd.y, sd.x, 0)), dom=LIGHT)
    pc = Piece(faces, "rock", Vector((sd.x, sd.y, 0)), True)
    b.pieces.append(pc)
    b.cols.append(pc)
    return pc


# ---------------------------------------------------------------------------
# hero and variants
# ---------------------------------------------------------------------------

# upper tier x -8..+12 (plus its columns); its left end (x < -1.5) is set back
# 6 studs, so the lower grass wraps round the left of it and the filler rock
# closes the inside corner of the step
HERO = Spec(ys=1.5, xl=-12.2, step_x=-3.5, step_d=6.0, seed=1, gap=3.2, front_in=2.8)
# the UpperCap part: a broader slab (about 27 x 16) with a small step at its left
CAP = Spec(xl=-13.0, step_x=-7.0, step_d=2.5, seed=1)


def build_hero(kit):
    b = Builder(kit, "TerracedLedge", 201)
    s = HERO
    lower, upper = terrace(b, s)
    # tall pointed filler rock standing on the lower deck in the inside corner
    # of the stepped-back left end, a little clear of both notch walls so it
    # reads against the lower grass that runs round its front and left
    # its pointed top stops ~3 below the upper lip so it reads against the notch wall
    fx, fy = s.step_x - 3.3, s.ys + s.step_d - 3.4
    filler_rock(b, (fx, fy), (4.8, 4.4, 9.6), 77, slope_dir=(-0.7, -0.7), z0=s.Hl - 0.6)
    dress_deck(b, upper, 31, bushes=[(-9.8, 11.8, 1.3), (-9.4, 14.6, 1.25), (-1.5, 14.8, 1.35),
                                     (5.0, 14.6, 1.6), (10.8, 13.4, 1.4), (10.8, 6.8, 1.2), (-0.6, 6.8, 1.05)],
               rocks=[(3.2, 9.4, (2.3, 2.0, 1.9))], pebbles=8, flowers=20, patch_n=6)
    dress_deck(b, lower, 41, bushes=[(-10.4, -10.4, 1.6), (-3.2, -11.0, 1.2), (4.6, -11.2, 1.25),
                                     (10.6, -10.2, 1.4), (10.6, -4.6, 1.2), (-11.0, -4.8, 1.15),
                                     (-11.0, 7.2, 1.1), (-11.2, 1.6, 0.9)],
               rocks=[(1.6, -6.8, (2.1, 1.8, 1.7))], pebbles=8, flowers=20, patch_n=6)
    rubble, tufts = edge_foot(s, 52, n_rubble=14, n_tufts=16)
    foot(b, s, 51,
         shards=[(-11.0, -15.4, "f", 4.8, 2.6), (-4.4, -15.5, "f", 3.6, 2.2), (2.6, -15.4, "f", 5.4, 2.6),
                 (9.2, -15.5, "f", 3.4, 2.0), (13.0, -15.4, "f", 4.4, 2.2), (-15.4, -12.5, "l", 3.8, 2.2),
                 (-15.4, -6.0, "l", 4.2, 2.4), (-15.4, 5.0, "l", 3.2, 2.0), (15.4, -8.0, "r", 3.8, 2.2)],
         clumps=[(-14.6, -14.8, 1.4), (-7.6, -15.0, 1.2), (-0.8, -15.2, 1.1), (6.2, -15.0, 1.25),
                 (11.0, -15.3, 1.0), (14.6, -14.6, 1.25), (-15.0, -9.0, 1.0), (-15.0, 0.0, 1.15),
                 (-15.0, 10.0, 1.0), (15.0, -3.0, 1.0), (15.0, 3.0, 1.1), (15.0, 11.0, 0.95)],
         rubble=rubble, tufts=tufts)
    streaks(b, [(-9.0, -15.2, "f", 11.0, 2.6), (0.5, -15.2, "f", 11.0, 3.6), (7.5, -15.2, "f", 11.0, 2.2),
                (-15.2, -9.0, "l", 11.0, 3.0), (2.5, s.yF - 1.0, "f", 23.0, 2.8), (8.5, s.yF - 1.0, "f", 23.0, 2.0),
                (-2.0, s.yF - 1.0, "f", 23.0, 2.4), (-10.0, s.ys + s.step_d, "f", 23.0, 2.4),
                (-12.6, 11.0, "l", 23.0, 2.4), (13.0, 7.0, "r", 23.0, 2.2)], 61)
    return b.finish("hero", "precise", 8000,
                    "two walkable grass decks (z=12 front, z=24 back); 32x32 grid; +Y connector plate",
                    bound=(16.0, -16.0, 16.0))


def build_shallow(kit):
    s = Spec(D=20.0, ys=-1.5, xl=-13.0, step_x=-4.0, step_d=3.0, seed=2, edge=2.4, cap_in=0.6, gap=1.8,
             front_in=2.0, up_out=(0.4, 1.0), up_proud=(0.5, 0.9))
    b = Builder(kit, "TerracedLedgeShallow", 211)
    lower, upper = terrace(b, s)
    filler_rock(b, (s.step_x - 2.6, s.ys + s.step_d - 2.2), (3.6, 3.2, 10.6), 78, slope_dir=(-0.7, -0.7),
                z0=s.Hl - 0.6)
    dress_deck(b, upper, 32, bushes=[(-11.0, 5.0, 1.2), (-10.6, 8.4, 1.15), (6.0, 8.4, 1.4), (11.6, 2.6, 1.05),
                                     (0.0, 2.4, 1.0)],
               rocks=[(-3.5, 6.0, (1.9, 1.7, 1.6))], pebbles=6, flowers=14, patch_n=4)
    dress_deck(b, lower, 42, bushes=[(-12.0, -6.0, 1.25), (-11.8, 0.5, 1.0), (1.5, -6.0, 1.1),
                                     (12.0, -5.8, 1.0), (7.0, -6.2, 0.9)],
               pebbles=6, flowers=12, patch_n=3)
    rubble, tufts = edge_foot(s, 55, n_rubble=10, n_tufts=10)
    foot(b, s, 52,
         shards=[(-9.0, -9.4, "f", 4.4, 2.4), (0.0, -9.5, "f", 3.4, 2.0), (8.0, -9.4, "f", 5.0, 2.4),
                 (-15.4, -2.0, "l", 3.6, 2.0), (13.0, -9.4, "f", 3.6, 2.0)],
         clumps=[(-14.6, -8.8, 1.2), (-4.5, -9.1, 1.0), (4.0, -9.2, 0.95), (14.6, -8.6, 1.1),
                 (-15.0, 4.0, 0.9), (15.0, 2.0, 0.9)],
         rubble=rubble, tufts=tufts)
    streaks(b, [(-6.0, -9.2, "f", 11.0, 2.8), (5.0, -9.2, "f", 11.0, 2.2), (-2.0, s.yF - 1.0, "f", 23.0, 3.0),
                (8.0, s.yF - 1.0, "f", 23.0, 2.2)], 62)
    return b.finish("variant", "precise", 6500, "A. SHALLOW: narrow 7-deep lower shelf at z=12, upper z=24; 32x20",
                    bound=(16.0, -10.0, 10.0))


def build_wide(kit):
    s = Spec(D=40.0, Hl=8.0, Hu=16.0, ys=1.5, xl=-12.2, step_x=-4.0, step_d=5.5, seed=3, gap=2.6, front_in=2.6)
    b = Builder(kit, "TerracedLedgeWide", 221)
    lower, upper = terrace(b, s)
    filler_rock(b, (s.step_x - 2.8, s.ys + s.step_d - 2.6), (4.2, 4.0, 7.2), 79, slope_dir=(-0.7, -0.7),
                z0=s.Hl - 0.6)
    dress_deck(b, upper, 33, bushes=[(-9.6, 11.0, 1.3), (-10.4, 18.0, 1.3), (3.0, 18.2, 1.5), (10.6, 16.0, 1.25),
                                     (10.6, 6.4, 1.1), (-1.0, 6.4, 1.0)],
               rocks=[(2.0, 12.0, (2.1, 1.9, 1.7))], pebbles=8, flowers=18, patch_n=7)
    dress_deck(b, lower, 43, bushes=[(-11.0, -14.8, 1.5), (-10.8, -3.5, 1.1), (-10.8, 6.6, 0.9),
                                     (1.0, -14.6, 1.2), (10.8, -14.6, 1.15), (10.8, -3.6, 1.1)],
               rocks=[(4.0, -9.0, (1.9, 1.7, 1.5))], pebbles=8, flowers=18, patch_n=8)
    rubble, tufts = edge_foot(s, 56, n_rubble=12, n_tufts=12)
    foot(b, s, 53,
         shards=[(-10.0, -19.4, "f", 3.6, 2.4), (-1.0, -19.5, "f", 3.0, 2.0), (7.5, -19.4, "f", 4.0, 2.4),
                 (-15.4, -8.0, "l", 3.2, 2.0), (15.4, -12.0, "r", 3.0, 2.0)],
         clumps=[(-14.6, -18.8, 1.25), (-5.5, -19.1, 1.0), (3.0, -19.2, 1.05), (14.6, -18.4, 1.1),
                 (-15.0, 6.0, 0.95), (15.0, 0.0, 0.95)],
         rubble=rubble, tufts=tufts)
    streaks(b, [(-7.0, -19.2, "f", 7.0, 2.2), (4.0, -19.2, "f", 7.0, 1.8), (-2.0, s.yF - 1.0, "f", 15.0, 2.4),
                (8.0, s.yF - 1.0, "f", 15.0, 1.8)], 63)
    return b.finish("variant", "precise", 7500, "B. WIDE: broad low terraces, decks z=8 / z=16, 20 deep each; 32x40",
                    bound=(16.0, -20.0, 20.0))


# The ramp: along the +X end, 8 wide, from the ground at the front to z=24 at the
# back. 24 studs up needs 34.3 studs of run to stay under 35 degrees, so its toe
# runs out RAMP_TOE studs in front of the 32 x 32 ledge.
RAMP_Y0, RAMP_Y1 = -18.9, 15.6


def ramp_z(y):
    return max(0.0, min(24.0, 24.0 * (y - RAMP_Y0) / (RAMP_Y1 - RAMP_Y0)))


def build_ramp(kit):
    x0, x1 = 5.4, 15.4
    s = Spec(ys=1.5, xl=-12.2, step_x=-5.0, step_d=5.0, seed=4, gap=3.2, front_in=2.8,
             ramp={"x0": x0, "z": ramp_z})
    b = Builder(kit, "TerracedLedgeRampEnd", 231)
    lower, upper = terrace(b, s, ramp={"x0": x0, "z": ramp_z})
    a = b.a
    # rock wall under the ramp, facing +X, and a low closing face on the toe's -X side
    band(b, [(x1, RAMP_Y0 + 2.0), (x1, s.yb)], 0.0, lambda x, y: ramp_z(y) + 0.6, 401, wr=(3.4, 5.0),
         drop=(0.5, 0.8), min_h=1.0)
    band(b, [(x0 + 0.6, s.F + 0.4), (x0 + 0.6, RAMP_Y0 + 1.5)], 0.0, lambda x, y: ramp_z(y) + 0.5, 402,
         wr=(1.8, 2.6), depth=2.0, min_h=0.6, occlude=False)
    # dirt ramp surface with step seams every ~3.4 studs (path_dark ridges)
    xa, xb = x0 + 0.6, x1 - 1.6          # 7.8 studs of dirt, grass borders either side
    k = 10
    ys = [RAMP_Y0 + (RAMP_Y1 - RAMP_Y0) * i / k for i in range(k + 1)]
    rows = [(a.bm.verts.new((xa, y, ramp_z(y) + 0.3)), a.bm.verts.new(((xa + xb) / 2, y, ramp_z(y) + 0.3)),
             a.bm.verts.new((xb, y, ramp_z(y) + 0.3))) for y in ys]
    up = Vector((0, -0.6, 0.8)).normalized()
    fs = []
    for i in range(k):
        r0, r1 = rows[i], rows[i + 1]
        fs += [face(a, (r0[0], r0[1], r1[1], r1[0]), up), face(a, (r0[1], r0[2], r1[2], r1[1]), up)]
    rng = random.Random(403)
    for f in fs:
        if f:
            paint(a, [f], PATH, rng.uniform(0.95, 1.05), 0.03)
    for y in ys[1:-1]:
        z = ramp_z(y) + 0.3
        a.box((xb - xa - 0.2, 0.9, 0.45), loc=((xa + xb) / 2, y, z + 0.05), mat=PATH_D, tint=1.0)
    # front lip of the toe
    face(a, (rows[0][0], rows[0][2], a.bm.verts.new((xb, RAMP_Y0, 0.0)), a.bm.verts.new((xa, RAMP_Y0, 0.0))),
         Vector((0, -1, 0)))
    # sloped grass borders: outer (+X) strip with a lip, inner strip at the wall foot
    rz = (lambda x, y: ramp_z(y) + 0.55)
    outer = [V2(p) for p in ((xb, RAMP_Y0 + 1.0), (x1 + 0.1, RAMP_Y0 + 1.0), (x1 + 0.1, s.yb), (xb, s.yb))]
    grass_cap(b, outer, rz, lambda p: (p.x > x1 - 0.2 or p.y < RAMP_Y0 + 1.05) and p.y < s.yb - 0.05, 404,
              hang=(0.2, 0.55))
    inner = [V2(p) for p in ((x0 - 0.4, RAMP_Y0 + 2.5), (xa, RAMP_Y0 + 2.5), (xa, s.yb), (x0 - 0.4, s.yb))]
    grass_cap(b, inner, lambda x, y: ramp_z(y) + 0.42, lambda p: False, 405, layers=((0.5, GRASS, 1.0),))
    rng = random.Random(406)
    for y, r in ((-12.0, 1.0), (-4.0, 1.15), (4.5, 1.0), (11.5, 1.2)):
        bush(b, (x1 - 0.3, y, ramp_z(y) + 0.45), r, rng)
    for y in (-8.0, 1.0, 8.0):
        bush(b, (x0 + 0.2, y, ramp_z(y) + 0.4), 0.7, rng, lobes=2)
    filler_rock(b, (s.step_x - 3.0, s.ys + s.step_d - 2.8), (4.2, 4.0, 10.6), 80, slope_dir=(-0.7, -0.7),
                z0=s.Hl - 0.6)
    dress_deck(b, upper, 34, bushes=[(-9.6, 11.2, 1.3), (-10.4, 14.4, 1.25), (1.0, 14.4, 1.45), (2.6, 6.4, 1.0)],
               rocks=[(-3.5, 10.5, (2.1, 1.9, 1.8))], pebbles=6, flowers=14, patch_n=5)
    dress_deck(b, lower, 44, bushes=[(-10.6, -10.6, 1.5), (-11.0, -4.6, 1.0), (-1.0, -11.0, 1.1), (3.6, -4.8, 1.0)],
               rocks=[(-4.0, -7.0, (1.9, 1.7, 1.6))], pebbles=6, flowers=14, patch_n=5)
    rubble, tufts = edge_foot(s, 57, n_rubble=10, n_tufts=10, right=False)
    rubble = [r for r in rubble if r[0] < x0 - 1.0]          # nothing buried under the ramp toe
    tufts = [t for t in tufts if t[0] < x0 - 1.0]
    foot(b, s, 54,
         shards=[(-11.0, -15.4, "f", 4.6, 2.6), (-3.0, -15.5, "f", 3.6, 2.2), (2.6, -15.4, "f", 4.8, 2.4),
                 (-15.4, -6.0, "l", 4.0, 2.2)],
         clumps=[(-14.6, -14.8, 1.25), (-7.0, -15.1, 1.05), (15.4, -16.5, 0.85), (15.5, -6.0, 0.9),
                 (-15.0, 6.0, 0.95)],
         rubble=rubble + [(15.6, 2.0, 0.6), (15.5, -11.0, 0.7)], tufts=tufts)
    streaks(b, [(-8.0, -15.2, "f", 11.0, 2.8), (1.0, -15.2, "f", 11.0, 2.4), (-1.0, s.yF - 1.0, "f", 23.0, 2.6),
                (15.4, -4.0, "r", ramp_z(-4.0), 2.0), (15.4, 8.0, "r", ramp_z(8.0), 3.0)], 64)
    return b.finish("variant", "precise", 8000,
                    "C. RAMP END: 32x32x24 ledge, dirt ramp 8 wide on +X climbing 0->24 front to back at ~35 deg "
                    "(toe runs 2.9 past the front, so the ledge grid centre is 1.45 +Y of the origin)",
                    bound=(16.0, RAMP_Y0, 16.0))


# ---------------------------------------------------------------------------
# parts
# ---------------------------------------------------------------------------


def build_upper_cap(kit):
    """The upper grass slab with its earth / stone edge band and bushes."""
    s = CAP
    b = Builder(kit, "TerracedLedgeUpperCap", 241)
    up = [V2((p[0], p[1])) for p in s.upper_path()]
    deck = grass_cap(b, up, 2.5, lambda p: True, 242, hang=(0.0, 0.35),
                     layers=((0.6, GRASS, 1.0), (2.05, EARTH, 1.0), (2.5, ROCK, 1.0)), flat_bottom=True)
    rng = random.Random(243)
    # stones set in the earth band along the front and the sides
    for x, y, nx, ny in ((-10.0, 3.0, 0, -1), (-3.5, 0.5, 0, -1), (3.0, 0.5, 0, -1), (9.5, 0.5, 0, -1),
                         (-13.2, 8.0, -1, 0), (13.2, 8.0, 1, 0)):
        stone(b, (x + nx * 0.1, y + ny * 0.1, 0.35), (1.6, 0.9, 1.2), rng, n=8)
    dress_deck(b, deck, 244, bushes=[(-11.0, 5.2, 1.3), (6.5, 13.6, 1.6), (11.6, 12.6, 1.2), (-11.0, 13.4, 1.2),
                                     (10.8, 2.2, 1.0)],
               rocks=[(-7.0, 8.0, (2.3, 2.0, 1.9))], pebbles=6, flowers=12, patch_n=4)
    return b.finish("part", "precise", 2000, "upper grass slab; seats on the upper tier / MainCliffBase tray")


def build_lower_shelf(kit):
    """The lower grass shelf on a short rock rim."""
    b = Builder(kit, "TerracedLedgeLowerShelf", 251)
    E = 14.6
    corners = [(-E, 6.8), (-E, -6.8), (E, -6.8), (E, 6.8)]
    band(b, corners, 0.0, 3.0, 252, wr=(3.4, 5.4), depth=2.6, drop=(0.3, 0.6), min_h=0.5, closed=True,
         occlude=False, lean=0.1)
    deck = grass_cap(b, [V2(p) for p in corners], 3.0, lambda p: True, 253)
    dress_deck(b, deck, 254, bushes=[(-13.4, -5.6, 1.5), (-2.5, 5.6, 1.4), (13.2, 5.4, 1.2)],
               rocks=[(-6.0, -1.0, (2.0, 1.7, 1.6))], pebbles=5, flowers=9, patch_n=4)
    return b.finish("part", "precise", 2500, "lower grass shelf on a rock rim; seats in the MainCliffBase tray",
                    bound=(16.0, -8.0, 8.0))


def build_filler(kit):
    b = Builder(kit, "TerracedLedgeCornerFillerRock", 261)
    filler_rock(b, (0.0, 0.0), (5.0, 5.0, 12.0), 262)
    return b.finish("part", "hull", 600, "wedge rock closing the side gap of the stepped upper tier")


def build_base(kit):
    """The lower rock block with a recessed tray top the shelves seat into."""
    b = Builder(kit, "TerracedLedgeMainCliffBase", 271)
    E, yb = 14.6, 15.6
    band(b, [(-E, yb), (-E, -E), (E, -E), (E, yb)], 0.0, 12.0, 11, keep_back=True, occlude=False)
    # tray floor inside the rim, below the column tops
    a = b.a
    rng = random.Random(272)
    tray = [V2(p) for p in ((-11.4, -11.4), (11.4, -11.4), (11.4, 15.2), (-11.4, 15.2))]
    res = delaunay_2d_cdt(resample_closed(tray, 5.0), [], [], 0, 1e-5)
    vs = [a.bm.verts.new((p.x, p.y, 9.6 + rng.uniform(-0.15, 0.15))) for p in res[0]]
    fs = [face(a, [vs[k] for k in t], Z) for t in res[2]]
    for f in fs:
        if f:
            paint(a, [f], ROCK if rng.random() < 0.7 else COOL, rng.uniform(0.95, 1.05), 0.0)
    connector(b, 32.0, 32.0, 12.5)
    return b.finish("part", "precise", 5000, "32x32x12 columnar base, hollow tray top at z~9.6, +Y connector",
                    bound=(16.0, -16.0, 16.0))


def build(kit):
    # parts order sets the runner's exploded row: the tall filler rock goes
    # between the two low slabs so nothing tall stands beside it
    return [build_hero(kit), build_upper_cap(kit), build_filler(kit), build_lower_shelf(kit), build_base(kit),
            build_shallow(kit), build_wide(kit), build_ramp(kit)]
