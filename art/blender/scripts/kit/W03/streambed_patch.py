"""W03 row 4: STREAMBED (PATCH), a modular 32 x 32 shallow-stream terrain tile.

Hero "StreambedPatch" (32 x 32 x ~4.5): a shallow, gently meandering stream runs
front (-Y) to back (+Y). Broad warm w03_sand banks (z=1.6, slightly lumpy)
slope down to the waterline at z=1.0. Below the waterline everything is
w03_riverbed (#0B6E8F): the bed at z=0.2, the underwater bank slope, the low
bed stones and the underwater bases of rocks, so the see-through water reads a
deep saturated cyan. The water is ONE flat w03_water slab at z=1.0. Clusters of big chunky flat-topped w03_rock
boulders straddle both waterlines, low flat rocks break the surface inside the
channel, and pebbles, a few grass tufts and daisies dress the banks.

WATER IS VFX: no foam, ripple or streak geometry. Flow streaks are water_flow
beam sockets VFX_StreambedFlowStrips_N lying on the water (z 1.03) along the
centreline, chained upstream -> downstream (downstream = -Y; the bend flows
right edge -> front, the fork from the left and right edges into the front).
Foam is water_foam sockets: one at every rock that breaks the surface or
straddles a waterline, a short riffle downstream of each in-stream rock, and
one every ~8 studs along each waterline.

Parts (in hero positions): StreambedBankRocks, StreambedBedSlab,
StreambedSubmergedRocks, StreambedWaterPlane (the reference's "Flow Strips"
are the water_flow sockets, not a mesh).
Variants: StreambedStraight, StreambedBend (quarter circle, front -> right),
StreambedFork (front -> left + right, with an islet in the split).

Technique: every tile is a "channel field". Each channel is a centreline path
(x, y, half-width) that runs past the tile edges, so its seams are exactly
perpendicular; g(x, y) = distance to the centreline minus the half-width (the
riverbank_chunk frame idea: along-stream s, across-stream d), and the field G
is the minimum over the channels, raised by islets (sandbar, fork islet). The
cross-section is a function of G only, so straight, meander, bend and fork all
share it: bank 1.6 (G >= 1.6), sand top edge at G=0.9 (z 1.45), waterline at
G=0 (z 1.0), bed 0.2 from G <= -2. Ground and water are Delaunay surfaces whose
constraint edges are the G-contours (offset curves of the paths, kept where
they lie on the true contour), so material bands are crisp and every seam is
the same 12-wide channel (x -6..6 at the waterline) that chains with the
WaterfallModule pool mouth. Tile edges are flat w03_sand walls to z=0 on the
banks; across the channel a w03_water skirt runs from the surface down to the
ground and a w03_riverbed wall from there to z=0.

Colour: ONE key per material (w03_sand, w03_riverbed, w03_rock, w03_water,
w03_grass, the flowers) with a small random Tint; all light and dark is the
lighting. Rock hulls that cross the waterline are cut at z=1.0 so the part
under the water is w03_riverbed and the part above it w03_rock (a real
material change: wet, underwater stone). The water keeps the sheet's default
transparency (no per-module override, so all W03 tiles agree).
"""

import bisect
import math
import random

import bmesh
import numpy as np
from mathutils import Vector
from mathutils.geometry import delaunay_2d_cdt

SUBJECT = "StreambedPatch"
ROW = 4
HERO_AZIMUTH = 22  # the sheet draws the hero from the front-right: the channel exits the long front face
# The W03 sheet palette, identical in all four W03 modules. Existing flintkit
# keys used as they are: flower_white, flower_yellow (pine and bark belong to
# the sheet but are not used on this tile).
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
TAU = 2 * PI
HALF = 16.0
WZ, BED, BANK = 1.0, 0.2, 1.6
SAND = "w03_sand"      # banks and shore above the waterline, bank-side tile walls
RIVERBED = "w03_riverbed"  # everything under the water: bed, wet slope, bed stones, rock bases, channel walls
WATER = "w03_water"    # the ONE flat water slab and its seam skirts
ROCK = "w03_rock"      # every stone above the water: boulders, slab tops, pebbles
GRASS = "w03_grass"
FLOW_Z = WZ + 0.03     # water_flow beams lie just on the water
FOAM_Z = WZ + 0.05     # water_foam sockets

# cross-section levels of the field G (distance outside the waterline)
K_BED = -2.0    # the shore slope reaches the bed
K_WET = 0.55    # wet sand below, dry bank sand above (z 1.3)
WET_RISE = 0.3  # height of the wet-sand shore above the water
K_TOP = 1.6     # bank plateau
K_WOUT = 0.15   # water outline, buried just under the shore slope
GROUND_LEVELS = (K_BED, 0.0, K_WET)
WATER_LEVELS = (K_WOUT,)


# ---------------------------------------------------------------------------
# low-level helpers
# ---------------------------------------------------------------------------


def paint(a, faces, mat, tint=1.0, var=0.04):
    mi = a._mi(mat)
    for f in faces:
        f.material_index = mi
        f.smooth = False
        t = tint * (1.0 + a.rng.uniform(-var, var)) if var else tint
        for lp in f.loops:
            lp[a.tint_layer] = (t, t, t, 1.0)


def face(a, vs, mat, tint=1.0, var=0.03, out=None):
    """New face from verts; flipped so its normal points along `out` (3D)."""
    try:
        f = a.bm.faces.new(vs)
    except ValueError:
        return None
    f.normal_update()
    if out is not None and f.normal.dot(Vector(out)) < 0:
        f.normal_flip()
    paint(a, [f], mat, tint, var)
    return f


def smoothstep(e0, e1, x):
    t = max(0.0, min(1.0, (x - e0) / (e1 - e0)))
    return t * t * (3 - 2 * t)


def catmull(p0, p1, p2, p3, t):
    t2, t3 = t * t, t * t * t
    return 0.5 * ((2 * p1) + (-p0 + p2) * t + (2 * p0 - 5 * p1 + 4 * p2 - p3) * t2
                  + (-p0 + 3 * p1 - 3 * p2 + p3) * t3)


def smooth_path(pts, step=0.5):
    """Catmull-Rom through 3D control points (x, y, half-width)."""
    P = [Vector(p) for p in pts]
    out = []
    for k in range(len(P) - 1):
        p0, p1, p2, p3 = P[max(k - 1, 0)], P[k], P[k + 1], P[min(k + 2, len(P) - 1)]
        n = max(1, int((p2 - p1).length / step))
        for s in range(n):
            out.append(catmull(p0, p1, p2, p3, s / n))
    out.append(P[-1])
    return [(p.x, p.y, p.z) for p in out]


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
        self.a = np.array([(v.x, v.y) for v in P])
        self.b = np.roll(self.a, -1, axis=0)

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

    def resample(self, step):
        P = self.p + [self.p[0]]
        out = []
        for k in range(len(P) - 1):
            d = P[k + 1] - P[k]
            n = max(1, int(round(d.length / step)))
            for s in range(n):
                out.append(P[k] + d * (s / n))
        return out


class Path2:
    """Arc-length parametrised open polyline (for dashes)."""

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


# ---------------------------------------------------------------------------
# the channel field
# ---------------------------------------------------------------------------


