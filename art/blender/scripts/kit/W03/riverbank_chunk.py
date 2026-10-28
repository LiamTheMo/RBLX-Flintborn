"""W03 row 1: RIVERBANK CHUNK, a modular 32 x 32 riverbank terrain tile.

Hero "RiverbankChunk" (32 x 32 x ~10.4, pines to ~17): land on the back (+Y),
water on the front (-Y). Back to front: a vivid yellow-green grass top
(z=10.4) on a thin dark-brown soil band with a lumpy overhanging lip, a row of
big columnar rock blocks with bevelled light tops (the cliff, ~y -4 to 0)
stepping down to lower blocks, a warm sand beach sloping from z=1.8 at the
rock foot to the waterline at z=1.0, then ONE flat see-through w03_water slab
at z=1.0 over the deep teal w03_riverbed at z=0.2, with loose faceted boulders
standing in it. Everything under the water surface (bed, beach slope, boulder
bases, edge walls under the skirt) is w03_riverbed. Foam and flow streaks are
VFX, not mesh: water_foam sockets along the waterline and at each boulder in
the river, and water_flow beams lying on the river. A sand path winds from the back-left of the grass top to the front-right,
where it drops down a ramp through a gap in the rock row to the beach.

Parts: RiverbankGrassTop, RiverbankSandStrip, RiverbankRockSlope,
RiverbankWaterPlane (the hero's pieces, in place, so they re-assemble).
Variants: RiverbankStraight, RiverbankInnerBend (concave), RiverbankOuterBend
(convex).

Technique: every tile is described in a "frame" with an along-shore coordinate
s and a depth coordinate d (d grows inland). The straight tiles and the inner bend
use d = y (the bend bows its shore and cliff ~9 studs inland round a bay, 0 at the
seams); the outer bend uses a CornerFrame: the land fills the back corner (+X,+Y)
and turns round a rounded point facing the front corner, with water on both front
edges (d = x on the -X leg, d = y on the -Y leg). On every seam edge d equals the hero's
y, so the tiles chain (shore at d = -7.5, grass rim at d = -0.4). The
cross-section (water, beach, cliff, grass) is a function of d, the surfaces are
Delaunay caps of regions clipped along d-contours, and the tile edges are walls
(water over the sand bed, sand under the beach, a soil band under the grass; on the
x = +/-16 sides the land is a row of separate fat columns with deep creases, in
front of a recessed backing wall; the back edge uses creased column panels). The stone is w03_rock, a pale cool grey sampled from the
reference. The cliff is a few big
fat rounded columns (hulls of 8-sided superellipse rings with a big, fairly flat top
chamfer), in two rows: a back row of 6-7.5 wide columns standing in front of the
grass rim with their bevelled tops level with the turf (so they catch the sun), and a
front row about half as tall, plus at most two small low blocks.
Colours: ONE base colour per material with a small random Tint, never chosen by
face direction; the renderer and Roblox light the facets. Genuinely different
materials of similar hue (turf vs bush leaves, rock vs daisy petals, bark vs
sand) are named in obj['kit_two_tone_ok'].
"""

import bisect
import math
import random

import bmesh
import numpy as np
from mathutils import Vector
from mathutils.geometry import delaunay_2d_cdt

SUBJECT = "RiverbankChunk"
ROW = 1
# The sheet's SIDE / REAR cell looks at the right-hand end of the tile from a little in front
# (water on the left, the cliff's sunlit column faces and grass on the right).
SIDE_AZIMUTH = 62
# The shared W03 sheet palette, identical in all four W03 modules: ONE key per material.
# Existing flintkit keys also used here: pine, bark, flower_white, flower_yellow.
PALETTE = {
    "w03_grass": ("#A6CA18", 0.95, 0, 0),
    "w03_soil": ("#6A4524", 0.95, 0, 0),
    "w03_sand": ("#E2B67C", 0.95, 0, 0),
    "w03_rock": ("#B2AFBA", 0.9, 0, 0),
    "w03_riverbed": ("#0B6E8F", 0.9, 0, 0),
    "w03_water": ("#18CFFA", 0.15, 0, 0),
    "w03_bush": ("#4C9C18", 0.8, 0, 0),
}

PI = math.pi
HALF = 16.0
WZ, BED, GZ, SOIL, SAND_TOP = 1.0, 0.2, 10.4, 0.8, 1.8
# ONE colour per material; everything under the water surface is the riverbed key
ROCK, GRASS, SAND, SOILM, WATER = "w03_rock", "w03_grass", "w03_sand", "w03_soil", "w03_water"
RBED = "w03_riverbed"
BSCALE = 1.3  # shore boulders: spec sizes scaled up to the reference's chunky rocks


# ---------------------------------------------------------------------------
# 2D geometry
# ---------------------------------------------------------------------------


class Poly:
    """Closed 2D polygon, stored counter-clockwise."""

    def __init__(self, pts):
        P = []
        for p in pts:
            v = Vector((p[0], p[1]))
            if not P or (v - P[-1]).length > 0.02:
                P.append(v)
        if len(P) > 2 and (P[0] - P[-1]).length < 0.02:
            P.pop()
        area = sum(P[i - 1].x * P[i].y - P[i].x * P[i - 1].y for i in range(len(P)))
        if area < 0:
            P.reverse()
        self.p = P
        self.a = np.array([(v.x, v.y) for v in P]) if P else np.zeros((0, 2))
        self.b = np.roll(self.a, -1, axis=0)

    def __len__(self):
        return len(self.p)

    def inside(self, x, y):
        a, b = self.a, self.b
        cond = (a[:, 1] > y) != (b[:, 1] > y)
        with np.errstate(divide="ignore", invalid="ignore"):
            xi = a[:, 0] + (y - a[:, 1]) * (b[:, 0] - a[:, 0]) / (b[:, 1] - a[:, 1])
        return bool(np.count_nonzero(cond & (x < xi)) % 2)

    def dist(self, x, y):
        a, b = self.a, self.b
        d = b - a
        p = np.array((x, y))
        t = np.clip(((p - a) * d).sum(1) / ((d * d).sum(1) + 1e-12), 0, 1)
        q = a + d * t[:, None]
        return float(np.sqrt(((q - p) ** 2).sum(1)).min())

    def sdist(self, x, y):
        d = self.dist(x, y)
        return d if self.inside(x, y) else -d

    def length(self):
        return float(np.sqrt(((self.b - self.a) ** 2).sum(1)).sum())

    def resample(self, step):
        P = self.p + [self.p[0]]
        out = []
        for k in range(len(P) - 1):
            d = P[k + 1] - P[k]
            n = max(1, int(round(d.length / step)))
            for s in range(n):
                out.append(P[k] + d * (s / n))
        return Poly(out)

    def coarse(self, step):
        """Drop outline points closer than `step` to the last kept one, keeping corners
        (turns sharper than ~25 degrees), so dense contour samples don't bloat caps."""
        P = self.p
        n = len(P)
        keep = [P[0]]
        for i in range(1, n):
            a, b, c = P[i - 1], P[i], P[(i + 1) % n]
            d1, d2 = b - a, c - b
            turn = d1.length > 1e-6 and d2.length > 1e-6 and d1.normalized().dot(d2.normalized()) < 0.9
            if turn or (b - keep[-1]).length >= step:
                keep.append(b)
        return Poly(keep)

    def bbox(self):
        return (float(self.a[:, 0].min()), float(self.a[:, 1].min()),
                float(self.a[:, 0].max()), float(self.a[:, 1].max()))

    def clip_fn(self, g, curve=None):
        """Keep the region g(p) >= 0; where the outline leaves and re-enters it,
        the cut follows curve(p_exit, p_entry)."""
        P = self.p
        n = len(P)
        start = next((i for i in range(n) if g(P[i]) >= 0), None)
        if start is None:
            return Poly([])
        P = P[start:] + P[:start] + [P[start]]

        def cross(p, q):
            lo, hi = 0.0, 1.0
            gp = g(p)
            for _ in range(24):
                m = (lo + hi) / 2
                if (g(p.lerp(q, m)) >= 0) == (gp >= 0):
                    lo = m
                else:
                    hi = m
            return p.lerp(q, (lo + hi) / 2)

        out = [P[0]]
        exit_pt = None
        for k in range(1, len(P)):
            p, q = P[k - 1], P[k]
            gp, gq = g(p), g(q)
            if gq >= 0:
                if gp < 0:
                    x = cross(p, q)
                    if exit_pt is not None and curve:
                        out += curve(exit_pt, x)
                    exit_pt = None
                    out.append(x)
                if k < len(P) - 1:
                    out.append(q)
            elif gp >= 0:
                x = cross(p, q)
                out.append(x)
                exit_pt = x
        return Poly(out)


def square(step=1.0):
    return Poly([(-HALF, -HALF), (HALF, -HALF), (HALF, HALF), (-HALF, HALF)]).resample(step)


class Path2:
    """Arc-length parametrised open polyline."""

    def __init__(self, pts):
        self.P = [Vector((p[0], p[1])) for p in pts]
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

    def dist(self, x, y):
        p = Vector((x, y))
        best = 1e9
        for k in range(len(self.P) - 1):
            a, b = self.P[k], self.P[k + 1]
            d = b - a
            t = max(0.0, min(1.0, (p - a).dot(d) / max(d.length_squared, 1e-9)))
            best = min(best, (a + d * t - p).length)
        return best


def catmull(p0, p1, p2, p3, t):
    t2, t3 = t * t, t * t * t
    return 0.5 * ((2 * p1) + (-p0 + p2) * t + (2 * p0 - 5 * p1 + 4 * p2 - p3) * t2
                  + (-p0 + 3 * p1 - 3 * p2 + p3) * t3)


def smooth_path(pts, step=1.0):
    P = [Vector(p) for p in pts]
    out = []
    for k in range(len(P) - 1):
        p0, p1, p2, p3 = P[max(k - 1, 0)], P[k], P[k + 1], P[min(k + 2, len(P) - 1)]
        n = max(1, int((p2 - p1).length / step))
        for s in range(n):
            out.append(catmull(p0, p1, p2, p3, s / n))
    out.append(P[-1])
    return out


def edge_of(p, q, eps=1e-3):
    m = (p + q) / 2
    if abs(m.x - HALF) < eps:
        return "E"
    if abs(m.x + HALF) < eps:
        return "W"
    if abs(m.y - HALF) < eps:
        return "N"
    return "S"


def split_by_edge(pts):
    """Split a run along the tile perimeter into (edge, points) sub-runs, one per tile side."""
    out = []
    for k in range(len(pts) - 1):
        p, q = pts[k], pts[k + 1]
        if (q - p).length < 1e-6:
            continue
        e = edge_of(p, q)
        if out and out[-1][0] == e:
            out[-1][1].append(q)
        else:
            out.append((e, [p, q]))
    return out


def smoothstep(e0, e1, x):
    t = max(0.0, min(1.0, (x - e0) / (e1 - e0)))
    return t * t * (3 - 2 * t)


# ---------------------------------------------------------------------------
# Frames: along-shore s, depth d (inland positive), equal to the hero's y on seams
# ---------------------------------------------------------------------------


class LineFrame:
    """Straight shore along X: s = x, d = y."""

    s0, s1 = -HALF, HALF

    def sd(self, x, y):
        return x, y

    def xy(self, s, d):
        return Vector((s, d))


class ArcFrame:
    """Quarter-arc shore around a tile corner C: d = sign * (r - 16), s = arc
    length at r = 16 from angle th0 to th1 (land on the left walking +s)."""

    def __init__(self, C, sign, th0, th1):
        self.C = Vector(C)
        self.sign = sign
        self.th0, self.th1 = th0, th1
        self.s0, self.s1 = 0.0, 16.0 * abs(th1 - th0)

    def sd(self, x, y):
        dx, dy = x - self.C.x, y - self.C.y
        r = math.hypot(dx, dy)
        th = math.atan2(dy, dx) if r > 1e-6 else self.th0
        mid = (self.th0 + self.th1) / 2  # unwrap atan2 round the arc's middle
        while th - mid > PI:
            th -= 2 * PI
        while th - mid < -PI:
            th += 2 * PI
        s = (th - self.th0) / (self.th1 - self.th0) * self.s1
        return s, self.sign * (r - 16.0)

    def xy(self, s, d):
        th = self.th0 + (self.th1 - self.th0) * s / self.s1
        r = 16.0 + self.sign * d
        return self.C + Vector((math.cos(th), math.sin(th))) * r