class Path:
    """Channel centreline: dense (x, y, half-width) points running past the tile.
    flow = +1 when the water runs toward increasing s."""

    def __init__(self, pts, flow=1):
        P = np.array(pts, float)
        self.xy = P[:, :2]
        self.hw = P[:, 2]
        self.a = self.xy[:-1]
        self.d = self.xy[1:] - self.xy[:-1]
        self.len2 = (self.d ** 2).sum(1) + 1e-12
        self.cum = np.concatenate([[0.0], np.cumsum(np.sqrt(self.len2))])
        self.L = float(self.cum[-1])
        self.flow = flow
        inside = [k for k in range(len(self.xy)) if max(abs(self.xy[k][0]), abs(self.xy[k][1])) <= HALF]
        self.s0, self.s1 = float(self.cum[inside[0]]), float(self.cum[inside[-1]])

    def g(self, x, y):
        p = np.array((x, y))
        t = np.clip(((p - self.a) * self.d).sum(1) / self.len2, 0, 1)
        q = self.a + self.d * t[:, None]
        dd = ((q - p) ** 2).sum(1)
        k = int(np.argmin(dd))
        hw = self.hw[k] + t[k] * (self.hw[k + 1] - self.hw[k])
        return math.sqrt(dd[k]) - hw

    def at(self, s):
        """(centre, unit tangent, half-width) at arc length s."""
        def pt(s):
            s = max(0.0, min(self.L, s))
            k = max(0, min(len(self.xy) - 2, int(np.searchsorted(self.cum, s, side="right")) - 1))
            seg = self.cum[k + 1] - self.cum[k]
            t = (s - self.cum[k]) / seg if seg > 1e-9 else 0.0
            xy = self.xy[k] + (self.xy[k + 1] - self.xy[k]) * t
            return Vector((xy[0], xy[1])), self.hw[k] + (self.hw[k + 1] - self.hw[k]) * t
        c, hw = pt(s)
        tt = pt(s + 0.6)[0] - pt(s - 0.6)[0]
        return c, tt.normalized(), float(hw)

    def tile_s(self, u):
        return self.s0 + u * (self.s1 - self.s0)

    def frame(self, u, d):
        """Point at tile fraction u along the path, d half-widths across (+ = right
        of travel). Returns (pos, tangent, right normal, hw)."""
        c, t, hw = self.at(self.tile_s(u))
        n = Vector((t.y, -t.x))
        return c + n * d * hw, t, n, hw


class Islet:
    """Land shape raised out of the channel (fork islet, inner-bend sandbar)."""

    def __init__(self, pts, top):
        self.poly = Poly(pts)
        self.top = top

    def sdf(self, x, y):
        return self.poly.sdist(x, y)


def prof(g, top):
    """Ground height across the stream for field value g on a plateau `top`."""
    if g >= 0:
        a = min(WET_RISE, top - WZ)
        if g < K_WET:
            return WZ + a * g / K_WET
        return WZ + a + (top - WZ - a) * min(1.0, (g - K_WET) / (K_TOP - K_WET))
    if g > K_BED:
        return WZ - (WZ - BED) * (-g / -K_BED) ** 0.85
    return BED


def inside_sq(p):
    return abs(p[0]) <= HALF and abs(p[1]) <= HALF


def edge_cross(q, p):
    """Point where segment q (inside) -> p (outside) leaves the tile square."""
    lo, hi = 0.0, 1.0
    for _ in range(30):
        m = (lo + hi) / 2
        r = q.lerp(p, m)
        if inside_sq(r):
            lo = m
        else:
            hi = m
    r = q.lerp(p, (lo + hi) / 2)
    if abs(r.x) >= abs(r.y):
        r.x = math.copysign(HALF, r.x)
        r.y = max(-HALF, min(HALF, r.y))
    else:
        r.y = math.copysign(HALF, r.y)
        r.x = max(-HALF, min(HALF, r.x))
    return r


def clip_square(run):
    res, cur = [], []
    for i, p in enumerate(run):
        ins = inside_sq(p)
        if i > 0:
            q = run[i - 1]
            qin = inside_sq(q)
            if ins and not qin:
                cur = [edge_cross(p, q)]
            elif qin and not ins:
                cur.append(edge_cross(q, p))
                if len(cur) > 1:
                    res.append(cur)
                cur = []
        if ins:
            cur.append(p)
    if len(cur) > 1:
        res.append(cur)
    return res


class Field:
    def __init__(self, paths, islets=(), seed=0):
        self.paths = paths
        self.islets = list(islets)
        r = random.Random(seed)
        self.ph = [r.uniform(0, TAU) for _ in range(6)]

    def gch(self, x, y):
        return min(p.g(x, y) for p in self.paths)

    def G(self, x, y):
        g = self.gch(x, y)
        for i in self.islets:
            g = max(g, i.sdf(x, y))
        return g

    def lump(self, x, y, g):
        ph = self.ph
        e = min(HALF - abs(x), HALF - abs(y))
        n = 0.6 * math.sin(0.62 * x + ph[0]) * math.sin(0.55 * y + ph[1]) + 0.45 * math.sin(1.2 * x - 0.9 * y + ph[2])
        return 0.2 * max(0.0, n) * smoothstep(0.4, 3.0, e) * smoothstep(K_TOP, K_TOP + 1.6, g)

    def H(self, x, y):
        g = self.gch(x, y)
        z = prof(g, BANK + self.lump(x, y, g))
        for i in self.islets:
            s = i.sdf(x, y)
            if s > K_BED - 1.0:
                z = max(z, prof(s, i.top))
        return z

    def stone(self, x, y):
        ph = self.ph
        n = math.sin(0.85 * x + ph[3]) * math.sin(0.75 * y + ph[4]) + 0.45 * math.sin(1.6 * x + 1.3 * y + ph[5])
        return n > 0.62

    def runs(self, k, step=0.9, tol=0.12):
        """Contour G = k as polylines clipped to the tile: offset curves of every
        path (both sides) and islet outline, kept where they lie on the true
        contour; near-duplicates (shared path stretches) are dropped."""
        out = []
        acc = np.zeros((0, 2))
        cands = []
        for P in self.paths:
            n = max(2, int(P.L / step))
            for side in (-1, 1):
                seq = []
                for i in range(n + 1):
                    c, t, hw = P.at(P.L * i / n)
                    nr = Vector((t.y, -t.x))
                    seq.append(c + nr * side * (hw + k))
                cands.append((seq, False))
        for isl in self.islets:
            pts = isl.poly.resample(step * 0.8)
            m = len(pts)
            seq = []
            for i in range(m):
                t = (pts[(i + 1) % m] - pts[i - 1]).normalized()
                nout = Vector((t.y, -t.x))
                seq.append(pts[i] - nout * k)
            cands.append((seq, True))
        for seq, closed in cands:
            ok = []
            for q in seq:
                good = abs(self.G(q.x, q.y) - k) < tol
                if good and len(acc):
                    good = float(((acc - np.array((q.x, q.y))) ** 2).sum(1).min()) > 0.09
                ok.append(good)
            mine = [(q.x, q.y) for q, o in zip(seq, ok) if o]
            if closed and all(ok):
                pieces = [seq + [seq[0]]]
            else:
                if closed and not all(ok):
                    s0 = ok.index(False)
                    seq = seq[s0:] + seq[:s0]
                    ok = ok[s0:] + ok[:s0]
                pieces, cur = [], []
                for q, o in zip(seq, ok):
                    if o:
                        cur.append(q)
                    else:
                        if len(cur) > 1:
                            pieces.append(cur)
                        cur = []
                if len(cur) > 1:
                    pieces.append(cur)
            for pc in pieces:
                out += clip_square(pc)
            if mine:
                acc = np.vstack([acc, np.array(mine)])
        return out


# ---------------------------------------------------------------------------
# surfaces
# ---------------------------------------------------------------------------


def perim_u(p):
    x, y = p[0], p[1]
    e = 1e-5
    if abs(y + HALF) < e:
        return x + HALF
    if abs(x - HALF) < e:
        return 32 + y + HALF
    if abs(y - HALF) < e:
        return 64 + HALF - x
    return 96 + HALF - y


def perim_pt(u):
    u = u % 128.0
    if u < 32:
        return Vector((u - HALF, -HALF))
    if u < 64:
        return Vector((HALF, u - 32 - HALF))
    if u < 96:
        return Vector((HALF - (u - 64), HALF))
    return Vector((-HALF, HALF - (u - 96)))


def perimeter(allruns, step=32 / 26):
    ends = []
    for r in allruns:
        for p in (r[0], r[-1]):
            if max(abs(p.x), abs(p.y)) >= HALF - 1e-6:
                ends.append((perim_u(p), p))
    pts = []
    n = int(round(128 / step))
    for i in range(n):
        u = 128 * i / n
        corner = abs(u % 32) < 1e-6
        if not corner and any(min(abs(u - eu), 128 - abs(u - eu)) < 0.35 for eu, _ in ends):
            continue
        pts.append((u, perim_pt(u)))
    pts += ends
    pts.sort(key=lambda t: t[0])
    out = []
    for u, p in pts:
        if out and (p - out[-1]).length < 0.05:
            continue
        out.append(p)
    return out


def surface(a, F, allruns, levels, keep, zfn, matfn, fill, seed, var=0.03):
    """Delaunay surface over the tile with the contour runs as constraint edges.
    keep(x, y, G) selects faces; zfn(x, y) heights; matfn(x, y, G, zmax) colours."""
    idx, coords, edges = {}, [], []

    def vid(p):
        key = (round(p[0], 4), round(p[1], 4))
        if key not in idx:
            idx[key] = len(coords)
            coords.append(Vector((p[0], p[1])))
        return idx[key]

    per = perimeter(allruns)
    pid = [vid(p) for p in per]
    for i in range(len(pid)):
        if pid[i] != pid[(i + 1) % len(pid)]:
            edges.append((pid[i], pid[(i + 1) % len(pid)]))
    for r in allruns:
        ids = [vid(p) for p in r]
        for i in range(len(ids) - 1):
            if ids[i] != ids[i + 1]:
                edges.append((ids[i], ids[i + 1]))
    rr = random.Random(seed)
    sp = fill
    j = 0
    y = -HALF + sp * 0.5
    while y < HALF:
        x = -HALF + sp * (0.25 + 0.5 * (j % 2))
        while x < HALF:
            px, py = x + rr.uniform(-0.25, 0.25) * sp, y + rr.uniform(-0.25, 0.25) * sp
            if abs(px) < HALF - 0.45 * sp and abs(py) < HALF - 0.45 * sp:
                g = F.G(px, py)
                if keep(px, py, g, True) and min(abs(g - k) for k in levels) > 0.32 * sp:
                    vid((px, py))
            x += sp
        y += sp * 0.87
        j += 1
    res = delaunay_2d_cdt(coords, edges, [], 0, 1e-5)
    vco, faces = res[0], res[2]
    bm = a.bm
    vmap = {}

    def V(k):
        if k not in vmap:
            p = vco[k]
            vmap[k] = bm.verts.new((p.x, p.y, zfn(p.x, p.y)))
        return vmap[k]

    for f in faces:
        cx = sum(vco[k].x for k in f) / len(f)
        cy = sum(vco[k].y for k in f) / len(f)
        g = F.G(cx, cy)
        if not keep(cx, cy, g, False):
            continue
        vs = [V(k) for k in f]
        zmax = max(v.co.z for v in vs)
        face(a, vs, matfn(cx, cy, g, zmax), 1.0, var, out=(0, 0, 1))
    return per


def edge_out(p, q):
    m = (p + q) / 2
    if abs(m.y + HALF) < 1e-4:
        return (0, -1, 0)
    if abs(m.x - HALF) < 1e-4:
        return (1, 0, 0)
    if abs(m.y - HALF) < 1e-4:
        return (0, 1, 0)
    return (-1, 0, 0)


def quad_wall(a, p, q, zp_top, zq_top, zp_bot, zq_bot, mat, out):
    bm = a.bm
    vs = []
    vs.append(bm.verts.new((p.x, p.y, zp_top)))
    if zp_top - zp_bot > 1e-3:
        vs.append(bm.verts.new((p.x, p.y, zp_bot)))
    if zq_top - zq_bot > 1e-3:
        vs.append(bm.verts.new((q.x, q.y, zq_bot)))
    vs.append(bm.verts.new((q.x, q.y, zq_top)))
    if len(vs) >= 3:
        face(a, vs, mat, a.rng.uniform(0.96, 1.04), 0.03, out=out)


def ground(a, F, seed):
    """Banks, wet shores and the bed with its stone patches, plus the tile walls."""
    allruns = []
    for k in GROUND_LEVELS:
        allruns += F.runs(k, 1.0)

    # sand above the waterline (G >= 0, a constraint contour), riverbed under it
    per = surface(a, F, allruns, GROUND_LEVELS, lambda x, y, g, fill: True, F.H,
                  lambda x, y, g, zmax: SAND if g >= 0 else RIVERBED, 1.9, seed)
    n = len(per)
    for i in range(n):
        p, q = per[i], per[(i + 1) % n]
        if (p - q).length < 1e-4:
            continue
        # the tile's cut section: flat w03_sand walls to z=0 on the banks, and
        # w03_riverbed walls under the water skirt across the channel
        m = (p + q) / 2
        mat = SAND if F.G(m.x, m.y) >= 0 else RIVERBED
        quad_wall(a, p, q, F.H(p.x, p.y), F.H(q.x, q.y), 0.0, 0.0, mat, edge_out(p, q))
    bed_stones(a, F, seed)
    return per


def bed_stone_list(F, seed):
    """Every submerged bed stone as (x, y, z_floor, size, height): groups on the
    flat bed mid-channel (one big stone with one or two small ones beside) plus
    small stones scattered along both shore slopes, all tops 0.1-0.25 under the
    surface so they read through the water."""
    out = []
    for x, y, rad, s, sx, ang in bed_patches(F, seed):
        rng = random.Random(s)
        for k in range(rng.randint(1, 3)):
            th = ang + PI * k
            rr = 0.0 if k == 0 else rng.uniform(1.6, 1.9)
            size = rng.uniform(2.9, 3.4) if k == 0 else rng.uniform(1.5, 1.8)
            out.append((x + math.cos(th) * rr, y + math.sin(th) * rr, BED - 0.05, size,
                        0.8 if k == 0 else 0.68, rng.randrange(99999)))  # tops 0.05-0.17 under the surface
    # small stones near the channel edges, on the shore slope under the water
    r = random.Random(seed + 57)
    edge, tries = [], 0
    while len(edge) < 14 and tries < 2000:
        tries += 1
        x, y = r.uniform(-14.5, 14.5), r.uniform(-14.5, 14.5)
        g = F.G(x, y)
        if not (-1.7 < g < -1.0):
            continue
        if any((x - o[0]) ** 2 + (y - o[1]) ** 2 < 9.0 for o in edge + out):
            continue
        z = F.H(x, y)
        size = r.uniform(0.95, 1.35)
        edge.append((x, y, z - 0.08, size, max(0.3, WZ - 0.06 - z), r.randrange(99999)))
    return out + edge