def inner_frame():  # water bay in the front corner (-X,-Y), land arcing round behind it
    return ArcFrame((-HALF, -HALF), 1, PI / 2, 0.0)


class CornerFrame:
    """Convex land corner: the land is the tile's back corner (+X,+Y) with a rounded
    point at (k, k) facing the front corner, water along both front edges (-X, -Y).
    d = x along the -X leg (y >= k), d = y along the -Y leg (x >= k), d = k - |p - K|
    round the point (K = (k, k)); s walks the shore from the back of the -X leg down
    round the point and out along the -Y leg (land on the left). On the seams
    (x = +16 and y = +16) d equals the straight tile's y, so they chain."""

    def __init__(self, k=4.0, rref=8.0):
        self.k, self.R = k, rref
        self.sA = HALF - k
        self.sB = self.sA + 0.5 * PI * rref
        self.s0, self.s1 = 0.0, self.sB + HALF - k

    def sd(self, x, y):
        k = self.k
        if x < k and y < k:
            dx, dy = x - k, y - k
            th = math.atan2(dy, dx)
            if th < 0:
                th += 2 * PI
            th = min(max(th, PI), 1.5 * PI)
            return self.sA + (th - PI) * self.R, k - math.hypot(dx, dy)
        if y >= k and (x < k or x < y):
            return HALF - y, x
        return self.sB + (x - k), y

    def xy(self, s, d):
        k = self.k
        if s <= self.sA:
            return Vector((d, HALF - s))
        if s >= self.sB:
            return Vector((k + (s - self.sB), d))
        th = PI + (s - self.sA) / self.R
        r = k - d
        return Vector((k + math.cos(th) * r, k + math.sin(th) * r))


def outer_frame():  # land promontory in the back corner (+X,+Y), water on both front edges
    return CornerFrame(1.8, 6.0)


# ---------------------------------------------------------------------------
# Mesh helpers
# ---------------------------------------------------------------------------


def paint(a, faces, mat, tint=1.0, var=0.04):
    mi = a._mi(mat)
    for f in faces:
        f.material_index = mi
        f.smooth = False
        t = tint * (1.0 + a.rng.uniform(-var, var)) if var else tint
        t = min(1.08, max(0.92, t))  # Tint is a small random variation only (runner limit 1.25x)
        for lp in f.loops:
            lp[a.tint_layer] = (t, t, t, 1.0)


def hull(a, fk, pts, paint_fn, facets=2.0):
    """Convex hull of pts; paint_fn(face) -> (mat, tint)."""
    bm = a.bm
    verts = [bm.verts.new(p) for p in pts]
    res = bmesh.ops.convex_hull(bm, input=verts, use_existing_faces=False)
    junk = list({g for g in res["geom_interior"] + res["geom_unused"]
                 if isinstance(g, bmesh.types.BMVert) and g.is_valid})
    if junk:
        bmesh.ops.delete(bm, geom=junk, context="VERTS")
    verts = [v for v in verts if v.is_valid]
    bmesh.ops.recalc_face_normals(bm, faces=fk._faces_of(verts))
    if facets:
        bmesh.ops.dissolve_limit(bm, angle_limit=math.radians(facets), verts=verts,
                                 edges=fk._edges_of(verts))
        verts = [v for v in verts if v.is_valid]
    bm.normal_update()
    for f in fk._faces_of(verts):
        m, t = paint_fn(f)
        paint(a, [f], m, t, 0.05)
    return verts


def rock_pick(rng, tint):
    """Rock facet colour: ONE rock (w03_rock) with a small random Tint, never chosen by
    face direction (Roblox lights the facets; light tops / dark sides come from the sun)."""
    return ROCK, tint * rng.uniform(0.96, 1.04)


def column_paint(rng, tint, u=None):
    return lambda f: rock_pick(rng, tint)


def boulder_paint(rng, tint):
    return lambda f: rock_pick(rng, tint)


def column(a, fk, c, u, w, dep, h, z0, tint=None, bulge=0.3, lean=(0.0, 0.0), sides=8):
    """Fat rounded rock column: the hull of jittered rounded-rectangle rings
    (6-8 sided), bulging a little at mid height, with a big chamfer round its top
    (the bevelled light top of the reference comes from that chamfer facing the sun).
    u = unit along the face, front n = (u.y, -u.x) points at the water."""
    rng = a.rng
    u = Vector(u)
    n = Vector((u.y, -u.x))
    hw, hd = w / 2, dep / 2
    tint = tint if tint is not None else rng.uniform(0.99, 1.06)
    # big chamfer round the top: ~25% of the column width (the reference's broad bevelled tops)
    ch = 0.32 * w * rng.uniform(0.94, 1.06)
    ch = max(0.5, min(ch, h * 0.3, hd * 0.7, 2.5))
    ex = rng.uniform(0.7, 0.82)  # superellipse exponent: ~0.75 gives a fat, rounded 8-sided barrel
    ph = rng.uniform(-0.12, 0.12)

    def P(lu, lv, z):
        t = (z - z0) / h if h > 1e-6 else 0.0
        return Vector((c[0] + u.x * (lu + lean[0] * t) + n.x * (lv + lean[1] * t),
                       c[1] + u.y * (lu + lean[0] * t) + n.y * (lv + lean[1] * t), z))

    def ring(sx, sy, j):
        out = []
        for k in range(sides):
            ang = 2 * PI * (k + 0.5) / sides + ph + rng.uniform(-0.12, 0.12)
            cx, cy = math.cos(ang), math.sin(ang)
            out.append((math.copysign(abs(cx) ** ex, cx) * sx + rng.uniform(-j, j),
                        math.copysign(abs(cy) ** ex, cy) * sy + rng.uniform(-j, j)))
        return out

    pts = []
    zt = z0 + h
    zm = z0 + h * rng.uniform(0.4, 0.55)
    bul = 1.0 + rng.uniform(0.01, 0.04) + bulge * 0.03
    # plain 8-sided hull: foot ring, a slight mid bulge, the shoulder ring, then a big
    # ~40-degree chamfer up to a smaller flat top ring. The chamfer faces up and catches the
    # sun like the reference's light bevelled tops (lighting, not paint).
    # the shoulder sits ~0.55 x the inset below the top: a broad, fairly flat (~29 degree)
    # bevel that faces the sky and reads bright
    levels = [(z0, 1.0, 0.1), (zm, bul, 0.12), (zt - ch * 0.55, 1.0, 0.06)]
    for z, sc, j in levels:
        for lu, lv in ring(hw * sc, hd * sc, j):
            pts.append(P(lu, lv, z + (rng.uniform(-0.15, 0.15) if z0 < z < zt - ch else 0.0)))
    tilt = rng.uniform(-0.15, 0.15)
    for lu, lv in ring(max(0.4, hw - ch), max(0.4, hd - ch), 0.06):
        pts.append(P(lu, lv, zt + tilt * lu / max(hw, 0.1) + rng.uniform(-0.04, 0.04)))
    return hull(a, fk, pts, column_paint(rng, tint, u), facets=3.0)


def chunk(a, fk, centre, size, rough=0.1, n=26, floor=None, exp=0.6, facets=6.0):
    """Rounded faceted boulder: hull of a jittered superellipsoid, flat-cut at floor."""
    rng = a.rng
    cx, cy, cz = centre
    sx, sy, sz = size[0] / 2, size[1] / 2, size[2] / 2
    pts = []
    for _ in range(n):
        th = rng.uniform(0, 2 * PI)
        ph = math.acos(rng.uniform(-1, 1))
        x, y, z = math.sin(ph) * math.cos(th), math.sin(ph) * math.sin(th), math.cos(ph)
        sp = lambda v: math.copysign(abs(v) ** exp, v)  # noqa: E731
        r = 1 + rng.uniform(-rough, rough)
        p = Vector((cx + sp(x) * sx * r, cy + sp(y) * sy * r, cz + sp(z) * sz * r))
        if floor is not None:
            p.z = max(p.z, floor)
        pts.append(p)
    return hull(a, fk, pts, boulder_paint(rng, rng.uniform(0.97, 1.06)), facets=facets)


def boulder(a, fk, x, y, zb, s, tall=0.9):
    """Faceted boulder of width ~s standing on zb; returns its half-width."""
    rng = a.rng
    sx, sy = s * rng.uniform(1.0, 1.2), s * rng.uniform(0.85, 1.0)
    sz = s * 1.05 * tall
    chunk(a, fk, (x, y, zb + sz * 0.3), (sx, sy, sz), floor=zb)
    return (sx + sy) / 4


def pebble(a, fk, x, y, z, s):
    chunk(a, fk, (x, y, z + s * 0.12), (s, s * 0.85, s * 0.6), n=10, floor=z - 0.05, exp=0.7, facets=8.0)


def cap(a, poly, H, mat, spacing=2.4, jz=0.05, seed=0, matfn=None, var=0.03):
    """Triangulated surface filling `poly`, draped on H(x, y)."""
    bnd = poly.coarse(min(1.3, spacing * 0.5)).resample(min(1.3, spacing * 0.5))
    coords = [Vector((p.x, p.y)) for p in bnd.p]
    edges = [(i, (i + 1) % len(coords)) for i in range(len(coords))]
    nb = len(coords)
    r = random.Random(seed)
    x0, y0, x1, y1 = poly.bbox()
    j = 0
    y = y0 + spacing * 0.5
    while y < y1:
        x = x0 + spacing * (0.25 + 0.5 * (j % 2))
        while x < x1:
            px, py = x + r.uniform(-0.28, 0.28) * spacing, y + r.uniform(-0.28, 0.28) * spacing
            if poly.sdist(px, py) > spacing * 0.42:
                coords.append(Vector((px, py)))
            x += spacing
        y += spacing * 0.87
        j += 1
    res = delaunay_2d_cdt(coords, edges, [], 0, 1e-5)
    vco, faces, orig = res[0], res[2], res[3]
    bm = a.bm
    vmap = {}

    def V(k):
        if k not in vmap:
            p = vco[k]
            border = any(i < nb for i in orig[k])
            z = H(p.x, p.y) + (0.0 if border else r.uniform(-jz, jz))
            vmap[k] = bm.verts.new((p.x, p.y, z))
        return vmap[k]

    out = []
    for f in faces:
        cx = sum(vco[k].x for k in f) / len(f)
        cy = sum(vco[k].y for k in f) / len(f)
        if not poly.inside(cx, cy):
            continue
        try:
            bf = bm.faces.new([V(k) for k in f])
        except ValueError:
            continue
        bf.normal_update()
        if bf.normal.z < 0:
            bf.normal_flip()
        out.append(bf)
        m, t = matfn(cx, cy) if matfn else (mat, 1.0)
        paint(a, [bf], m, t, var)
    return out


def band(a, pts, ztop, zbot, mat, tint=1.0, var=0.04, closed=False, out_bot=0.0):
    """Vertical band under a polyline (outside to the right of travel).
    ztop/zbot: float or f(p)."""
    bm = a.bm
    P = [Vector((p[0], p[1])) for p in pts] + ([Vector((pts[0][0], pts[0][1]))] if closed else [])
    zt = ztop if callable(ztop) else (lambda p, v=ztop: v)
    zb = zbot if callable(zbot) else (lambda p, v=zbot: v)
    rows = []
    for k, p in enumerate(P):
        t = P[min(k + 1, len(P) - 1)] - P[max(k - 1, 0)]
        t = t.normalized() if t.length > 1e-9 else Vector((1, 0))
        n = Vector((t.y, -t.x))
        q = p + n * out_bot * a.rng.uniform(0.75, 1.0)
        rows.append((bm.verts.new((p.x, p.y, zt(p))), bm.verts.new((q.x, q.y, zb(p)))))
    faces = []
    for k in range(len(rows) - 1):
        (t0, b0), (t1, b1) = rows[k], rows[k + 1]
        if (t0.co - b0.co).length < 1e-4 and (t1.co - b1.co).length < 1e-4:
            continue
        try:
            faces.append(bm.faces.new((t0, b0, b1, t1)))
        except ValueError:
            continue
    paint(a, faces, mat, tint, var)
    return faces