def bed_stones(a, F, seed):
    """Low bed stones on the riverbed (all under the water, so w03_riverbed)."""
    for x, y, z, size, h, s in bed_stone_list(F, seed):
        rng = random.Random(s)
        if size >= 1.6:
            # big bed stones: a few broad planes (steep sides, flat top) whose
            # side facets catch the light through the water
            chunk(a, rng, x, y, size, size * rng.uniform(0.7, 0.85), z, z + h,
                  rings=SLAB_RINGS, ang=rng.uniform(0, PI), cap=0.0)
        else:
            pebble(a, rng, x, y, z, size, hf=min(0.45, h / size))


def bed_patches(F, seed, count=9):
    """Centres of the bed stones (on the flat bed floor near the middle of the
    channel, spread apart)."""
    r = random.Random(seed + 31)
    out, tries = [], 0
    while len(out) < count and tries < 900:
        tries += 1
        x, y = r.uniform(-14.5, 14.5), r.uniform(-14.5, 14.5)
        rad = r.uniform(0.9, 1.2)
        if F.G(x, y) > K_BED - 2.0 or max(abs(x), abs(y)) > 13.0:
            continue
        if any((x - o[0]) ** 2 + (y - o[1]) ** 2 < 40.0 for o in out):
            continue
        out.append((x, y, rad, r.randrange(99999), r.uniform(1.0, 1.6), r.uniform(0, PI)))
    return out


def water(a, F, seed, skirts=True):
    """ONE flat w03_water slab at z=1.0 over the whole channel (its outline
    buried just under the shore slope) and the w03_water skirts across the
    channel at the seams."""
    allruns = []
    for k in WATER_LEVELS:
        allruns += F.runs(k, 1.5)

    def keep(x, y, g, fill):
        return g < (K_WOUT - 0.6 if fill else K_WOUT)

    surface(a, F, allruns, WATER_LEVELS, keep, lambda x, y: WZ, lambda x, y, g, zmax: WATER, 4.6, seed, var=0.0)
    if skirts:
        gruns = []
        for k in GROUND_LEVELS:
            gruns += F.runs(k, 1.0)
        per = perimeter(gruns)
        n = len(per)
        for i in range(n):
            p, q = per[i], per[(i + 1) % n]
            if (p - q).length < 1e-4:
                continue
            m = (p + q) / 2
            if F.G(m.x, m.y) >= 0:
                continue
            quad_wall(a, p, q, WZ, WZ, min(WZ, F.H(p.x, p.y)), min(WZ, F.H(q.x, q.y)), WATER, edge_out(p, q))


# ---------------------------------------------------------------------------
# rocks
# ---------------------------------------------------------------------------


def hull(a, pts, paint_fn, facets=6.0):
    """Convex hull of pts; paint_fn(face) -> (mat, tint)."""
    bm = a.bm
    verts = [bm.verts.new(p) for p in pts]
    res = bmesh.ops.convex_hull(bm, input=verts, use_existing_faces=False)
    junk = list({g for g in res["geom_interior"] + res["geom_unused"]
                 if isinstance(g, bmesh.types.BMVert) and g.is_valid})
    if junk:
        bmesh.ops.delete(bm, geom=junk, context="VERTS")
    verts = [v for v in verts if v.is_valid]
    faces = list({f for v in verts for f in v.link_faces})
    bmesh.ops.recalc_face_normals(bm, faces=faces)
    if facets:
        bmesh.ops.dissolve_limit(bm, angle_limit=math.radians(facets), verts=verts,
                                 edges=list({e for v in verts for e in v.link_edges}))
        verts = [v for v in verts if v.is_valid]
    zs = [v.co.z for v in verts]
    if min(zs) < WZ - 0.02 and max(zs) > WZ + 0.02:
        # cut at the water surface: the wet part under it is riverbed
        edges = list({e for v in verts for e in v.link_edges})
        faces = list({f for v in verts for f in v.link_faces})
        res = bmesh.ops.bisect_plane(bm, geom=verts + edges + faces, dist=1e-4,
                                     plane_co=(0, 0, WZ), plane_no=(0, 0, 1))
        verts = verts + [g for g in res["geom_cut"] if isinstance(g, bmesh.types.BMVert)]
        verts = [v for v in verts if v.is_valid]
    bm.normal_update()
    faces = list({f for v in verts for f in v.link_faces})
    for f in sorted(faces, key=lambda f: tuple(f.calc_center_median())):
        m, t = paint_fn(f)
        if f.calc_center_median().z < WZ:
            m = RIVERBED
        paint(a, [f], m, t, 0.03)
    return verts


def rock_fn(rng):
    """One base colour per rock: w03_rock (the sheet's pale cool grey), with a
    small random per-rock Tint (never by face direction). The light tops come
    from the lighting on the flat top facet."""
    tint = rng.uniform(0.97, 1.03)

    def fn(f):
        return ROCK, tint
    return fn


# Three rings only: a wide base, steep near-upright sides up to ~60% of the
# height, then ONE bevel ring onto a broad flat top, so each boulder reads as a
# few big chunky planes with a flat cap (not a rounded ico ball)
BOULDER_RINGS = ((0.0, 0.92, 7), (0.42, 1.0, 7), (0.8, 0.9, 6), (1.0, 0.66, 5))  # tall chunky anchor: shoulder ring + flat cap
SMALL_RINGS = ((0.0, 0.96, 6), (0.55, 1.0, 5), (1.0, 0.78, 5))
SLAB_RINGS = ((0.0, 0.9, 6), (0.5, 1.0, 6), (1.0, 0.74, 5))  # low flat slab, broad flat top
# bank boulders: anchors ~5 wide and ~3.4 above the waterline (tops at z ~4.3), partners
# ~3.5 wide x 2.7; the clusters dominate the tile's skyline as on the reference
BIG_W, BIG_H, BIG_HMAX = 1.15, 1.12, 3.9
ANCHOR_GROW = 1.18  # the 3 anchors per bank (spec h >= 3.0) are another ~18% wider and deeper
PARTNER_GROW = 1.08  # their ~3.5-wide partners grow a little too, so the clusters read chunky
TOP_MAX = 4.42  # anchor tops level out at z ~4.4-4.5 (the tile is ~4.5 tall)


def chunk(a, rng, x, y, w, dep, floor, top, rings=BOULDER_RINGS, ang=0.0, cap=0.1):
    """Chunky rock: hull of stacked jittered rings (a wide base, a bulging middle,
    a shoulder and a small flat top), so it reads as a few big chiselled facets
    with a flat bevelled top."""
    H = top - floor
    sx, sy = w / 2, dep / 2
    ca, sa = math.cos(ang), math.sin(ang)
    pts = []
    for i, (f, sc, n) in enumerate(rings):
        rot = rng.uniform(0, TAU)
        last = i == len(rings) - 1
        tilt = (rng.uniform(-0.08, 0.08), rng.uniform(-0.08, 0.08))
        for k in range(n):
            th = rot + TAU * k / n + rng.uniform(-0.2, 0.2)
            r = sc * rng.uniform(0.9, 1.08)
            lx, ly = math.cos(th) * sx * r, math.sin(th) * sy * r
            if f == 0.0:
                z = floor
            elif last:
                z = top + (tilt[0] * lx + tilt[1] * ly) * 0.5 + rng.uniform(-0.03, 0.03)
            else:
                z = floor + H * f + rng.uniform(-0.06, 0.06) * H
            pts.append(Vector((x + lx * ca - ly * sa, y + lx * sa + ly * ca, min(z, top + cap))))
    return hull(a, pts, rock_fn(rng), facets=10.0)