def ribbon(a, pts, width, zfn, mat, lift=0.05, wobble=0.0, step=0.8, smooth=True, taper=False,
           var=0.03, seed=0, tint=1.0):
    """Flat strip draped on zfn(x, y) (or explicit z per point when pts are 3D)."""
    bm = a.bm
    r = random.Random(seed)
    ph = [r.uniform(0, 2 * PI) for _ in range(4)]
    P3 = [Vector((p[0], p[1], p[2] if len(p) > 2 else 0.0)) for p in pts]
    S = smooth_path(P3, step) if smooth else P3
    rows = []
    for k, p in enumerate(S):
        t = (S[min(k + 1, len(S) - 1)] - S[max(k - 1, 0)])
        t = Vector((t.x, t.y)).normalized()
        nn = Vector((-t.y, t.x))
        f = 0.6 if taper and (k == 0 or k == len(S) - 1) else 1.0
        wl = width / 2 * f * (1 + wobble * (0.6 * math.sin(k * 0.55 + ph[0]) + 0.4 * math.sin(k * 1.7 + ph[1])))
        wr = width / 2 * f * (1 + wobble * (0.6 * math.sin(k * 0.6 + ph[2]) + 0.4 * math.sin(k * 1.5 + ph[3])))
        c = Vector((p.x, p.y))
        L, R = c + nn * wl, c - nn * wr
        if zfn is None:
            zl = zr = p.z + lift
        else:
            zl, zr = zfn(L.x, L.y) + lift, zfn(R.x, R.y) + lift
        rows.append((bm.verts.new((R.x, R.y, zr)), bm.verts.new((L.x, L.y, zl))))
    faces = []
    for k in range(len(S) - 1):
        faces.append(bm.faces.new((rows[k][0], rows[k + 1][0], rows[k + 1][1], rows[k][1])))
    paint(a, faces, mat, tint, var)
    return rows


def dirt_patch(a, cx, cy, z, rad, seg=9):
    """Flat wobbly patch of bare soil (w03_soil) on the turf."""
    rng = a.rng
    bm = a.bm
    ph = rng.uniform(0, 2 * PI)
    vs = []
    for k in range(seg):
        ang = 2 * PI * k / seg
        re = rad * (1 + 0.18 * math.sin(2 * ang + ph) + rng.uniform(-0.1, 0.1))
        vs.append(bm.verts.new((cx + math.cos(ang) * re, cy + math.sin(ang) * re, z)))
    f = bm.faces.new(vs)
    f.normal_update()
    if f.normal.z < 0:
        f.normal_flip()
    paint(a, [f], SOILM, 1.0, 0.03)


# ---------------------------------------------------------------------------
# Vegetation (lobby build_07 recipes, recoloured for the W03 sheet)
# ---------------------------------------------------------------------------


def frond(a, base, ang, elev, L, w, mat, droop=0.3, tint=None):
    bm = a.bm
    B = Vector(base)
    d = Vector((math.cos(ang), math.sin(ang), 0))
    up = Vector((0, 0, 1))
    side = Vector((-math.sin(ang), math.cos(ang), 0))
    dv = d * math.cos(elev) + up * math.sin(elev)
    T = B + dv * L - up * (L * droop * math.cos(elev))
    M = B + dv * (L * 0.5)
    vs = [bm.verts.new(p) for p in (B, M - side * w / 2, M + up * (w * 0.22), M + side * w / 2, T)]
    b, mr, r, ml, t = vs
    faces = [bm.faces.new(f) for f in ((b, mr, r), (b, r, ml), (r, mr, t), (r, t, ml))]
    for f in faces:
        f.normal_update()
        if f.normal.z < 0:
            f.normal_flip()
    paint(a, faces, mat, tint if tint is not None else a.rng.uniform(0.95, 1.08), 0.05)


def tuft(a, x, y, z, s=1.0, n=3, dark=True):
    rng = a.rng
    mats = ["w03_bush"]  # small leafy sprigs: the leaf green, so they read on the turf
    for i in range(n):
        ang = 2 * PI * i / n + rng.uniform(-0.5, 0.5)
        frond(a, (x + rng.uniform(-0.2, 0.2) * s, y + rng.uniform(-0.2, 0.2) * s, z - 0.05),
              ang, rng.uniform(1.0, 1.35), rng.uniform(0.7, 1.1) * s, 0.28 * s, rng.choice(mats), droop=0.12)


def fern(a, x, y, z, s=1.0):
    rng = a.rng
    k = 7
    for i in range(k):
        ang = 2 * PI * i / k + rng.uniform(-0.25, 0.25)
        frond(a, (x, y, z - 0.05), ang, rng.uniform(0.6, 0.95), rng.uniform(1.6, 2.2) * s,
              0.75 * s, "w03_bush", droop=0.45)


# bush and fern leaves: ONE leaf green (w03_bush), a different material from the turf
BUSH_KEYS = ("w03_bush",)


def lobe(a, cx, cy, cz, r, mat, flat=0.8, n=14):
    """One faceted leafy blob: hull of jittered points on a squashed sphere, its
    buried underside flattened onto the ground."""
    rng = a.rng
    pts = []
    for k in range(n):
        th = 2 * PI * (k + rng.uniform(-0.3, 0.3)) / n * 2.0
        zc = 1 - 2 * (k + 0.5) / n
        rr = math.sqrt(max(0.0, 1 - zc * zc)) * r * rng.uniform(0.88, 1.1)
        pts.append(Vector((cx + math.cos(th) * rr, cy + math.sin(th) * rr,
                           max(cz - r * flat * 0.55, cz + zc * r * flat * rng.uniform(0.9, 1.08)))))
    t = rng.uniform(0.95, 1.05)
    return hull(a, a.fk_ref, pts, lambda f: (mat, t), facets=4.0)


def bush(a, x, y, z, s=1.0):
    """Round leafy bush: 3-4 faceted lobes round a taller crown lobe."""
    rng = a.rng
    R = 1.15 * s
    k = rng.choice((3, 4))
    for i in range(k):
        ang = 2 * PI * i / k + rng.uniform(-0.35, 0.35)
        r = R * rng.uniform(0.55, 0.7)
        lobe(a, x + math.cos(ang) * R * 0.55, y + math.sin(ang) * R * 0.55, z + r * 0.5, r, rng.choice(BUSH_KEYS), n=9)
    r = R * rng.uniform(0.66, 0.78)
    lobe(a, x + rng.uniform(-0.2, 0.2) * R, y + rng.uniform(-0.2, 0.2) * R, z + R * 0.85, r,
         rng.choice(BUSH_KEYS), flat=0.85, n=11)


def star_cone(a, x, y, z, r, h, pts=8, inner=0.62, droop=0.35, mat="pine", rot=0.0):
    bm, rng = a.bm, a.rng
    ring = []
    for k in range(2 * pts):
        ang = rot + PI * k / pts
        rr = r * (1.0 if k % 2 == 0 else inner) * rng.uniform(0.9, 1.08)
        dz = -droop * r * (1.0 if k % 2 == 0 else 0.25) * rng.uniform(0.7, 1.1)
        ring.append(bm.verts.new((x + math.cos(ang) * rr, y + math.sin(ang) * rr, z + dz)))
    apex = bm.verts.new((x + rng.uniform(-0.1, 0.1), y + rng.uniform(-0.1, 0.1), z + h))
    cen = bm.verts.new((x, y, z + h * 0.12))
    faces = []
    m = len(ring)
    for k in range(m):
        faces.append(bm.faces.new((ring[k], ring[(k + 1) % m], apex)))
        faces.append(bm.faces.new((ring[(k + 1) % m], ring[k], cen)))
    t = rng.uniform(0.94, 1.08)
    paint(a, faces, mat, t, 0.05)  # one tier, one colour: the sun shades the undersides


def pine(a, x, y, z, s=1.0):
    """Broad pine of 4 wide flared tiers on a short visible trunk, ~7.4 * s tall and
    ~8 * s wide at the lowest tier (all of it above the ground); one canopy green."""
    rng = a.rng
    a.cyl(0.42 * s, 0.3 * s, 2.0 * s, 6, loc=(x, y, z - 0.2), mat="bark")
    for k in range(4):
        r = (4.1, 3.25, 2.4, 1.5)[k] * s  # broad, flared lower tiers (the reference's full pines)
        star_cone(a, x, y, z + (1.7 + 1.15 * k) * s, r, 2.0 * s, pts=8 if k < 2 else 7, inner=0.72,
                  droop=0.28, mat="pine", rot=rng.uniform(0, PI))


def daisy(a, x, y, z, R=0.68):
    """White five-petal flower with a yellow centre, on a short stem."""
    bm = a.bm
    c = Vector((x, y, z + 0.16))
    ph = a.rng.uniform(0, 2 * PI)
    ring = []
    for k in range(10):
        ang = ph + k * PI / 5
        rr = 1.0 if k % 2 == 0 else 0.55
        ring.append(bm.verts.new(c + Vector((math.cos(ang) * R * rr, math.sin(ang) * R * rr, 0.05 * rr))))
    top = bm.verts.new(c + Vector((0, 0, 0.04)))
    faces = [bm.faces.new((top, ring[i], ring[(i + 1) % 10])) for i in range(10)]  # seen from above only
    paint(a, faces, "flower_white", 1.0, 0.03)
    # yellow centre: a low 5-sided pyramid
    cv = [bm.verts.new(c + Vector((math.cos(ph + k * 2 * PI / 5) * R * 0.3,
                                   math.sin(ph + k * 2 * PI / 5) * R * 0.3, 0.05))) for k in range(5)]
    tip = bm.verts.new(c + Vector((0, 0, 0.16)))
    paint(a, [bm.faces.new((cv[k], cv[(k + 1) % 5], tip)) for k in range(5)], "flower_yellow", 1.0, 0.02)


# ---------------------------------------------------------------------------
# The tile
# ---------------------------------------------------------------------------