def downstream(F, x, y):
    """Unit flow direction of the nearest channel at (x, y)."""
    best = None
    for P in F.paths:
        g = P.g(x, y)
        if best is None or g < best[0]:
            best = (g, P)
    P = best[1]
    p = np.array((x, y))
    t = np.clip(((p - P.a) * P.d).sum(1) / P.len2, 0, 1)
    q = P.a + P.d * t[:, None]
    k = int(np.argmin(((q - p) ** 2).sum(1)))
    d = Vector((P.d[k][0], P.d[k][1])).normalized() * P.flow
    return d


def rock_spot(F, spec):
    """spec: (path, u, d, w, h) in the channel frame, or ("xy", x, y, w, h).
    Returns (pos, tangent, w, h)."""
    if spec[0] == "xy":
        _, x, y, w, h = spec
        return Vector((x, y)), Vector((0, 1)), w, h
    pi, u, d, w, h = spec
    pos, t, n, hw = F.paths[pi].frame(u, d)
    return pos, t, w, h


def place_rock(a, F, spec, seed, stream=False, build=True):
    """Bank boulder (h above the local ground) or low in-stream rock (h above the
    bed). Returns (pos, width, foam) where foam is the water_foam socket
    (pos, scale) when the rock breaks the surface / straddles a waterline."""
    rng = random.Random(seed)
    pos, t, w, h = rock_spot(F, spec)
    if not stream:
        big = h >= 2.4
        grow = ANCHOR_GROW if h >= 3.0 else (PARTNER_GROW if big else 1.0)
        w, h = w * BIG_W * grow, min(BIG_HMAX, h * BIG_H * (1.0 + (grow - 1.0) * 0.5))
    ang = math.atan2(t.y, t.x) + rng.uniform(-0.6, 0.6)
    dep = w * rng.uniform(0.78, 0.95)
    if stream:
        w = w * 1.15  # wide and low (<=1.5 tall), so they read as flat slabs
        dep = w * rng.uniform(0.62, 0.8)
        ang = math.atan2(t.y, t.x) + rng.uniform(-0.3, 0.3)
    zs, gs = [], []
    for k in range(7):
        th = TAU * k / 7
        rr = 0.0 if k == 0 else 0.42 * w
        px, py = pos.x + math.cos(th) * rr, pos.y + math.sin(th) * rr
        zs.append(F.H(px, py))
        gs.append(F.G(px, py))
    zc = F.H(pos.x, pos.y)
    floor = max(0.0, min(zs) - (0.1 if stream else 0.15))
    top = BED + h if stream else min(zc + h, TOP_MAX)
    rings = SLAB_RINGS if stream else (BOULDER_RINGS if big else SMALL_RINGS)
    if build:
        chunk(a, rng, pos.x, pos.y, w, dep, floor, top, rings=rings, ang=ang, cap=0.0 if stream else 0.1)
    foam = None
    if min(gs) < 0.0 and top > WZ:
        if stream:
            fp = pos
        else:
            # on the water side of a straddling boulder: step down the field
            e = 0.3
            gx = F.G(pos.x + e, pos.y) - F.G(pos.x - e, pos.y)
            gy = F.G(pos.x, pos.y + e) - F.G(pos.x, pos.y - e)
            gv = Vector((gx, gy))
            gv = gv.normalized() if gv.length > 1e-6 else Vector((0, 0))
            fp = pos - gv * (w * 0.45)
        foam = (fp, round(min(0.8, max(0.4, 0.13 * w)), 2))
    return pos, w, foam


def pebble(a, rng, x, y, z, s, hf=0.45):
    pts = []
    for _ in range(9):
        th = rng.uniform(0, TAU)
        rr = s * rng.uniform(0.35, 0.55)
        pts.append(Vector((x + math.cos(th) * rr, y + math.sin(th) * rr * 0.85, z + rng.uniform(0.0, s * hf))))
    t = rng.uniform(0.97, 1.03)
    hull(a, pts, lambda f: (ROCK, t), facets=8.0)


def pebbles(a, F, cfg, seed, taken):
    """Rubble: about half the bank pebbles cluster at the boulder bases (as the
    reference's rubble beside the rocks), the rest scatter over banks and bed."""
    rng = random.Random(seed)
    nb, nw = cfg.get("pebbles", (10, 4))
    rocks = [t for t in taken if t[2] > 1.4]
    placed = [0, 0]
    tries = 0
    while (placed[0] < nb or placed[1] < nw) and tries < 900:
        tries += 1
        if rocks and placed[0] < nb // 2 + 1 and tries < 500:
            bx, by, br = rocks[rng.randrange(len(rocks))]
            th = rng.uniform(0, TAU)
            rr = br * rng.uniform(1.15, 1.45) + 0.4
            x, y = bx + math.cos(th) * rr, by + math.sin(th) * rr
        else:
            x, y = rng.uniform(-15.2, 15.2), rng.uniform(-15.2, 15.2)
        if abs(x) > 15.2 or abs(y) > 15.2:
            continue
        g = F.G(x, y)
        kind = 0 if g > 0.9 else (1 if g < K_BED - 0.4 else None)
        if kind is None or placed[kind] >= (nb, nw)[kind]:
            continue
        if any((x - px) ** 2 + (y - py) ** 2 < rad * rad for px, py, rad in taken):
            continue
        s = rng.uniform(0.8, 1.3)
        pebble(a, rng, x, y, F.H(x, y) - 0.05, s)
        taken.append((x, y, 0.7))
        placed[kind] += 1


# ---------------------------------------------------------------------------
# bank dressing (waterfall_module recipes)
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
    paint(a, faces, mat, tint if tint is not None else a.rng.uniform(0.97, 1.03), 0.03)


def tuft(a, x, y, z, s=1.0, n=4):
    rng = a.rng
    for i in range(n):
        ang = TAU * i / n + rng.uniform(-0.5, 0.5)
        frond(a, (x + rng.uniform(-0.25, 0.25) * s, y + rng.uniform(-0.25, 0.25) * s, z - 0.05),
              ang, rng.uniform(1.0, 1.35), rng.uniform(0.8, 1.2) * s, 0.3 * s,
              GRASS, droop=0.12)


def daisy(a, x, y, z, s=1.0):
    """White five-petal daisy (one flat star n-gon) with a yellow centre."""
    bm, rng = a.bm, a.rng
    k = 5
    rot = rng.uniform(0, TAU)
    zz = z + 0.3 * s
    ring = []
    for i in range(2 * k):
        ang = rot + PI * i / k
        rr = (0.45 if i % 2 == 0 else 0.17) * s
        ring.append(bm.verts.new((x + math.cos(ang) * rr, y + math.sin(ang) * rr, zz)))
    face(a, ring, "flower_white", rng.uniform(0.97, 1.03), 0.0, out=(0, 0, 1))
    c = [bm.verts.new((x + math.cos(rot + TAU * i / 3) * 0.14 * s, y + math.sin(rot + TAU * i / 3) * 0.14 * s,
                       zz + 0.02)) for i in range(3)]
    ap = bm.verts.new((x, y, zz + 0.12 * s))
    for i in range(3):
        face(a, (c[i], c[(i + 1) % 3], ap), "flower_yellow", 1.0, 0.0, out=(0, 0, 1))