class Tile:
    """One riverbank tile described in a frame (s along the shore, d inland)."""

    def __init__(self, fk, spec):
        self.fk = fk
        self.spec = spec
        self.F = spec["frame"]
        self.s0, self.s1 = self.F.s0, self.F.s1
        r = random.Random(spec["seed"])
        self.ph = [r.uniform(0, 2 * PI) for _ in range(6)]
        self.path = Path2(spec["path"]) if spec.get("path") else None
        self.notch = spec.get("notch")

    # -- profile in d ------------------------------------------------------------

    def u(self, s):
        return max(0.0, min(1.0, (s - self.s0) / (self.s1 - self.s0)))

    def s_of(self, u):
        return self.s0 + u * (self.s1 - self.s0)

    def fade(self, s):
        return smoothstep(0.0, 2.5, min(s - self.s0, self.s1 - s))

    def bump(self, s):
        """0 on both seams, 1 at the peak; spec 'peak' moves the peak along the shore
        (u = peak), spec 'flat' > 1 flattens the ends so the seams meet square."""
        u = self.u(s)
        p = math.log(0.5) / math.log(self.spec.get("peak", 0.5))
        return math.sin(PI * u ** p) ** self.spec.get("flat", 1.0)

    def shore(self, s):
        return -7.5 + self.spec.get("shore_bulge", 0.0) * self.bump(s)

    def rim_base(self, s):
        return -0.4 + self.spec.get("rim_bulge", 0.0) * self.bump(s)

    def rim(self, s):
        """Grass rim (lumpy lip line), with the hero's path notch."""
        ph = self.ph
        lump = 0.28 * self.fade(s) * (0.6 * math.sin(1.1 * s + ph[0]) + 0.4 * math.sin(2.7 * s + ph[1]))
        d = self.rim_base(s) + lump
        if self.notch:
            na, nb, nd = self.notch
            w = smoothstep(na - 0.3, na, s) * (1 - smoothstep(nb, nb + 0.3, s))
            d = d + (nd - d) * w
        return d

    def foot(self, s):  # where the beach meets the rock foot (sand at its highest)
        return self.rim_base(s) - 3.7

    def sd(self, x, y):
        return self.F.sd(x, y)

    def xy(self, s, d):
        return self.F.xy(s, d)

    def tangent(self, s, fn, h=0.3):
        d = self.xy(s + h, fn(s + h)) - self.xy(s - h, fn(s - h))
        return d.normalized()

    def Hs(self, x, y):
        """Beach height: under water down to 0.55, rising from WZ at the shore to
        SAND_TOP at the rock foot."""
        s, d = self.sd(x, y)
        sh = self.shore(s)
        if d <= sh:
            return max(0.55, WZ - (sh - d) / 1.6 * 0.45)
        t = min(1.0, (d - sh) / max(0.5, self.foot(s) - sh))
        return WZ + (SAND_TOP - WZ) * (t ** 0.85)

    def zone(self, x, y):
        s, d = self.sd(x, y)
        if d < self.shore(s):
            return "water"
        if d < self.rim_base(s) - 3.4:
            return "sand"
        if d < self.rim(s):
            return "rock"
        return "grass"

    def contour(self, fn, step=0.35, s_a=None, s_b=None):
        s_a = self.s0 if s_a is None else s_a
        s_b = self.s1 if s_b is None else s_b
        n = max(2, int(abs(s_b - s_a) / step))
        out = []
        for k in range(n + 1):
            s = s_a + (s_b - s_a) * k / n
            p = self.xy(s, fn(s))
            out.append(Vector((max(-HALF, min(HALF, p.x)), max(-HALF, min(HALF, p.y)))))
        return out

    def region(self, fn, above):
        """Tile square clipped to d >= fn(s) (above) or d <= fn(s)."""
        def g(p):
            s, d = self.sd(p.x, p.y)
            return (d - fn(s)) if above else (fn(s) - d)

        def curve(p0, p1):
            sa, _ = self.sd(p0.x, p0.y)
            sb, _ = self.sd(p1.x, p1.y)
            n = max(1, int(abs(sb - sa) / 0.35))
            return [self.xy(sa + (sb - sa) * k / n, fn(sa + (sb - sa) * k / n)) for k in range(1, n)]
        return square().clip_fn(g, curve)

    def clip2(self, poly, fn, above):
        def g(p):
            s, d = self.sd(p.x, p.y)
            return (d - fn(s)) if above else (fn(s) - d)

        def curve(p0, p1):
            sa, _ = self.sd(p0.x, p0.y)
            sb, _ = self.sd(p1.x, p1.y)
            n = max(1, int(abs(sb - sa) / 0.35))
            return [self.xy(sa + (sb - sa) * k / n, fn(sa + (sb - sa) * k / n)) for k in range(1, n)]
        return poly.clip_fn(g, curve)

    def at(self, u, d):
        return self.xy(self.s_of(u), d)

    def on_grass(self, x, y, m=0.8):
        if abs(x) > HALF - 0.6 or abs(y) > HALF - 0.6:
            return False
        s, d = self.sd(x, y)
        if d < self.rim(s) + m:
            return False
        return not (self.path and self.path.dist(x, y) < 2.9)

    # -- components ------------------------------------------------------------------

    def grass(self, a, part=False):
        """Grass cap with light patches, the lumpy overhanging lip, the soil band
        and the dark rock backing behind the columns."""
        sp = self.spec
        poly = self.region(self.rim, True)
        H = lambda x, y: GZ  # noqa: E731
        cap(a, poly, H, GRASS, spacing=4.2, jz=0.07, seed=sp["seed"] + 1)
        # lumpy lip, soil band and rock backing along the rim
        rim = self.contour(self.rim, 0.8)
        self.lip(a, rim)
        # soil band flaring out under the lip (bulging soil, as the reference shows under each grass cap)
        band(a, [self.offset_out(p, 0.3) for p in rim], GZ - 0.05, GZ - SOIL - 0.15, SOILM, 1.0, 0.06, out_bot=0.4)
        if part:
            # the part is a slab with soil sides on the tile edges too (the path rides on
            # RiverbankRockSlope with its ramp, as the reference Grass Top part shows none)
            self.edge_walls(a, {"grass": [(GZ, GZ - SOIL, SOILM, 1.0)]})
            if self.path:  # the winding path on the grass is part of the grass top
                self.path_flat(a)
        else:
            back = self.contour(lambda s: self.rim(s) + 2.0, 0.9)
            for f in band(a, back, GZ - SOIL + 0.05, WZ, ROCK, 1.0, 0.04):
                m, t = rock_pick(a.rng, 1.0)
                paint(a, [f], m, t, 0.03)

    def offset_out(self, p, dist):
        s, d = self.sd(p.x, p.y)
        q = self.xy(s, d - dist)
        return Vector((max(-HALF, min(HALF, q.x)), max(-HALF, min(HALF, q.y))))

    def lip(self, a, pts):
        """Grass lip overhanging the soil band by ~0.4, darker hanging underside."""
        bm, rng = a.bm, a.rng
        rows = []
        for k, p in enumerate(pts):
            t = pts[min(k + 1, len(pts) - 1)] - pts[max(k - 1, 0)]
            t = t.normalized() if t.length > 1e-9 else Vector((1, 0))
            n = Vector((t.y, -t.x))
            o = 0.3 * rng.uniform(0.8, 1.15)  # a thin lip: the column tops in front stay in the sun
            drop = rng.uniform(0.18, 0.35)
            i_ = p - n * 0.3
            op = p + n * o
            hp = p + n * (o + 0.06)
            rows.append((bm.verts.new((i_.x, i_.y, GZ + 0.03)), bm.verts.new((op.x, op.y, GZ - 0.01)),
                         bm.verts.new((hp.x, hp.y, GZ - drop))))
        tops, hangs = [], []
        for k in range(len(rows) - 1):
            r0, r1 = rows[k], rows[k + 1]
            tops.append(bm.faces.new((r0[0], r0[1], r1[1], r1[0])))
            hangs.append(bm.faces.new((r0[1], r0[2], r1[2], r1[1])))
        for f, h in zip(tops, hangs):  # one strip of lip, one colour, top and hanging edge alike
            m = GRASS
            paint(a, [f, h], m, 1.0, 0.03)

    def sand(self, a, part=False):
        """Beach (one sand; its slope under the water becomes riverbed in submerge),
        pebbles, and the path's ramp down through the rock gap (the flat path on the
        grass rides on the grass top). The SandStrip part is the beach above the
        waterline only, a sand slab with sand sides, plus the ramp."""
        sp = self.spec
        if part:
            poly = self.region(lambda s: self.shore(s) + 0.05, True)
        else:
            poly = self.region(lambda s: self.shore(s) - 1.6, True)
        poly = self.clip2(poly, lambda s: self.rim_base(s) - 1.4, False)
        cap(a, poly, self.Hs, SAND, spacing=2.0, jz=0.02, seed=sp["seed"] + 3, var=0.03)
        a.rng = random.Random(sp["seed"] + 33)  # the part and the hero share the pebbles and ramp
        for u, f, sz in sp.get("pebbles", []):
            s = self.s_of(u)
            d = self.shore(s) + f * (self.foot(s) - self.shore(s))
            p = self.xy(s, d)
            pebble(a, self.fk, p.x, p.y, self.Hs(p.x, p.y) - 0.05, sz)
        if self.path and not part:  # the parts: the path rides on GrassTop, the ramp on RockSlope
            self.path_flat(a)
            self.ramp(a)
        if part:  # a slab of even thickness, its sides the same sand as its top
            band(a, poly.coarse(1.2).p, lambda p: self.Hs(p.x, p.y), lambda p: self.Hs(p.x, p.y) - 0.7,
                 SAND, 1.0, 0.03, closed=True)
        else:
            self.edge_walls(a, {"sand": [(None, 0.0, SAND, 1.0)]})  # the beach sand cut open: same sand as its top

    def path_flat(self, a):
        """Wide sand path on the grass top."""
        sp = self.spec
        ribbon(a, sp["path"], 4.25, lambda x, y: GZ, SAND, lift=0.08, wobble=0.04, seed=sp["seed"] + 6)

    def ramp(self, a):
        """Sand ramp from the path down through the gap in the rock row to the beach."""
        sp = self.spec
        ramp = sp["ramp"]
        R = Path2(ramp)
        end = Vector(ramp[-1])
        z1 = self.Hs(end.x, end.y) + 0.02
        P3 = []
        for k in range(len(ramp)):
            t = R.cum[k] / R.L
            # nearly even grade (soft ends only), so no stretch of the ramp is steeper than it must be
            z = GZ + 0.09 - (GZ + 0.09 - z1) * (0.8 * t + 0.2 * smoothstep(0.0, 1.0, t))
            P3.append((ramp[k][0], ramp[k][1], z))
        rows = ribbon(a, P3, 4.6, None, SAND, lift=0.0, wobble=0.05, step=0.7, seed=sp["seed"] + 7)
        # ramp sides: sand walls down to the beach
        left = [Vector((r[1].co.x, r[1].co.y, r[1].co.z)) for r in rows]
        right = [Vector((r[0].co.x, r[0].co.y, r[0].co.z)) for r in rows]
        bm = a.bm
        for side, flip in ((left, True), (right, False)):  # walls face away from the ramp
            faces = []
            for k in range(len(side) - 1):
                p0, p1 = side[k], side[k + 1]
                zb0 = max(WZ, min(p0.z, self.Hs(p0.x, p0.y) - 0.2))
                zb1 = max(WZ, min(p1.z, self.Hs(p1.x, p1.y) - 0.2))
                vs = [bm.verts.new(p0), bm.verts.new((p0.x, p0.y, zb0)), bm.verts.new((p1.x, p1.y, zb1)),
                      bm.verts.new(p1)]
                if flip:
                    vs.reverse()
                if p0.z - zb0 < 0.05 and p1.z - zb1 < 0.05:
                    continue
                faces.append(bm.faces.new(vs))
            paint(a, faces, SAND, 1.0, 0.03)  # same sand as the ramp top: lighting darkens the sides

    def water(self, a, part=False):
        """ONE flat see-through water slab (z = WZ) over the riverbed (z = BED). No foam,
        ripple or flow geometry: those are water_foam / water_flow VFX sockets."""
        sp = self.spec
        poly = self.region(lambda s: self.shore(s) + 0.45, False)
        cap(a, poly, lambda x, y: WZ, WATER, spacing=4.0, jz=0.0, seed=sp["seed"] + 8, var=0.0)
        cap(a, poly, lambda x, y: BED, RBED, spacing=8.0, jz=0.0, seed=sp["seed"] + 9, var=0.0)
        if part:
            band(a, poly.coarse(1.2).p, WZ, BED, WATER, 1.0, 0.0, closed=True)
            band(a, poly.coarse(1.2).p, BED, 0.0, RBED, 1.0, 0.0, closed=True)
        else:  # the water skirt and the riverbed under it, cut open at the tile edges
            self.edge_walls(a, {"water": [(WZ, BED, WATER, 1.0), (BED, 0.0, RBED, 1.0)]})

    def submerge(self, a):
        """Everything under the water surface is riverbed: cut the sand (beach slope,
        edge walls) and the rock standing in the water at z = WZ and repaint what lies
        below it w03_riverbed (one key, keeping each face's small random Tint)."""
        bm = a.bm
        mats = a.mats
        mi_sand = mats.index(SAND) if SAND in mats else -1
        mi_rock = mats.index(ROCK) if ROCK in mats else -1
        if mi_sand < 0 and mi_rock < 0:
            return
        mi_bed = a._mi(RBED)
        eps = 1e-3

        def wet(f):  # every sand and stone face: below the water surface it is riverbed
            return f.material_index in (mi_sand, mi_rock)
        cross = [f for f in bm.faces if wet(f)
                 and min(v.co.z for v in f.verts) < WZ - eps < WZ + eps < max(v.co.z for v in f.verts)]
        if cross:
            geom = list({e for f in cross for e in f.edges}) + list({v for f in cross for v in f.verts}) + cross
            bmesh.ops.bisect_plane(bm, geom=geom, plane_co=(0, 0, WZ), plane_no=(0, 0, 1), dist=1e-4)
        for f in bm.faces:
            zs = [v.co.z for v in f.verts]
            if max(zs) <= WZ + eps and sum(zs) / len(zs) < WZ - eps and wet(f):
                f.material_index = mi_bed

    def rocks_xy(self):
        """Shore boulder spots (x, y, half-width) in the water / at the waterline."""
        out = []
        r = random.Random(self.spec["seed"] + 20)
        for u, off, sz in self.spec.get("boulders", []):
            s = self.s_of(u)
            p = self.xy(s, self.shore(s) + off)
            sx = sz * (1.0 + r.uniform(0.0, 0.2))
            out.append((p.x, p.y, sz * BSCALE * 0.5, sx))
        return [(x, y, rad * 1.02) for x, y, rad, _ in out]

    def block(self, a, s, dmid, w, dep, top, lean=None, zsink=0.45):
        """One rock column centred at (s, dmid) facing the water, its foot sunk into
        the beach; returns its top z."""
        rng = a.rng
        fn = lambda q: dmid + (self.rim_base(q) - self.rim_base(s))  # noqa: E731
        c = self.xy(s, dmid)
        u = self.tangent(s, fn)
        wr = (self.xy(s + w / 2, fn(s + w / 2)) - self.xy(s - w / 2, fn(s - w / 2))).length * 0.97
        front = self.xy(s, dmid - dep / 2)
        z0 = max(BED, self.Hs(front.x, front.y) - zsink)
        lean = lean or (rng.uniform(-0.12, 0.12), -rng.uniform(0.0, 0.15))
        vs = column(a, self.fk, c, u, wr, dep, top - z0, z0, bulge=0.2, lean=lean)
        return max(v.co.z for v in vs), c

    def rocks(self, a, part=False):
        """The cliff as a broken stack: a back row of tall fat columns under the grass
        lip (some pushed forward and lower), a front row of mid-height blocks, lower
        step blocks on the beach, the front-left grass terrace, shore boulders and
        rubble."""
        sp = self.spec
        fk = self.fk
        rng = a.rng
        s = self.s0 - 1.0
        gap = None
        if self.notch:
            gap = (self.notch[0], self.notch[1] - 0.2)
        tops = sp.get("tops", (GZ - 0.5, GZ + 0.3))
        n = 0
        # back row: a few big fat separate columns (6-7.5 wide) with open creases (~0.8-1.2)
        # between them, standing in front of the grass rim with their big bevelled tops level
        # with the turf (a little proud or a little below, alternately), so the tops catch the sun
        while s < self.s1 + 0.6:
            w = rng.uniform(*sp.get("widths", (6.0, 7.5)))
            if gap and s + w > gap[0] and s < gap[1]:
                if gap[0] - s >= 2.2:
                    w = gap[0] - s
                else:
                    s = gap[1] + 0.3
                    continue
            if self.s1 + 0.6 - (s + w) < 3.0:  # never leave a sliver at the far seam
                w = self.s1 + 1.0 - s
            sc = s + w / 2
            dep = rng.uniform(5.2, 5.8)
            push = rng.uniform(-0.1, 0.5)
            top = rng.uniform(*tops) - (0.4 if n % 2 else 0.0)
            self.block(a, sc, self.rim_base(sc) + 1.5 - dep / 2 - push, w, dep, top)
            n += 1
            s += w + rng.uniform(0.7, 1.0)
        self.n_columns = n
        # front row: fat mid-height blocks in front of the back row
        for u_, w, top, dd in sp.get("front", []):
            q = self.s_of(u_)
            dep = rng.uniform(3.6, 4.2)
            self.block(a, q, self.rim_base(q) - 2.8 - dep / 2 - dd, w, dep, top)  # leaves sand in front
        # lower step blocks on the beach, some carrying a leafy clump
        for u_, w, h, dd, *extra in sp.get("lower", []):
            q = self.s_of(u_)
            dep = rng.uniform(2.4, 3.0)
            dmid = self.rim_base(q) - 5.0 - dd
            front = self.xy(q, dmid - dep / 2)
            zt, c = self.block(a, q, dmid, w, dep, max(BED, self.Hs(front.x, front.y) - 0.4) + h,
                               lean=(rng.uniform(-0.15, 0.15), -0.1), zsink=0.4)
            if extra and extra[0] and not part:
                bush(a, c.x + rng.uniform(-0.4, 0.4), c.y + rng.uniform(-0.3, 0.3), zt - 0.35, 0.6)
        if sp.get("terrace") and not part:
            self.terrace(a)
        r = random.Random(self.spec["seed"] + 20)
        for (u_, off, sz) in sp.get("boulders", []):
            q = self.s_of(u_)
            p = self.xy(q, self.shore(q) + off)
            r.uniform(0.0, 0.2)
            zb = max(BED, self.Hs(p.x, p.y) - 0.35)
            boulder(a, fk, p.x, p.y, zb, sz * BSCALE, tall=rng.uniform(0.95, 1.15) * (1.2 if sz < 1.8 else 1.0))
        if part and self.path:  # the ramp fills the slope's gap (the SandStrip part stays a flat slab)
            self.ramp(a)
        for u_, f, sz in sp.get("rubble", []):  # rubble stones at the cliff foot
            q = self.s_of(u_)
            p = self.xy(q, self.shore(q) + f * (self.foot(q) - self.shore(q)))
            chunk(a, fk, (p.x, p.y, self.Hs(p.x, p.y) + sz * 0.15), (sz * 1.1, sz, sz * 0.75), n=12,
                  floor=self.Hs(p.x, p.y) - 0.1, exp=0.7, facets=6.0)

    def terrace(self, a):
        """Low grass-topped rock terrace at the water's edge (the reference's front-left
        corner), with a small pine and a bush on it."""
        u_, dmid, w, dep, top, pine_s = self.spec["terrace"]
        rng = a.rng
        q = self.s_of(u_)
        zt, c = self.block(a, q, dmid, w, dep, top, lean=(0.0, 0.0))
        bm = a.bm
        n_ = Vector((0, -1)) if isinstance(self.F, LineFrame) else (self.xy(q, dmid - 1) - self.xy(q, dmid)).normalized()
        t_ = Vector((-n_.y, n_.x))
        hw, hd = w / 2 * 0.86, dep / 2 * 0.86
        zg = zt + 0.35
        ring_t, ring_b = [], []
        for k in range(10):
            ang = 2 * PI * (k + 0.5) / 10
            cx, cy = math.cos(ang), math.sin(ang)
            lu = math.copysign(abs(cx) ** 0.6, cx) * hw * rng.uniform(0.95, 1.05)
            lv = math.copysign(abs(cy) ** 0.6, cy) * hd * rng.uniform(0.95, 1.05)
            p = c + t_ * lu + n_ * lv
            ring_t.append(bm.verts.new((p.x, p.y, zg)))
            ring_b.append(bm.verts.new((p.x, p.y, zt - 0.6)))
        top_f = bm.faces.new(ring_t)
        top_f.normal_update()
        if top_f.normal.z < 0:
            top_f.normal_flip()
        paint(a, [top_f], GRASS, 1.0, 0.03)
        sides = []
        for k in range(10):
            j = (k + 1) % 10
            f = bm.faces.new((ring_t[k], ring_b[k], ring_b[j], ring_t[j]))
            f.normal_update()
            if (f.calc_center_median().xy - c).dot(f.normal.xy) < 0:
                f.normal_flip()
            sides.append(f)
        paint(a, sides, SOILM, 1.0, 0.05)
        pine(a, c.x - t_.x * hw * 0.3 + n_.x * 0.2, c.y - t_.y * hw * 0.3 + n_.y * 0.2, zg, pine_s)
        bush(a, c.x + t_.x * hw * 0.45 + n_.x * hd * 0.3, c.y + t_.y * hw * 0.45 + n_.y * hd * 0.3, zg, 0.7)
        tuft(a, c.x + t_.x * hw * 0.1 + n_.x * hd * 0.6, c.y + t_.y * hw * 0.1 + n_.y * hd * 0.6, zg, 1.0)

    def edge_walls(self, a, layers):
        """Flat walls on the tile edges, one stack of layers per zone:
        layers[zone] = [(ztop or None for the beach height, zbot, mat, tint)]."""
        rock_top = self.spec.get("rock_wall", 8.4)
        heights = {"grass": GZ, "rock": rock_top, "water": WZ}
        k_in = (HALF - 0.03) / HALF
        for zone, pts in self.edge_runs():
            if zone not in layers or len(pts) < 2:
                continue
            pts = [p * k_in for p in pts]
            for zt, zb, mat, tint in layers[zone]:
                top = zt if zt is not None else ((lambda p: self.Hs(p.x, p.y)) if zone == "sand"
                                                 else heights[zone])
                band(a, pts, top, zb, mat, tint, 0.05)

    def edge_runs(self):
        """The tile perimeter (counter-clockwise) split into runs by zone."""
        P = []
        corners = [(-HALF, -HALF), (HALF, -HALF), (HALF, HALF), (-HALF, HALF)]
        for k in range(4):
            a0, a1 = Vector(corners[k]), Vector(corners[(k + 1) % 4])
            n = 32
            for i in range(n):
                P.append(a0.lerp(a1, i / n))
        P.append(P[0])
        Z = [self.zone(p.x, p.y) for p in P]
        runs = []
        cur = [P[0]]
        for k in range(1, len(P)):
            if Z[k] != Z[k - 1]:
                lo, hi = P[k - 1], P[k]
                for _ in range(20):
                    m = lo.lerp(hi, 0.5)
                    if self.zone(m.x, m.y) == Z[k - 1]:
                        lo = m
                    else:
                        hi = m
                x = lo.lerp(hi, 0.5)
                cur.append(x)
                runs.append((Z[k - 1], cur))
                cur = [x]
            cur.append(P[k])
        runs.append((Z[-1], cur))
        return runs

    def land_walls(self, a):
        """Land cut faces on the tile edges: the soil band under the grass, and below
        it (and under the cliff zone) a rock face broken into column-like panels
        stepped a little inward, so the cut side reads as stacked rock columns."""
        self.edge_walls(a, {"grass": [(GZ, GZ - SOIL, SOILM, 1.0)]})
        k_in = (HALF - 0.03) / HALF
        for zone, pts in self.edge_runs():
            if zone not in ("grass", "rock") or len(pts) < 2:
                continue
            for edge, sub in split_by_edge(pts):
                if len(sub) < 2:
                    continue
                if edge in ("E", "W"):  # the cut sides the side view looks at: stacked columns
                    self.side_columns(a, zone, sub, 1.0 if edge == "E" else -1.0)
                else:
                    self.panel_run(a, zone, [p * k_in for p in sub])

    def side_columns(self, a, zone, pts, sx):
        """Cut side on x = +/-16 as a row of separate fat 8-sided columns, their outer
        faces 0.2-3.2 studs in from the edge (deep creases between them) and
        their bevelled tops at varied heights under the soil band, in front of a
        recessed backing wall, so the side view reads as stacked blocks."""
        rng, fk, bm = a.rng, self.fk, a.bm
        out = Vector((sx, 0.0))
        inn = -out
        u = Vector((-out.y, out.x))
        P = sorted(pts, key=lambda p: p.y)
        y0, y1 = P[0].y, P[-1].y
        grass = zone == "grass"
        ztop_run = GZ - SOIL if grass else self.spec.get("rock_wall", 8.4)
        # recessed backing wall (seen only in the creases between the columns)
        xb = sx * (HALF - 4.2)
        vs = [bm.verts.new((xb, y0, 0.0)), bm.verts.new((xb, y1, 0.0)),
              bm.verts.new((xb, y1, ztop_run)), bm.verts.new((xb, y0, ztop_run))]
        f = bm.faces.new(vs)
        f.normal_update()
        if f.normal.x * sx < 0:
            f.normal_flip()
        paint(a, [f], ROCK, 1.0, 0.03)
        L = y1 - y0
        y = y0
        k = 0
        while y < y1 - 0.3:
            w = rng.uniform(3.6, 5.0)
            if y1 - (y + w) < 2.5:
                w = y1 - y
            yc = y + w / 2
            c = Vector((sx * HALF, yc))
            ztop = ztop_run - (rng.uniform(0.0, 0.5) if grass else rng.uniform(0.0, 1.2))
            if grass and L > 6 and yc - y0 < 3.0:
                ztop -= rng.uniform(0.6, 1.2)  # the column nearest the water stands a step lower
            e = (0.2, 2.6, 0.7, 3.2, 1.4)[k % 5] + rng.uniform(-0.15, 0.15)  # deep creases between columns
            dep = 3.4
            # plain fat columns only (stacked blocks read as notched 'totem' columns from the front)
            column(a, fk, c + inn * (e + dep / 2), u, w * 0.98, dep, ztop, 0.0, bulge=0.3,
                   lean=(0.0, 0.0), sides=8)
            y += w
            k += 1

    def panel_run(self, a, zone, pts):
        """A land cut face as column-like panels stepped a little inward (the back edge)."""
        rng = a.rng
        bm = a.bm
        if True:
            path = Path2(pts)
            s = 0.0
            prev = None
            while s < path.L - 1e-3:
                w = min(rng.uniform(2.4, 5.0), path.L - s)
                if path.L - s - w < 1.4:
                    w = path.L - s
                p0, p1 = path.at(s), path.at(s + w)
                t = (p1 - p0).normalized() if (p1 - p0).length > 1e-6 else Vector((1, 0))
                inn = Vector((-t.y, t.x))
                grass = zone == "grass"
                ztop = GZ - SOIL if grass else self.spec.get("rock_wall", 8.4) - rng.uniform(0.0, 1.2)
                # 2-3 stacked column chunks per panel, each set further back than the one
                # below, each two big planes meeting at a deep vertical crease, with ledges
                # between them: the cut side reads as a broken stack of rock columns
                nt = 3 if (rng.random() < 0.45 and ztop > 6.5) else 2
                cuts = []
                lo = 1.6
                for k in range(nt - 1):
                    hi = ztop - 1.4 * (nt - 1 - k)
                    z = rng.uniform(lo, max(lo + 0.1, min(hi, lo + 4.5)))
                    cuts.append(z)
                    lo = z + 1.4
                tc = rng.uniform(0.3, 0.7)
                q = p0.lerp(p1, tc)
                tiers = []
                e, deep, za = rng.uniform(0.0, 0.45), 0.0, 0.0
                for k in range(nt):
                    if k:
                        e += rng.uniform(0.5, 1.2)
                    cdep = max(rng.uniform(1.0, 1.8), deep - e + 0.35)
                    deep = e + cdep
                    zb = cuts[k] if k < nt - 1 else ztop
                    tiers.append((e, cdep, za, zb))
                    za = zb
                faces = []
                V = {}
                for ti, (e, cdep, za, zb) in enumerate(tiers):
                    A, B, M = p0 + inn * e, p1 + inn * e, q + inn * (e + cdep)
                    for key, P in (("A", A), ("B", B), ("M", M)):
                        V[(ti, key, 0)] = bm.verts.new((P.x, P.y, za))
                        V[(ti, key, 1)] = bm.verts.new((P.x, P.y, zb))
                    for k1, k2 in (("A", "M"), ("M", "B")):
                        f = bm.faces.new((V[(ti, k1, 1)], V[(ti, k1, 0)], V[(ti, k2, 0)], V[(ti, k2, 1)]))
                        f.normal_update()
                        if f.normal.xy.dot(inn) > 0:
                            f.normal_flip()
                        faces.append(f)
                    if ti:  # ledge onto the tier below (faces up)
                        for k1, k2 in (("A", "M"), ("M", "B")):
                            f = bm.faces.new((V[(ti - 1, k1, 1)], V[(ti - 1, k2, 1)], V[(ti, k2, 0)], V[(ti, k1, 0)]))
                            f.normal_update()
                            if f.normal.z < 0:
                                f.normal_flip()
                            faces.append(f)
                top = len(tiers) - 1
                # cap between the cut plane and the top tier: the underside of the soil
                # overhang under the grass, or the top of the rock in the cliff zone
                O0, O1 = bm.verts.new((p0.x, p0.y, ztop)), bm.verts.new((p1.x, p1.y, ztop))
                try:
                    lg = bm.faces.new((O0, V[(top, "A", 1)], V[(top, "M", 1)], V[(top, "B", 1)], O1))
                    lg.normal_update()
                    if (lg.normal.z > 0) == grass:
                        lg.normal_flip()
                    faces.append(lg)
                except ValueError:
                    pass
                prof = [(zb, e) for e, _, _, zb in tiers]
                # step faces where this panel's profile differs from the last (or from the
                # flat cut plane at the start of the run)
                faces += self.steps(a, prev or ([(ztop, 0.0)], p0), prof, t, inn)
                base = rng.uniform(0.94, 1.05)
                for f in faces:  # each facet its own random pick from the rock mix
                    m, tint = rock_pick(rng, base)
                    paint(a, [f], m, tint, 0.03)
                prev = (prof, p1)
                s += w
            if prev is not None:  # close the run's last panel back to the cut plane
                for f in self.steps(a, prev, [(prev[0][-1][0], 0.0)], t, inn):
                    m, tint = rock_pick(rng, 1.0)
                    paint(a, [f], m, tint, 0.03)

    def steps(self, a, prev, nxt, t, inn):
        """Faces across the cut plane between two neighbouring panel profiles
        ([(tier top z, inset), ...] bottom-up) meeting at prev's end point."""
        bm = a.bm
        pprof, pp = prev

        def depth(prof, z):
            return next((e for zb, e in prof if z < zb), prof[-1][1])
        zt = min(pprof[-1][0], nxt[-1][0])
        cuts = sorted({0.0, zt} | {min(zb, zt) for zb, _ in pprof + nxt})
        out = []
        for zl, zh in zip(cuts, cuts[1:]):
            zc = (zl + zh) / 2
            dp, dn = depth(pprof, zc), depth(nxt, zc)
            if abs(dp - dn) < 0.03 or zh - zl < 0.02:
                continue
            C, D = pp + inn * dp, pp + inn * dn
            f = bm.faces.new((bm.verts.new((C.x, C.y, zh)), bm.verts.new((C.x, C.y, zl)),
                              bm.verts.new((D.x, D.y, zl)), bm.verts.new((D.x, D.y, zh))))
            f.normal_update()
            if (f.normal.xy.dot(t) > 0) != (dn > dp):
                f.normal_flip()
            out.append(f)
        return out

    def trees(self, a):
        for u, d, s in self.spec.get("pines", []):
            p = self.at(u, d)
            dirt_patch(a, p.x, p.y, GZ + 0.07, 2.2 * s, seg=11)  # bare soil round the trunk, as on the reference
            pine(a, p.x, p.y, GZ, s)
        for u, d, r in self.spec.get("dirt", []):  # a few bare earth patches on the turf
            p = self.at(u, d)
            dirt_patch(a, p.x, p.y, GZ + 0.06, r)

    def foot_clumps(self, a):
        """Leafy clumps tucked against the rock foot on the beach."""
        for kind, u, f, s in self.spec.get("foot", []):
            q = self.s_of(u)
            p = self.xy(q, self.shore(q) + f * (self.foot(q) - self.shore(q)))
            (bush if kind == "bush" else fern)(a, p.x, p.y, self.Hs(p.x, p.y) - 0.05, s)

    def dressing(self, a, foot=True):
        """Bushes and ferns along the cliff edge, daisies and tufts on the grass (and,
        on the tiles, the clumps at the rock foot; the parts give those to RockSlope)."""
        sp = self.spec
        rng = a.rng
        spots = []
        for kind, lst in (("bush", sp.get("bushes", [])), ("fern", sp.get("ferns", []))):
            for u, dd, s in lst:
                q = self.s_of(u)
                p = self.xy(q, self.rim(q) + dd)
                if not self.on_grass(p.x, p.y, 0.6):
                    continue
                (bush if kind == "bush" else fern)(a, p.x, p.y, GZ, s * 1.2)
                spots.append((p.x, p.y, 1.3 * s))
        rc = sp.get("rim_clumps")
        if rc:  # a loose row of bushes and ferns along the cliff edge, just behind the column tops
            step, smin, smax = rc
            rr = random.Random(sp["seed"] + 31)
            q = self.s0 + rr.uniform(0.6, 1.4)
            k = 0
            while q < self.s1 - 0.8:
                p = self.xy(q, self.rim(q) + rr.uniform(2.0, 2.8))
                sz = rr.uniform(smin, smax)
                if self.on_grass(p.x, p.y, 0.5) and all((p.x - px) ** 2 + (p.y - py) ** 2 > (0.9 * pr) ** 2
                                                        for px, py, pr in spots):
                    (fern if k % 3 == 2 else bush)(a, p.x, p.y, GZ, sz)
                    spots.append((p.x, p.y, 1.1 * sz))
                k += 1
                q += step * rr.uniform(0.85, 1.15)
        if foot:
            self.foot_clumps(a)
        r = random.Random(sp["seed"] + 30)

        def free(x, y, m):
            return all((x - px) ** 2 + (y - py) ** 2 > (m + pr) ** 2 for px, py, pr in spots)

        trunks = [(self.at(u, d).x, self.at(u, d).y, 1.6 * s) for u, d, s in sp.get("pines", [])]
        spots += trunks
        # interior clumps: ferns and small bushes scattered over the whole turf, not just the rim
        placed = 0
        for _ in range(400):
            if placed >= sp.get("inner_clumps", 0):
                break
            u, dd = r.uniform(0.05, 0.95), r.uniform(3.0, 16.0)
            q = self.s_of(u)
            p = self.xy(q, self.rim(q) + dd)
            if not self.on_grass(p.x, p.y, 1.2) or not free(p.x, p.y, 1.4):
                continue
            if placed % 3 == 2:
                bush(a, p.x, p.y, GZ, rng.uniform(0.7, 0.85))
            else:
                fern(a, p.x, p.y, GZ, rng.uniform(0.8, 0.95))
            spots.append((p.x, p.y, 1.2))
            placed += 1
        placed = 0
        for _ in range(900):
            if placed >= sp.get("daisies", 12):
                break
            u, dd = r.uniform(0.03, 0.97), r.uniform(0.7, 15.0)
            q = self.s_of(u)
            p = self.xy(q, self.rim(q) + dd)
            if not self.on_grass(p.x, p.y, 0.6) or not free(p.x, p.y, 0.35):
                continue
            daisy(a, p.x, p.y, GZ, R=r.uniform(0.95, 1.2))
            spots.append((p.x, p.y, 0.3))
            placed += 1
        placed = 0
        for _ in range(600):
            if placed >= sp.get("tufts", 14):
                break
            u, dd = r.uniform(0.02, 0.98), r.uniform(0.5, 14.0)
            q = self.s_of(u)
            p = self.xy(q, self.rim(q) + dd)
            if not self.on_grass(p.x, p.y, 0.5) or not free(p.x, p.y, 0.3):
                continue
            tuft(a, p.x, p.y, GZ, rng.uniform(0.9, 1.3), 3, dark=placed % 3 != 2)
            spots.append((p.x, p.y, 0.25))
            placed += 1

    def foam_spots(self, spacing=5.5):
        """water_foam line sockets every ~5.5 studs along the waterline (z ~1.05)."""
        shore = Path2(self.contour(self.shore, 0.5))
        n = max(2, int(round(shore.L / spacing)))
        out = []
        for k in range(n):
            p = shore.at(shore.L * (k + 0.5) / n)
            out.append(((round(p.x, 2), round(p.y, 2), WZ + 0.05), 0.6 + 0.2 * (k % 2)))
        return out

    def ring_spots(self):
        """One water_foam ring socket per boulder standing in the water, scale 0.5-0.7."""
        out = []
        for x, y, rad in self.rocks_xy():
            if self.zone(x, y) == "water":
                out.append(((round(x, 2), round(y, 2), WZ + 0.05), round(min(1.0, max(0.5, rad / 2.4)), 2)))
        return out

    def flow_chain(self, n=1, off=-4.5):
        """water_flow beam points lying on the river at z ~1.03, `off` studs out from the
        shore line (d = -12 at the seams), in the flow direction (+s)."""
        pts = []
        for k in range(n + 1):
            s = self.s_of(k / n)
            p = self.xy(s, self.shore(s) + off)
            pts.append((round(max(-HALF, min(HALF, p.x)), 2), round(max(-HALF, min(HALF, p.y)), 2), WZ + 0.03))
        return pts