def dressing(a, F, cfg, seed, taken):
    """Grass tufts and daisies on the dry banks; about half the tufts sit at the
    landward foot of the big boulders, as the reference's base dressing."""
    rng = random.Random(seed)
    nt, nd = cfg.get("dress", (3, 2))
    rocks = [t for t in taken if t[2] > 1.5]
    for kind, count in (("tuft", nt), ("daisy", nd)):
        placed, tries = 0, 0
        while placed < count and tries < 600:
            tries += 1
            # about 70% grouped at the landward foot of the boulder clusters
            if rocks and placed < int(count * 0.7 + 0.5) and tries < 400:
                bx, by, br = rocks[rng.randrange(len(rocks))]
                th = rng.uniform(0, TAU)
                rr = br + rng.uniform(0.7, 1.4)
                x, y = bx + math.cos(th) * rr, by + math.sin(th) * rr
                if abs(x) > 14.8 or abs(y) > 14.8 or F.G(x, y) < 1.2:
                    continue
                if any((x - px) ** 2 + (y - py) ** 2 < (rad + 0.2) ** 2 for px, py, rad in taken if rad < 1.5):
                    continue
                z = F.H(x, y)
                if kind == "tuft":
                    tuft(a, x, y, z, rng.uniform(1.05, 1.3), n=5)
                else:
                    daisy(a, x, y, z, rng.uniform(1.15, 1.35))
                    tuft(a, x + 0.6, y - 0.4, z, 0.6, n=3)
                taken.append((x, y, 1.0))
                placed += 1
                continue
            x, y = rng.uniform(-14.8, 14.8), rng.uniform(-14.8, 14.8)
            if F.G(x, y) < 2.6:
                continue
            if any((x - px) ** 2 + (y - py) ** 2 < (rad + 0.6) ** 2 for px, py, rad in taken):
                continue
            z = F.H(x, y)
            if kind == "tuft":
                tuft(a, x, y, z, rng.uniform(0.95, 1.2), n=5)
            else:
                daisy(a, x, y, z, rng.uniform(1.15, 1.35))
                tuft(a, x + 0.6, y - 0.4, z, 0.6, n=3)
            taken.append((x, y, 1.0))
            placed += 1


# ---------------------------------------------------------------------------
# tiles
# ---------------------------------------------------------------------------


def meander_path(amp, hw0, hw_mid):
    pts = []
    y = -21.0
    while y <= 21.0 + 1e-6:
        t = max(0.0, min(1.0, (y + HALF) / 32.0))
        x = amp * math.sin(TAU * t) * math.sin(PI * t)
        hw = hw0 + (hw_mid - hw0) * math.sin(PI * t) ** 2
        pts.append((x, y, hw))
        y += 0.5
    return Path(pts, flow=-1)  # flows from the waterfall pool at +Y toward -Y


def bend_path():
    C = (HALF, -HALF)
    pts = [(0.0, y, 6.0) for y in np.arange(-21.0, -16.0, 0.5)]
    n = 48
    for i in range(n + 1):
        f = i / n
        th = PI - (PI / 2) * f
        hw = 6.0 + 1.0 * math.sin(PI * f) ** 2  # 12 at the seams, 14 mid-arc
        pts.append((C[0] + 16 * math.cos(th), C[1] + 16 * math.sin(th), hw))
    pts += [(x, 0.0, 6.0) for x in np.arange(16.5, 21.01, 0.5)]
    return Path(pts, flow=-1)  # flows from the right edge round to the front edge


def fork_paths():
    ctrl = [(0.0, -21.0, 6.0), (0.0, -12.0, 6.0), (0.0, -6.5, 6.2), (-0.8, -2.6, 6.6), (-3.4, 0.0, 6.6),
            (-7.5, 0.3, 6.3), (-12.0, 0.0, 6.0), (-21.0, 0.0, 6.0)]
    # both arms flow from their side edge into the stem and out of the front edge
    left = Path(smooth_path(ctrl, 0.5), flow=-1)
    right = Path(smooth_path([(-x, y, h) for x, y, h in ctrl], 0.5), flow=-1)
    return [left, right]


def teardrop(cx, cy, r0, tip, n=28):
    """Smooth islet outline pointing toward -Y (upstream of the split)."""
    pts = []
    for k in range(n):
        th = TAU * k / n
        r = r0 * (1 + tip * max(0.0, -math.sin(th)) ** 2) * (1 + 0.05 * math.sin(3 * th + 0.7))
        pts.append((cx + math.cos(th) * r * 0.95, cy + math.sin(th) * r))
    return pts


def sandbar(C, rc, th_c, half_ang, wid, n=14):
    """Crescent sandbar along an arc about C."""
    outer, inner = [], []
    for k in range(n + 1):
        u = -1 + 2 * k / n
        th = th_c + u * half_ang
        f = (1 - u * u) ** 0.7
        outer.append((C[0] + math.cos(th) * (rc + wid * f), C[1] + math.sin(th) * (rc + wid * f)))
        inner.append((C[0] + math.cos(th) * (rc - wid * f * 0.6), C[1] + math.sin(th) * (rc - wid * f * 0.6)))
    return outer + list(reversed(inner))[1:-1]


def flow_beams(F, cfg):
    """water_flow beams along the centreline: (start, end) pairs, upstream ->
    downstream, consecutive segments sharing their end points."""
    out = []
    for pi, us in cfg.get("flow", ()):
        P = F.paths[pi]
        pts = []
        for u in us:
            p = P.at(P.tile_s(u))[0]
            if u in (0.0, 1.0):  # the chain starts / ends exactly on the seam
                if abs(p.x) >= abs(p.y):
                    p.x = math.copysign(HALF, p.x)
                else:
                    p.y = math.copysign(HALF, p.y)
            pts.append(p)
        out += list(zip(pts, pts[1:]))
    return out


def shore_foam(F, taken_foam, step=8.0):
    """water_foam points every ~step studs along each waterline (just off it),
    skipping spots a rock's foam already covers."""
    out = []
    for run in F.runs(-0.35, 0.8, tol=0.12):
        P = Path2(run)
        if P.L < 3.0:
            continue
        n = max(1, int(round(P.L / step)))
        for i in range(n):
            p = P.at(P.L * (i + 0.5) / n)
            if any((p - q).length < 3.0 for q in taken_foam + out):
                continue
            out.append(p)
    return out