# ---------------------------------------------------------------------------
# Specs
# ---------------------------------------------------------------------------


def hero_spec():
    return dict(
        # the cliff recedes ~4.8 and the shore ~2.2 over a broad middle (peak u = 0.62, flat 0.6), so
        # the beach is 5-6 studs wide over the right half while the grass plateau stays large
        # (seams keep shore -7.5 / rim -0.4)
        name="RiverbankChunk", frame=LineFrame(), seed=3101, shore_bulge=0.4, rim_bulge=2.4, peak=0.62,
        flat=0.6,
        # an S-shaped path (4.6 wide) from the back-left of the grass top to the back-right ...
        # (kept toward the back, so an open lawn ~8 deep stays between the path and the cliff edge)
        path=[(-8.5, 16.4), (-8.0, 13.8), (-5.6, 11.8), (-2.0, 11.0), (1.4, 12.0), (4.6, 13.6), (7.2, 14.3),
              (8.4, 13.4)],
        # ... dropping down a long, even ramp (4.6 wide) through a gap in the rock row to the beach
        ramp=[(8.4, 13.4), (8.7, 10.4), (9.0, 7.4), (9.3, 4.4), (9.5, 1.6), (9.7, -0.6), (9.8, -1.8)],
        notch=(6.0, 12.4, 13.0),
        # back row: 4 big columns (6-7.5 wide) with their bevelled tops level with the turf
        tops=(GZ - 0.5, GZ + 0.3), widths=(6.0, 7.5),
        # front row (~half height, tops ~4-5 below the back row) on the left half only; the right
        # half keeps an open sand beach
        front=[(0.27, 6.2, 6.0, 0.0), (0.43, 5.4, 5.2, 0.3)],
        # two small low blocks: one between the rows' ends, one at the right foot by the water
        lower=[(0.57, 3.0, 2.2, 0.4, True), (0.97, 3.2, 2.6, -0.4, False)],
        terrace=(0.1, -5.3, 5.4, 4.0, 4.2, 0.62),
        boulders=[(0.17, -0.4, 1.7), (0.33, -2.6, 1.4), (0.5, -4.6, 3.4), (0.64, -1.8, 1.3), (0.78, -4.0, 3.0),
                  (0.9, -1.3, 1.4), (0.97, -4.4, 2.0)],
        pebbles=[(0.42, 0.6, 0.55), (0.55, 0.4, 0.6), (0.6, 0.72, 0.55), (0.72, 0.3, 0.6), (0.76, 0.55, 0.5),
                 (0.87, 0.4, 0.55), (0.9, 0.75, 0.6), (0.95, 0.5, 0.5)],
        rubble=[(0.3, 0.85, 1.2), (0.52, 0.88, 1.1), (0.58, 0.75, 0.8), (0.62, 0.85, 1.3), (0.86, 0.85, 1.1),
                (0.98, 0.9, 1.0), (0.7, 0.6, 0.9)],
        foot=[("bush", 0.38, 0.92, 0.95), ("fern", 0.55, 0.9, 0.95), ("bush", 0.71, 0.9, 0.9),
              ("fern", 0.89, 0.92, 0.95), ("fern", 0.25, 0.8, 0.9), ("bush", 0.61, 0.92, 0.85),
              ("bush", 0.97, 0.85, 0.85)],
        # three big broad pines at the back-left (6-7 tall, 4 wide tiers)
        # (set back from the rim so the lawn in front of them stays open)
        pines=[(0.12, 10.5, 0.95), (0.27, 8.2, 0.82), (0.04, 5.2, 0.72)],
        # a loose row of clumps on the edge only, leaving an open lawn with a daisy scatter
        rim_clumps=(4.6, 0.85, 1.1),
        dirt=[(0.05, 14.5, 1.4), (0.42, 13.5, 1.3), (0.9, 14.0, 1.4)],
        bushes=[(0.97, 8.0, 0.9)],
        ferns=[(0.45, 5.0, 0.9)],
        inner_clumps=4, daisies=44, tufts=10,
    )