def build_tile(kit, name, cfg, parts=("ground", "water", "rocks", "stream", "dress")):
    """Builds the requested parts of a tile. Returns (asset, field, sockets); the
    sockets (the whole tile's water VFX) are computed whatever parts are built."""
    fk = kit.flintkit
    a = fk.Asset(name, "Terrain", seed=cfg["seed"])
    F = cfg["field"]()
    seed = cfg["seed"]
    taken = []
    foam_rock, foam_riffle = [], []
    if "ground" in parts:
        ground(a, F, seed + 1)
    if "water" in parts:
        water(a, F, seed + 2)
    sel = cfg.get("select")
    for k, spec in enumerate(list(cfg.get("bank", ())) + list(cfg.get("extra_bank", ()))):
        build = "rocks" in parts and (sel is None or ("b", k) in sel)
        pos, w, foam = place_rock(a, F, spec, seed * 10 + k, build=build)
        taken.append((pos.x, pos.y, w * 0.55))
        if foam:
            foam_rock.append(foam)
    for k, spec in enumerate(cfg.get("stream", ())):
        pos, w, foam = place_rock(a, F, spec, seed * 10 + 500 + k, stream=True, build="stream" in parts)
        taken.append((pos.x, pos.y, w * 0.55))
        if foam:
            foam_rock.append(foam)
        # short riffle trailing downstream of the in-stream rock
        p = pos + downstream(F, pos.x, pos.y) * (w * 0.5 + 1.4)
        foam_riffle.append((p, 0.5))
    if "pebbles" in parts or "ground" in parts:
        pebbles(a, F, cfg, seed + 7, list(taken))
    if "dress" in parts:
        dressing(a, F, cfg, seed + 8, taken)

    sockets = []
    for k, (p, q) in enumerate(flow_beams(F, cfg)):
        sockets.append(dict(kind="water_flow", loc=(p.x, p.y, FLOW_Z), end=(q.x, q.y, FLOW_Z),
                            width=cfg.get("flow_width", 5.5), name=f"VFX_StreambedFlowStrips_{k + 1}"))
    extra = [(Vector(loc), sc) for loc, sc in cfg.get("extra_vfx", ())]
    for k, (p, sc) in enumerate(foam_rock + extra):
        sockets.append(dict(kind="water_foam", loc=(p.x, p.y, FOAM_Z), scale=sc, name=f"VFX_StreambedRockFoam_{k + 1}"))
    for k, (p, sc) in enumerate(foam_riffle):
        sockets.append(dict(kind="water_foam", loc=(p.x, p.y, FOAM_Z), scale=sc, name=f"VFX_StreambedRiffle_{k + 1}"))
    covered = [p for p, _ in foam_rock + foam_riffle + extra]
    for k, p in enumerate(shore_foam(F, covered)):
        sockets.append(dict(kind="water_foam", loc=(p.x, p.y, FOAM_Z), scale=0.6, name=f"VFX_StreambedShoreFoam_{k + 1}"))
    return a, F, sockets


def vfx_note(sockets):
    n = {}
    for s in sockets:
        key = s["name"].rsplit("_", 1)[0]
        n[key] = n.get(key, 0) + 1
    return ("VFX: water_flow beams VFX_StreambedFlowStrips_1..%d lie on the water (z 1.03) along the centreline, "
            "start upstream -> end downstream (these ARE the reference's 'Flow Strips (Simple Mesh)': water is VFX, "
            "so no strip mesh); water_foam: %d at rocks that break the surface or straddle a waterline "
            "(VFX_StreambedRockFoam_N), %d riffles downstream of in-stream rocks (VFX_StreambedRiffle_N), %d along "
            "the waterlines every ~8 studs (VFX_StreambedShoreFoam_N). No foam/ripple geometry."
            % (n.get("VFX_StreambedFlowStrips", 0), n.get("VFX_StreambedRockFoam", 0),
               n.get("VFX_StreambedRiffle", 0), n.get("VFX_StreambedShoreFoam", 0)))


def finish(kit, a, role, collision, budget, notes, sockets=()):
    """Clamp to the tile (nothing outside +-16 or below z=0), write the mesh, tag
    it and attach VFX sockets (locs given in tile coordinates)."""
    for v in a.bm.verts:
        v.co.x = min(max(v.co.x, -HALF), HALF)
        v.co.y = min(max(v.co.y, -HALF), HALF)
        v.co.z = max(v.co.z, 0.0)
    xs = [v.co.x for v in a.bm.verts]
    ys = [v.co.y for v in a.bm.verts]
    zs = [v.co.z for v in a.bm.verts]
    off = Vector(((min(xs) + max(xs)) / 2, (min(ys) + max(ys)) / 2, min(zs)))
    obj = a.finish()
    if sockets:
        notes = notes + " " + vfx_note(sockets)
    kit.tag(obj, role, collision=collision, budget=budget, notes=notes)
    for s in sockets:
        kw = {}
        if "end" in s:
            kw["end"] = tuple(Vector(s["end"]) - off)
            kw["width"] = s["width"]
        kit.vfx.add(obj, s["kind"], tuple(Vector(s["loc"]) - off), scale=s.get("scale", 1.0), name=s["name"], **kw)
    return obj


# ---------------------------------------------------------------------------
# configurations (rocks: (path, u along the tile, d half-widths across, width,
# height); d = +-1 is the waterline, so big bank boulders straddle it).
# flow: (path, tile fractions u from upstream to downstream) -> chained beams.
# ---------------------------------------------------------------------------

THROUGH = (1.0, 0.66, 0.33, 0.0)  # three chained beams, upstream (u=1) -> downstream (u=0)

HERO = dict(
    seed=4401,
    # 12 wide at the seams, ~17 wide mid-tile: the water fills about half the tile
    field=lambda: Field([meander_path(2.8, 6.0, 8.5)], seed=4401),
    # clusters = one ~4.4-wide anchor straddling the waterline, a 3-wide partner
    # and 2-wide / 1.5-wide chunks stacked against it (2-4 stud rocks)
    bank=[
        # left bank (-X): front, middle and back clusters (0-10)
        (0, 0.08, -0.86, 4.4, 3.3), (0, 0.19, -1.08, 3.0, 2.4), (0, 0.0, -1.18, 2.2, 1.6),
        (0, 0.45, -0.85, 4.6, 3.4), (0, 0.56, -1.1, 3.2, 2.5), (0, 0.35, -1.12, 2.2, 1.6),
        (0, 0.84, -0.87, 4.2, 3.2), (0, 0.95, -1.08, 3.0, 2.4), (0, 0.74, -1.14, 2.0, 1.4),
        # right bank (+X)
        (0, 0.27, 0.86, 4.4, 3.3), (0, 0.16, 1.08, 3.0, 2.4), (0, 0.38, 1.12, 2.2, 1.6),
        (0, 0.62, 0.86, 4.2, 3.2), (0, 0.72, 1.08, 2.8, 2.2), (0, 0.54, 1.15, 1.9, 1.3),
        (0, 0.92, 0.87, 4.4, 3.3), (0, 0.84, 1.1, 2.6, 2.0), (0, 0.99, 1.12, 2.0, 1.4),
        (0, 0.03, 0.98, 3.0, 2.4), (0, 0.09, 1.25, 1.6, 1.1),
        # lone boulders out on the dry sand, as the reference's back-left corner
        ("xy", -12.6, 12.4, 3.4, 2.6), ("xy", 12.8, -6.0, 3.0, 2.4),
    ],
    stream=[(0, 0.2, 0.12, 2.6, 1.25), (0, 0.37, -0.45, 2.1, 1.1), (0, 0.55, 0.4, 2.8, 1.3),
            (0, 0.72, -0.25, 2.0, 1.1), (0, 0.85, 0.42, 2.3, 1.2)],
    flow=[(0, THROUGH)],
    pebbles=(24, 6), dress=(10, 5),
)

STRAIGHT = dict(
    seed=4411,
    field=lambda: Field([meander_path(0.0, 6.0, 7.6)], seed=4411),
    bank=[
        (0, 0.72, -0.95, 4.6, 3.4), (0, 0.83, -1.08, 3.2, 2.5), (0, 0.62, -1.12, 2.0, 1.4),
        (0, 0.3, 0.95, 4.6, 3.4), (0, 0.41, 1.08, 3.2, 2.5), (0, 0.2, 1.12, 2.0, 1.4),
        (0, 0.1, -0.97, 4.0, 3.0), (0, 0.02, -1.12, 2.0, 1.4), (0, 0.4, -1.0, 3.0, 2.4),
        (0, 0.86, 0.97, 4.2, 3.2), (0, 0.95, 1.12, 2.2, 1.5),
    ],
    stream=[(0, 0.25, -0.3, 2.5, 1.2), (0, 0.52, 0.35, 2.7, 1.3), (0, 0.8, -0.1, 2.1, 1.1)],
    flow=[(0, (1.0, 0.5, 0.0))],
    pebbles=(16, 4), dress=(6, 3),
)

_BC = (HALF, -HALF)
BEND = dict(
    seed=4421,
    field=lambda: Field([bend_path()], [Islet(sandbar(_BC, 9.6, 3 * PI / 4, 0.4, 2.0), 1.4)], seed=4421),
    bank=[
        # outer bank (d < 0): the biggest boulders, a continuous line tracing the curve
        (0, 0.13, -0.95, 4.4, 3.3), (0, 0.39, -0.95, 4.8, 3.4), (0, 0.63, -0.95, 4.4, 3.3), (0, 0.87, -0.96, 4.2, 3.1),
        (0, 0.26, -1.0, 3.2, 2.5), (0, 0.51, -1.02, 3.2, 2.6), (0, 0.76, -1.12, 2.1, 1.5),
        # inner bank: small rocks only
        (0, 0.22, 1.05, 2.0, 1.4), (0, 0.82, 1.06, 1.8, 1.3), ("xy", 9.4, -9.6, 1.4, 1.0),
    ],
    stream=[(0, 0.3, -0.35, 2.5, 1.2), (0, 0.68, -0.25, 2.2, 1.15)],
    flow=[(0, THROUGH)],  # right edge (u=1) -> front edge (u=0)
    pebbles=(18, 4), dress=(7, 3),
    # the broad outer bank (back-left) stays open sand with one loose rock
    extra_bank=[("xy", -9.5, 8.5, 2.0, 1.4)],
)

FORK = dict(
    seed=4431,
    field=lambda: Field(fork_paths(), [Islet(teardrop(0.0, 1.8, 2.7, 0.45), BANK)], seed=4431),
    bank=[
        ("xy", -6.8, -9.6, 4.4, 3.3), ("xy", -9.6, -6.8, 2.6, 1.9), ("xy", -6.4, -14.2, 2.0, 1.4),
        ("xy", 6.9, -8.4, 4.4, 3.3), ("xy", 9.8, -6.6, 2.6, 1.9), ("xy", 6.6, -13.4, 1.8, 1.3),
        ("xy", -10.4, 6.6, 4.2, 3.2), ("xy", -5.6, 7.4, 2.3, 1.7), ("xy", 11.0, 6.5, 4.4, 3.3),
        ("xy", 5.9, 7.3, 2.1, 1.5), ("xy", 0.6, 8.4, 2.8, 2.0),
        # islet in the split
        ("xy", -0.7, 2.5, 2.8, 2.2), ("xy", 1.1, 0.5, 2.0, 1.6), ("xy", 0.2, -0.9, 1.4, 1.0),
    ],
    stream=[("xy", -1.6, -11.0, 2.4, 1.2), ("xy", -11.5, -1.3, 2.2, 1.15), ("xy", 12.0, 1.0, 2.2, 1.15)],
    # each arm from its side edge to the split, then the shared stem to the front edge
    flow=[(0, (1.0, 0.62, 0.3)), (1, (1.0, 0.62, 0.3)), (0, (0.3, 0.0))],
    flow_width=5.0,
    # where the two arms meet in front of the islet
    extra_vfx=[((0.0, -4.6), 0.8)],
    pebbles=(16, 4), dress=(6, 3),
)


# ---------------------------------------------------------------------------
# assets
# ---------------------------------------------------------------------------


def build_hero(kit):
    a, F, sockets = build_tile(kit, "StreambedPatch", HERO)
    return finish(kit, a, "hero", "precise", 8000,
                  "32x32 shallow stream tile, channel 12 wide at both seams (x -6..6, water z=1.0, bed 0.2, banks "
                  "1.6), flowing back (+Y) -> front (-Y) so it continues the WaterfallModule pool mouth; precise so "
                  "banks and bed are walkable / wadeable (the water exports see-through and non-colliding).",
                  sockets)


def build_straight(kit):
    a, F, sockets = build_tile(kit, "StreambedStraight", STRAIGHT)
    return finish(kit, a, "variant", "precise", 8000,
                  "Straight Section: centred 12-wide channel, flowing +Y -> -Y; two bank clusters plus a small "
                  "one, three in-stream rocks.", sockets)


def build_bend(kit):
    a, F, sockets = build_tile(kit, "StreambedBend", BEND)
    return finish(kit, a, "variant", "precise", 8000,
                  "Bend (Smooth Curve): quarter-circle channel (radius 16 about the front-right corner) between "
                  "the right edge (y -6..6) and the front edge (x -6..6), flowing right -> front; big boulders on "
                  "the outer bank, a sandbar on the inner bank.", sockets)


def build_fork(kit):
    a, F, sockets = build_tile(kit, "StreambedFork", FORK)
    return finish(kit, a, "variant", "precise", 8000,
                  "Fork / Split (T-Junction): arms from the left and right edges (each 12 wide, y -6..6) join "
                  "round a sand/rock islet and flow out of the front edge (x -6..6); back edge all bank. One "
                  "flow beam chain per arm plus the stem.", sockets)


def part_bank_rocks(kit):
    # ONE cluster (the hero's left-bank middle group: anchor + partner + chunk,
    # touching one another), so a single convex hull hugs it and never spans
    # the stream; the reference's 'Bank Rocks (Variant)' is one such group
    cfg = dict(HERO, select={("b", 3), ("b", 4), ("b", 5)})
    a, F, _ = build_tile(kit, "StreambedBankRocks", cfg, parts=("rocks",))
    return finish(kit, a, "part", "hull", 4000,
                  "Kit-bash bank boulder cluster in its hero position (left bank, middle): one big chunky "
                  "flat-topped w03_rock anchor (~6 wide, top at z ~4.4) straddling the waterline with a ~3.7-wide "
                  "partner and a small chunk against it; the faces of the bases under the water (z < 1.0) are "
                  "w03_riverbed. The hero places six such clusters (three per bank); one cluster per part keeps "
                  "the convex hull tight to the rocks so it never blocks the stream.")


def part_bed_slab(kit):
    a, F, _ = build_tile(kit, "StreambedBedSlab", HERO, parts=("ground", "pebbles"))
    return finish(kit, a, "part", "precise", 3000,
                  "ground slab: w03_sand banks at z=1.6 sloping to the waterline (z=1.0), w03_riverbed below it "
                  "(underwater slope, bed at 0.2, groups of low bed stones), bank pebbles; flat sand side walls "
                  "on the banks, riverbed walls across the channel; walkable")


def part_submerged(kit):
    a, F, _ = build_tile(kit, "StreambedSubmergedRocks", HERO, parts=("stream",))
    return finish(kit, a, "part", "hull", 2000,
                  "five low flat in-stream slabs (hero positions): faces under the water (z < 1.0) are "
                  "w03_riverbed, the tops that just break the surface w03_rock")


def part_water_plane(kit):
    a, F, sockets = build_tile(kit, "StreambedWaterPlane", HERO, parts=("water",))
    return finish(kit, a, "part", "none", 1500,
                  "ONE flat w03_water slab at z=1.0 over the whole channel with 0.8-deep w03_water skirts at "
                  "both seam ends; see-through, no collision, no foam/ripple geometry. Carries the hero's "
                  "water VFX (the reference's 'Flow Strips' are its water_flow sockets).", sockets)


def build(kit):
    return [build_hero(kit),
            part_bank_rocks(kit), part_bed_slab(kit), part_submerged(kit), part_water_plane(kit),
            build_straight(kit), build_bend(kit), build_fork(kit)]