def straight_spec():
    return dict(
        name="RiverbankStraight", frame=LineFrame(), seed=3201, shore_bulge=0.0,
        front=[(0.22, 5.0, 5.8, 0.2), (0.62, 5.4, 6.4, 0.3)],
        lower=[(0.4, 3.4, 2.6, 0.5, True), (0.9, 3.2, 2.4, 0.3, False)],
        boulders=[(0.14, -0.6, 1.9), (0.38, -2.6, 1.5), (0.56, -3.4, 2.4), (0.8, -1.0, 1.7)],
        pebbles=[(0.25, 0.5, 0.6), (0.66, 0.6, 0.55)],
        rubble=[(0.45, 0.85, 0.8), (0.7, 0.9, 0.9)],
        foot=[("bush", 0.5, 0.9, 0.85), ("fern", 0.18, 0.88, 0.9), ("fern", 0.74, 0.88, 0.85)],
        pines=[(0.12, 10.5, 0.9), (0.26, 13.0, 0.84), (0.85, 12.0, 0.8)],
        rim_clumps=(4.4, 0.85, 1.1),
        inner_clumps=3, daisies=34, tufts=8,
    )


def inner_spec():
    return dict(
        # concave bay: the cliff, beach and shore curve ~10 studs inland in the middle round the
        # water; seams at x = +/-16 match the hero
        name="RiverbankInnerBend", frame=LineFrame(), seed=3301, shore_bulge=10.0, rim_bulge=10.0, flat=0.85,
        front=[(0.3, 5.0, 6.0, 0.3), (0.62, 5.0, 6.4, 0.3)],
        lower=[(0.12, 3.0, 2.6, 0.4, True), (0.86, 3.0, 2.4, 0.4, False)],
        boulders=[(0.16, -0.5, 1.6), (0.36, -2.4, 1.6), (0.5, -4.2, 2.4), (0.66, -0.4, 1.5), (0.84, -1.2, 1.9)],
        pebbles=[(0.3, 0.5, 0.55), (0.55, 0.6, 0.6), (0.8, 0.5, 0.5)],
        rubble=[(0.4, 0.85, 0.8), (0.6, 0.9, 0.7)],
        foot=[("bush", 0.42, 0.9, 0.85), ("fern", 0.7, 0.88, 0.9), ("fern", 0.2, 0.88, 0.85)],
        pines=[(0.15, 11.5, 0.9), (0.5, 14.0, 0.92), (0.86, 12.0, 0.84)],
        rim_clumps=(4.4, 0.85, 1.1),
        inner_clumps=3, daisies=32, tufts=8,
    )


def outer_spec():
    return dict(
        # convex corner: land fills the back corner (+X,+Y) and its cliff swells ~4.5 studs out round
        # a rounded point facing the front corner; water wraps both front edges (-X and -Y)
        name="RiverbankOuterBend", frame=outer_frame(), seed=3401, shore_bulge=-3.5, rim_bulge=-4.5,
        front=[(0.35, 5.0, 6.2, 0.3), (0.62, 5.0, 6.6, 0.2)],
        lower=[(0.2, 3.2, 2.6, 0.4, True), (0.8, 3.2, 2.4, 0.4, False)],
        boulders=[(0.12, -0.8, 1.7), (0.33, -3.0, 2.4), (0.5, -1.0, 1.5), (0.68, -3.2, 2.6), (0.9, -0.6, 1.8)],
        pebbles=[(0.2, 0.5, 0.6), (0.45, 0.55, 0.55), (0.82, 0.5, 0.6)],
        rubble=[(0.4, 0.85, 0.8), (0.6, 0.88, 0.7)],
        foot=[("fern", 0.32, 0.9, 0.9), ("bush", 0.62, 0.9, 0.85), ("bush", 0.1, 0.9, 0.8)],
        pines=[(0.62, 12.0, 0.92), (0.2, 8.5, 0.84), (0.85, 9.5, 0.84)],
        rim_clumps=(4.4, 0.85, 1.1),
        inner_clumps=3, daisies=32, tufts=8,
    )


# ---------------------------------------------------------------------------
# Assembly
# ---------------------------------------------------------------------------


def new_asset(fk, name, seed):
    a = fk.Asset(name, "Terrain", seed=seed)
    a.fk_ref = fk
    return a


def run(a, seed, fn, *args, **kw):
    """Each component gets its own RNG, so a part matches its piece of the hero."""
    a.rng = random.Random(seed)
    return fn(a, *args, **kw)


def finish(a, kit, role, collision, budget, notes, clamp=True):
    """Clamp to the 32 x 32 footprint, nothing below z=0; returns (obj, offset)."""
    xs, ys, zs = [], [], []
    for v in a.bm.verts:
        if clamp:
            v.co.x = min(max(v.co.x, -HALF), HALF)
            v.co.y = min(max(v.co.y, -HALF), HALF)
        v.co.z = max(v.co.z, 0.0)
        xs.append(v.co.x)
        ys.append(v.co.y)
        zs.append(v.co.z)
    off = Vector(((min(xs) + max(xs)) / 2, (min(ys) + max(ys)) / 2, min(zs)))
    obj = a.finish()
    kit.tag(obj, role, collision=collision, budget=budget, notes=notes)
    if role == "part":  # where this part's origin sits in the hero, so the parts re-assemble
        obj["w03_hero_offset"] = [round(off.x, 3), round(off.y, 3), round(off.z, 3)]
    own = per_key_shading(obj)
    obj["w03_per_key_shading"] = round(own, 2)
    for fam, corr, area in family_shading(obj):  # build log only: which material family drives the score
        print(f"RBDBG {obj.name} family={fam} corr={corr:.2f} area={area:.0f}")
    pairs = colour_pairs(obj)
    known = [pr for pr in pairs if frozenset(pr) in TWO_TONE]
    unknown = [pr for pr in pairs if frozenset(pr) not in TWO_TONE]
    if known:  # only real material changes, each named
        obj["kit_two_tone_ok"] = "; ".join(TWO_TONE[frozenset(pr)] for pr in known)
    if unknown:
        print(f"RBDBG {obj.name} unexplained colour pairs {unknown}")
    return obj, off


# Colour pairs the runner reads as "one material in two shades" that are in fact
# different materials (same broad hue, similar brightness). Each is named.
TWO_TONE = {
    frozenset(("w03_riverbed", "w03_water")): "w03_riverbed is the river bed under the water, w03_water the "
                                              "see-through water surface",
    frozenset(("w03_rock", "flower_white")): "w03_rock is the cliff stone, flower_white the daisy petals",
    frozenset(("w03_grass", "flower_yellow")): "w03_grass is the turf, flower_yellow the daisy centres",
    frozenset(("w03_grass", "w03_bush")): "w03_grass is the turf, w03_bush the bush and fern leaves",
    frozenset(("w03_bush", "pine")): "w03_bush is the bush and fern leaves, pine the pine needles",
    frozenset(("bark", "w03_sand")): "bark is the pine trunks, w03_sand the beach and path sand",
    frozenset(("bark", "w03_soil")): "bark is the pine trunks, w03_soil the soil band under the grass",
    frozenset(("bark", "flower_yellow")): "bark is the pine trunks, flower_yellow the daisy centres",
}


def colour_pairs(obj):
    """The runner's same-hue colour pairs (shade_pairs), as key tuples."""
    import colorsys
    keys = []
    for m in obj.data.materials:
        if m is None or m.get("flintkit_key") == "foam" or (m.get("flintkit_spec") or [0, 0, 0])[2] > 0:
            continue
        h = m.get("flintkit_hex", "#808080").lstrip("#")
        keys.append((m.get("flintkit_key"), colorsys.rgb_to_hsv(*(int(h[i:i + 2], 16) / 255 for i in (0, 2, 4)))))
    out = []
    for i in range(len(keys)):
        for j in range(i + 1, len(keys)):
            (ka, (ha, sa, va)), (kb, (hb, sb, vb)) = keys[i], keys[j]
            dh = min(abs(ha - hb), 1 - abs(ha - hb)) * 360
            same = (sa < 0.2 and sb < 0.2) or (sa >= 0.2 and sb >= 0.2 and dh < 28 and abs(sa - sb) < 0.35)
            if same and min(va, vb) / max(va, vb, 1e-4) >= 0.5:
                out.append((ka, kb))
    return out


def family_shading(obj):
    """Per-family brightness vs face-direction correlation, mirroring the runner's
    check (same family grouping), for the build log."""
    import colorsys
    me = obj.data
    tint = me.color_attributes.get("Tint")
    keys = [m.get("flintkit_key", "?") if m else "?" for m in me.materials]
    hexes = [m.get("flintkit_hex", "#808080") if m else "#808080" for m in me.materials]
    hsv = [colorsys.rgb_to_hsv(*(int(h.lstrip("#")[i:i + 2], 16) / 255 for i in (0, 2, 4))) for h in hexes]

    def same(a_, b_):
        (h1, s1, _), (h2, s2, _) = a_, b_
        if s1 < 0.18 and s2 < 0.18:
            return True
        dh = min(abs(h1 - h2), 1 - abs(h1 - h2)) * 360
        return dh < 22 and abs(s1 - s2) < 0.3
    fam = []
    for i, c in enumerate(hsv):
        fam.append(next((fam[j] for j in range(i) if same(hsv[j], c)), i))
    key = Vector((-0.45, -0.55, 0.7)).normalized()
    groups = {}
    for p in me.polygons:
        mi = min(p.material_index, len(keys) - 1)
        if keys[mi] == "foam":
            continue
        t = sum(tint.data[li].color[0] for li in p.loop_indices) / len(p.loop_indices) if tint else 1.0
        groups.setdefault(fam[mi], []).append((p.area, hsv[mi][2] * t, p.normal.z, p.normal.dot(key), mi))
    total = sum(p.area for p in me.polygons) or 1.0
    out = []
    for f, rows in groups.items():
        area = sum(r[0] for r in rows)
        if len(rows) < 12 or area < 0.1 * total:
            continue
        w = np.array([r[0] for r in rows])
        b = np.array([r[1] for r in rows])
        mb = np.average(b, weights=w)
        sb = math.sqrt(np.average((b - mb) ** 2, weights=w))
        if sb / max(mb, 1e-4) < 0.06:
            continue
        worst = 0.0
        for col in (2, 3):
            x = np.array([r[col] for r in rows])
            mx = np.average(x, weights=w)
            sx = math.sqrt(np.average((x - mx) ** 2, weights=w))
            if sx > 1e-4:
                worst = max(worst, float(np.average((b - mb) * (x - mx), weights=w) / (sb * sx)))
        names = " ".join(f"{keys[i]}:{sum(r[0] for r in rows if r[4] == i):.0f}a/"
                         f"{np.mean([r[2] for r in rows if r[4] == i] or [0]):.2f}z"
                         for i in sorted({r[4] for r in rows}))
        out.append((names, worst, area))
    return out


def per_key_shading(obj):
    """Worst correlation, within ONE palette key, between a face's Tint and how much
    it faces up or toward a typical sun (front-left, above)."""
    me = obj.data
    tint = me.color_attributes.get("Tint")
    if tint is None:
        return 0.0
    key = Vector((-0.45, -0.55, 0.7)).normalized()
    per = {}
    for p in me.polygons:
        t = sum(tint.data[li].color[0] for li in p.loop_indices) / len(p.loop_indices)
        per.setdefault(p.material_index, []).append((p.area, t, p.normal.z, p.normal.dot(key)))
    worst = 0.0
    for rows in per.values():
        if len(rows) < 30:
            continue
        w = np.array([r[0] for r in rows]) + 1e-9
        b = np.array([r[1] for r in rows])
        mb = np.average(b, weights=w)
        sb = math.sqrt(np.average((b - mb) ** 2, weights=w))
        for col in (2, 3):
            x = np.array([r[col] for r in rows])
            mx = np.average(x, weights=w)
            sx = math.sqrt(np.average((x - mx) ** 2, weights=w))
            if sb < 1e-5 or sx < 1e-5:
                continue
            worst = max(worst, float(np.average((b - mb) * (x - mx), weights=w) / (sb * sx)))
    return worst


WATER_VFX_NOTE = ("Water is VFX, not mesh: water_foam sockets every ~5.5 studs along the waterline (z 1.05, scale 0.6-0.8) "
                   "are the shore foam line, one water_foam ring socket (scaled by boulder size, 0.5-1.0) sits at each boulder "
                   "standing in the river, and 3 chained water_flow beams (width ~6) lying on the river at z 1.03 carry the subtle "
                   "flow streaks{flow}. The flat w03_water slab (z 1.0) is see-through over the w03_riverbed "
                   "bed (z 0.2); everything under the water surface is w03_riverbed.")


def add_water_vfx(kit, obj, t, off, name, flow_n=3):
    """Shore foam line, boulder foam rings and the river's flow beam(s)."""
    def L(p):
        return (p[0] - off.x, p[1] - off.y, p[2] - off.z)
    for k, (p, sc) in enumerate(t.foam_spots()):
        kit.vfx.add(obj, "water_foam", L(p), scale=sc, name=f"VFX_{name}_foam_{k + 1}")
    for k, (p, sc) in enumerate(t.ring_spots()):
        kit.vfx.add(obj, "water_foam", L(p), scale=sc, name=f"VFX_{name}_ring_{k + 1}")
    chain = t.flow_chain(flow_n)
    for k in range(len(chain) - 1):
        kit.vfx.add(obj, "water_flow", L(chain[k]), end=L(chain[k + 1]), width=6.0,
                    name=f"VFX_{name}_flow_{k + 1}")


def build_tile(kit, spec, role, budget, notes, flow_n=3):
    fk = kit.flintkit
    t = Tile(fk, spec)
    a = new_asset(fk, spec["name"], spec["seed"])
    sd = spec["seed"]
    run(a, sd + 100, t.water)
    run(a, sd + 200, t.sand)
    run(a, sd + 300, t.rocks)
    run(a, sd + 400, t.grass)
    run(a, sd + 500, t.land_walls)
    run(a, sd + 600, t.dressing)
    run(a, sd + 700, t.trees)
    t.submerge(a)
    flow = f" (-X -> +X, {flow_n} beams chained along the shore ~4.5 studs out)"
    obj, off = finish(a, kit, role, "precise", budget, notes + " " + WATER_VFX_NOTE.format(flow=flow))
    add_water_vfx(kit, obj, t, off, spec["name"], flow_n)
    return obj, t


def build_parts(kit):
    fk = kit.flintkit
    spec = hero_spec()
    sd = spec["seed"]
    t = Tile(fk, spec)
    out = []

    a = new_asset(fk, "RiverbankGrassTop", sd)
    run(a, sd + 400, t.grass, part=True)
    run(a, sd + 600, t.dressing, foot=False)
    run(a, sd + 700, t.trees)
    obj, _ = finish(a, kit, "part", "precise", 3000,
                    "Grass Top: grass slab (z 10.4) with soil sides and a lumpy overhanging lip, the winding "
                    "sand path (>= 4 wide), three small pines, bushes, ferns, daisies and leafy sprigs; sits on "
                    "RiverbankRockSlope")
    # the runner groups w03_sand with w03_soil (same hue family): on this slab the up-facing faces of
    # that family are the sand path and the side faces are the soil band, two different materials.
    # Within each key the Tint is small and random (per-key correlation is logged as w03_per_key_shading).
    obj["kit_shading_ok"] = ("w03_sand path on the slab top vs the w03_soil band on its sides: two "
                             "materials of one hue family, each a single flat colour")
    out.append(obj)

    a = new_asset(fk, "RiverbankSandStrip", sd)
    run(a, sd + 200, t.sand, part=True)
    obj, _ = finish(a, kit, "part", "precise", 1500,
                    "Dirt / Sand Strip: the beach above the waterline as a flat w03_sand slab (top z 1.0-1.8, "
                    "sand sides 0.7 thick, pebbles); all sand (the slope under the water belongs to the riverbed). "
                    "The path's 4.6-wide sand ramp is carried by RiverbankRockSlope, in its gap, so this strip "
                    "stays a flat slab like the sheet's part")
    out.append(obj)

    a = new_asset(fk, "RiverbankRockSlope", sd)
    run(a, sd + 300, t.rocks, part=True)
    run(a, sd + 650, t.foot_clumps)
    t.submerge(a)
    obj, _ = finish(a, kit, "part", "precise", 4000,
                    "Rock Slope: the stacked cliff columns (bevelled tops), front and lower step blocks, rubble, "
                    "the leafy clumps at the rock foot, "
                    "the loose shore boulders standing in the river (w03_riverbed below the waterline; their foam "
                    "rings are water_foam sockets on RiverbankWaterPlane), and the path's walkable 4.6-wide sand "
                    "ramp down through the gap in the row")
    out.append(obj)

    a = new_asset(fk, "RiverbankWaterPlane", sd)
    run(a, sd + 100, t.water, part=True)
    obj, off = finish(a, kit, "part", "none", 1500,
                      "Water Plane (+ Foam): one flat see-through w03_water slab (z 1.0) over its w03_riverbed bed "
                      "(z 0.2). The '+ Foam' is VFX, not mesh: water_foam sockets along its shore edge (the foam "
                      "line) and at each boulder (the foam rings), plus 3 chained water_flow beams (-X -> +X, width 6, z 1.03) "
                      "for the flow streaks.")
    add_water_vfx(kit, obj, t, off, "RiverbankWaterPlane", 3)
    out.append(obj)
    return out


def build(kit):
    objs = []
    hero, _ = build_tile(
        kit, hero_spec(), "hero", 8000,
        "32x32 riverbank tile, water level z=1.0, bed z=0.2 (shared by W03), grass top z=10.4; walkable grass, "
        "path, ramp and beach (precise).")
    objs.append(hero)
    objs += build_parts(kit)
    for spec, n, cap_ in ((straight_spec(), 3, "Straight Section"),
                          (inner_spec(), 3, "Inner Bend (Concave)"),
                          (outer_spec(), 3, "Outer Bend (Convex)")):
        obj, _ = build_tile(kit, spec, "variant", 8000,
                            f"{cap_}: same seam profile as RiverbankChunk (shore at d=-7.5, grass rim at d=-0.4, "
                            f"water z 1.0, bed z 0.2, grass z 10.4 on every seam edge).", flow_n=n)
        objs.append(obj)
    return objs
