"""Build sheet 07: Terrain Kit (modular tiles on a 32-stud grid).

CliffSection, CliffOuterCorner, CliffInnerCorner, RockShelfTwoLevels, GrassRamp,
EarthSwitchback, CaveEntrance, RockArch, Riverbank, RockyLakeshore,
WaterfallCliff, ForestFloor.

Every tile is built on an organic footprint (rounded, wobbling outline with a
ragged rim) that sits inside its nominal grid rectangle. Edges that join a
neighbour stay within ~1 stud of the grid line and keep a constant height;
everything else follows the reference sheet. Cliff faces and water sides face
-Y. Water tiles and the cave carry VFX sockets (see lib/vfx.py).

Run headless:
    blender --background --factory-startup --python build_07_terrain_kit.py

Environment:
    FB_ONLY=CliffSection,GrassRamp   build and render only these tiles (fast
                                     iteration; the .blend and sheet are not saved)
    FB_SAMPLES=16                    Eevee render samples (default 32)
"""

import bisect
import math
import os
import random
import sys

import bmesh
import bpy
import numpy as np
from mathutils import Matrix, Vector
from mathutils.geometry import delaunay_2d_cdt

sys.path.insert(0, r"D:/Projects/Roblox/RBLX-Flintborn/art/blender/lib")
import flintkit as fk  # noqa: E402
import vfx  # noqa: E402

ROOT = r"D:/Projects/Roblox/RBLX-Flintborn/art/blender"
PI = math.pi
GRASS = "grass_ground"         # the sheet's yellow-green tops
GRASS_T = 1.0


# ---------------------------------------------------------------------------
# 2D geometry: organic outlines
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
        self.a = np.array([(v.x, v.y) for v in P])
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
        """Signed distance to the outline, positive inside."""
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

    def normals(self):
        n = len(self.p)
        out = []
        for i in range(n):
            t = (self.p[(i + 1) % n] - self.p[i - 1])
            t = t.normalized() if t.length > 1e-9 else Vector((1, 0))
            out.append(Vector((t.y, -t.x)))
        return out

    def offset(self, d):
        return Poly([p + n * d for p, n in zip(self.p, self.normals())])

    def bbox(self):
        return (float(self.a[:, 0].min()), float(self.a[:, 1].min()),
                float(self.a[:, 0].max()), float(self.a[:, 1].max()))

    def centroid(self):
        return Vector((float(self.a[:, 0].mean()), float(self.a[:, 1].mean())))

    def clip(self, A, B, C):
        """Keep the half-plane A*x + B*y + C >= 0 (Sutherland-Hodgman)."""
        out = []
        P = self.p
        for i in range(len(P)):
            p, q = P[i - 1], P[i]
            fp, fq = A * p.x + B * p.y + C, A * q.x + B * q.y + C
            if fq >= 0:
                if fp < 0:
                    out.append(p + (q - p) * (fp / (fp - fq)))
                out.append(q)
            elif fp >= 0:
                out.append(p + (q - p) * (fp / (fp - fq)))
        return Poly(out)

    def clip_fn(self, g, curve=None):
        """Keep the region g(p) >= 0. Where the outline leaves and re-enters the
        region, the cut follows curve(p_exit, p_entry) (intermediate points)."""
        P = self.p
        n = len(P)
        start = next((i for i in range(n) if g(P[i]) >= 0), None)
        if start is None:
            return Poly([])
        P = P[start:] + P[:start] + [P[start]]

        def cross(p, q):
            lo, hi = 0.0, 1.0  # p outside/inside... find the sign change
            gp = g(p)
            for _ in range(22):
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

    def arcs(self, pred):
        """Contiguous runs of outline points where pred(p) holds (open polylines)."""
        flags = [bool(pred(p)) for p in self.p]
        n = len(flags)
        if all(flags):
            return [self.p + [self.p[0]]]
        if not any(flags):
            return []
        start = next(i for i in range(n) if flags[i] and not flags[i - 1])
        runs, cur = [], []
        for k in range(n):
            i = (start + k) % n
            if flags[i]:
                cur.append(self.p[i])
            elif cur:
                runs.append(cur)
                cur = []
        if cur:
            runs.append(cur)
        return [r for r in runs if len(r) >= 2]

    def pull_inside(self, x, y, margin=0.3):
        if self.sdist(x, y) >= margin:
            return x, y
        c = self.centroid()
        p = Vector((x, y))
        lo, hi = 0.0, 1.0
        for _ in range(18):
            m = (lo + hi) / 2
            q = p.lerp(c, m)
            if self.sdist(q.x, q.y) >= margin:
                hi = m
            else:
                lo = m
        q = p.lerp(c, hi)
        return q.x, q.y


def box_pts(x0, x1, y0, y1):
    return [(x0, y0), (x1, y0), (x1, y1), (x0, y1)]


def fillet(corners, radii, step=0.6):
    """Closed polygon with each corner rounded by an arc of radius radii[i]."""
    C = [Vector(c) for c in corners]
    n = len(C)
    if isinstance(radii, (int, float)):
        radii = [radii] * n
    out = []
    for i in range(n):
        P, A, B = C[i], C[i - 1], C[(i + 1) % n]
        r = radii[i]
        d1, d2 = (A - P).normalized(), (B - P).normalized()
        th = math.acos(max(-1.0, min(1.0, d1.dot(d2))))
        if r <= 0 or th > PI - 1e-3 or th < 1e-3:
            out.append(P)
            continue
        t = min(r / math.tan(th / 2), 0.49 * (A - P).length, 0.49 * (B - P).length)
        r = t * math.tan(th / 2)
        p1 = P + d1 * t
        p2 = P + d2 * t
        cen = P + (d1 + d2).normalized() * (r / math.sin(th / 2))
        a1 = math.atan2(p1.y - cen.y, p1.x - cen.x)
        a2 = math.atan2(p2.y - cen.y, p2.x - cen.x)
        da = (a2 - a1 + PI) % (2 * PI) - PI
        k = max(2, int(abs(da) * r / step) + 1)
        for s in range(k + 1):
            ang = a1 + da * s / k
            out.append(cen + Vector((math.cos(ang), math.sin(ang))) * r)
    return out


def organic(corners, radii, seed, inset=0.25, wob=0.8, ragged=0.2, tight=None, step=0.7, tight_wob=0.25):
    """Rounded, wobbling outline inside the polygon `corners`. Where tight(p) holds
    (tile edges that join a neighbour) it stays within ~0.3 stud of the line."""
    base = Poly(fillet(corners, radii)).resample(step)
    r = random.Random(seed)
    L = base.length()
    ks = [max(1, round(L / w)) for w in (7.0, 3.1, 1.4)]
    ph = [r.uniform(0, 2 * PI) for _ in ks]
    P, N = base.p, base.normals()
    s, ds, tw = 0.0, [], []
    for i in range(len(P)):
        if i:
            s += (P[i] - P[i - 1]).length
        f = 0.5 + 0.5 * (0.55 * math.sin(2 * PI * ks[0] * s / L + ph[0])
                         + 0.3 * math.sin(2 * PI * ks[1] * s / L + ph[1])
                         + 0.15 * math.sin(2 * PI * ks[2] * s / L + ph[2]))
        ds.append((inset + wob * f + r.uniform(0, ragged), 0.05 + tight_wob * f))
        tw.append(1.0 if tight and tight(P[i]) else 0.0)
    n = len(P)
    tws = [sum(tw[(i + k) % n] for k in range(-3, 4)) / 7 for i in range(n)]  # soft transition
    tws = [1.0 if tw[i] else tws[i] for i in range(n)]
    out = [P[i] - N[i] * (ds[i][0] * (1 - tws[i]) + ds[i][1] * tws[i]) for i in range(n)]
    return Poly(out)


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

    def tan(self, s, h=0.8):
        d = self.at(s + h) - self.at(s - h)
        return d.normalized() if d.length > 1e-9 else Vector((1, 0))


# ---------------------------------------------------------------------------
# Low-level mesh helpers
# ---------------------------------------------------------------------------


PROF = {} if os.environ.get("FB_PROF") else None
_DEPTH = [0]


def _tris(bm):
    return sum(len(f.verts) - 2 for f in bm.faces)


def prof(fn):
    """FB_PROF=1: tally triangles added per helper (top-level calls only)."""
    if PROF is None:
        return fn
    depth = _DEPTH

    def w(a, *args, **kw):
        if depth[0]:
            return fn(a, *args, **kw)
        depth[0] += 1
        t0 = _tris(a.bm)
        try:
            return fn(a, *args, **kw)
        finally:
            depth[0] -= 1
            PROF[fn.__name__] = PROF.get(fn.__name__, 0) + _tris(a.bm) - t0
    return w


def paint(a, faces, mat, tint=1.0, var=0.05):
    if isinstance(mat, tuple):
        mat, t2 = mat
        tint *= t2
    mi = a._mi(mat)
    for f in faces:
        f.material_index = mi
        f.smooth = False
        t = tint * (1.0 + a.rng.uniform(-var, var))
        for loop in f.loops:
            loop[a.tint_layer] = (t, t, t, 1.0)


def lerpc(x, xa, xb, ha, hb):
    t = (x - xa) / (xb - xa)
    t = max(0.0, min(1.0, t))
    return ha + (hb - ha) * t


def hull(a, pts, paint_fn, facets=2.0):
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
        paint(a, [f], m, t, 0.07)
    return verts


a_rng = random.Random(7)
KEY = Vector((-0.49, -0.59, 0.64)).normalized()  # baked painterly light direction
ROCK = "cliff_rock"
FAM = {"stone": ("stone_light", "stone_dark"), "cliff_rock": ("cliff_rock_light", "cliff_rock_dark")}
DIRT = "dirt_tan"


def stone_paint(mat, top, tint):
    light, dark = FAM.get(mat, (mat, mat))
    rocky = mat in FAM

    def fn(f):
        nz = f.normal.z
        if nz > 0.9:
            return top, tint * 1.02
        if nz > 0.4:
            return (light, tint * 0.97) if rocky else (mat, tint * 1.1)
        if nz < -0.3:
            return dark, tint * 1.05
        lit = max(0.0, f.normal.dot(KEY))
        if rocky and lit > 0.78 and a_rng.random() < 0.6:  # chipped edges and facets catching the light
            return light, tint * a_rng.uniform(0.82, 0.95)
        k = (1.18 + 0.62 * lit) if rocky else (0.85 + 0.2 * lit)
        return mat, tint * k * a_rng.uniform(0.92, 1.08)
    return fn


@prof
def block(a, c, u, w, d, h, z0, mat=ROCK, top="cliff_rock_light", tint=None, cham=None, bulge=0.3,
          lean=(0.0, 0.0)):
    """Chunky chiselled rock column: one unbroken prism with a bevelled (lit) top
    and two big front planes meeting at an off-centre vertical crease.
    c = footprint centre, u = unit vector along the face, front n = (u.y, -u.x)."""
    rng = a.rng
    n = (u[1], -u[0])
    hw, hd = w / 2, d / 2
    if tint is None:
        tint = rng.uniform(0.86, 1.06)
    ch = cham if cham is not None else min(1.0, 0.18 * min(w, h) + 0.3) * rng.uniform(0.85, 1.2)
    ch = min(ch, hw * 0.6, h * 0.45)

    def P(lu, lv, z):
        t = (z - z0) / h if h > 1e-6 else 0.0
        return Vector((c[0] + u[0] * (lu + lean[0] * t) + n[0] * (lv + lean[1] * t),
                       c[1] + u[1] * (lu + lean[0] * t) + n[1] * (lv + lean[1] * t), z))

    fc = hd * rng.uniform(0.7, 1.1)
    rr = rng.uniform(-0.4, 0.4)
    sf = rng.choice((-1, 1)) * rng.uniform(0.2, 0.34)

    def ring(shift=0.0, out=0.0, sc=1.0):
        r = max(-0.6, min(0.6, rr + shift))
        return [(-hw * sc, -hd), (hw * sc, -hd), (hw * sc, hd - fc), (-hw * sc, hd - fc),
                (hw * sc * r, hd + out), (hw * sc * (r + sf), hd + out - fc * abs(sf) * 0.9),
                (hw * sc * 0.78, hd - fc * 0.3 + out * 0.5), (-hw * sc * 0.8, hd - fc * 0.35 + out * 0.4)]

    j = 0.16
    pts = []
    zs = z0 + h - ch
    nlev = 3 if h < 9 else 4
    for k in range(nlev):
        t = k / (nlev - 1)
        z = z0 + (zs - z0) * t + (rng.uniform(-0.25, 0.25) * min(1, h / 6) if 0 < k < nlev - 1 else 0.0)
        sc = 1.0 + (rng.uniform(0.0, 0.05) if 0 < k < nlev - 1 else 0.0) - 0.04 * t
        out = rng.uniform(0.0, bulge) if 0 < k < nlev - 1 else 0.0
        for lu, lv in ring(rng.uniform(-0.08, 0.08), out, sc):
            pts.append(P(lu + rng.uniform(-j, j), lv + rng.uniform(-j, j), z))
    tilt = rng.uniform(-0.2, 0.2) * min(1.0, h / 3)
    for lu, lv in ring(0.0, 0.0, 0.96):
        ilu = lu - math.copysign(ch, lu) * (1.0 if abs(lu) > hw * 0.7 else 0.3)
        ilv = lv - ch if lv > 0 else lv
        pts.append(P(ilu, ilv, z0 + h + tilt * lu / hw + rng.uniform(-0.05, 0.05)))
    return hull(a, pts, stone_paint(mat, top, tint))


def chunk(a, centre, size, rough=0.12, n=40, clip=None, mat=ROCK, tint=None, exp=0.35, facets=5.0, top=None):
    """Bulbous rock mass (hull of a jittered superellipsoid); exp ~0.6+ gives
    rounded faceted boulders."""
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
        if clip:
            p = clip(p)
        pts.append(p)
    tint = tint if tint is not None else rng.uniform(0.88, 1.06)
    return hull(a, pts, stone_paint(mat, top or FAM.get(mat, (mat,))[0], tint), facets=facets)


# ---------------------------------------------------------------------------
# Surfaces: caps, skirts, grass drapes, cliffs
# ---------------------------------------------------------------------------


@prof
def cap(a, poly, H, mat=(GRASS, GRASS_T), spacing=2.4, holes=(), jz=0.05, seed=0, matfn=None, var=0.03,
        bstep=None):
    """Triangulated surface filling `poly` (minus holes), draped on H(x, y)."""
    bnd = poly.resample(bstep or min(1.3, spacing * 0.5))
    coords = [Vector((p.x, p.y)) for p in bnd.p]
    edges = [(i, (i + 1) % len(coords)) for i in range(len(coords))]
    for h in holes:
        hb = h.resample(bstep or min(1.3, spacing * 0.5))
        o, m = len(coords), len(hb.p)
        coords += [Vector((p.x, p.y)) for p in hb.p]
        edges += [(o + i, o + (i + 1) % m) for i in range(m)]
    nb = len(coords)
    r = random.Random(seed)
    x0, y0, x1, y1 = poly.bbox()
    j = 0
    y = y0 + spacing * 0.5
    while y < y1:
        x = x0 + spacing * (0.25 + 0.5 * (j % 2))
        while x < x1:
            px, py = x + r.uniform(-0.28, 0.28) * spacing, y + r.uniform(-0.28, 0.28) * spacing
            if poly.sdist(px, py) > spacing * 0.42 and all(h.sdist(px, py) < -spacing * 0.42 for h in holes):
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
        if not poly.inside(cx, cy) or any(h.inside(cx, cy) for h in holes):
            continue
        try:
            bf = bm.faces.new([V(k) for k in f])
        except ValueError:
            continue
        out.append(bf)
        m = matfn(cx, cy, H(cx, cy)) if matfn else mat
        paint(a, [bf], m, 1.0, var)
    return out


@prof
def skirt(a, pts, ztop, zbot, mat="earth", closed=False, inward=0.05, tint=1.0, var=0.05, lumpy=0.0):
    """Band under an outline (outside to the right). ztop/zbot: f(p) or float.
    `lumpy` pushes the bottom edge out irregularly (a low rounded dirt skirt)."""
    bm = a.bm
    P = list(pts) + ([pts[0]] if closed else [])
    zt = ztop if callable(ztop) else (lambda p, v=ztop: v)
    zb = zbot if callable(zbot) else (lambda p, v=zbot: v)
    rng = a.rng
    rows = []
    for k, p in enumerate(P):
        t = P[min(k + 1, len(P) - 1)] - P[max(k - 1, 0)]
        t = t.normalized() if t.length > 1e-9 else Vector((1, 0))
        n = Vector((t.y, -t.x))
        q = p - n * inward + n * (lumpy * (0.6 + 0.4 * math.sin(k * 1.3)) * rng.uniform(0.6, 1.0))
        rows.append((bm.verts.new((p.x, p.y, zt(p))), bm.verts.new((q.x, q.y, zb(p)))))
    for k in range(len(rows) - 1):
        (t0, b0), (t1, b1) = rows[k], rows[k + 1]
        f = bm.faces.new((t0, b0, b1, t1))
        paint(a, [f], mat, tint * rng.uniform(0.9, 1.08), var)


def resample(pts, seg):
    P = [Vector((p[0], p[1])) for p in pts]
    out = []
    for k in range(len(P) - 1):
        d = P[k + 1] - P[k]
        n = max(1, int(round(d.length / seg)))
        for s in range(n):
            out.append(P[k] + d * (s / n))
    out.append(P[-1])
    return out


@prof
def drape(a, pts, zfn, out=0.5, inn=0.5, drop=(0.3, 1.1), seg=1.5, mask=None, mat=(GRASS, GRASS_T)):
    """Grass draping over an edge (outside to the right): flush with the top,
    hanging down the face in uneven tongues, same green as the top."""
    bm, rng = a.bm, a.rng
    zf = zfn if callable(zfn) else (lambda p, v=zfn: v)
    S = resample(pts, seg)
    p1, p2 = rng.uniform(0, 2 * PI), rng.uniform(0, 2 * PI)
    rows = []
    for k, p in enumerate(S):
        t = (S[min(k + 1, len(S) - 1)] - S[max(k - 1, 0)])
        t = t.normalized() if t.length > 1e-9 else Vector((1, 0))
        n = Vector((t.y, -t.x))
        if mask is not None and not mask(p):
            rows.append(None)
            continue
        z = zf(p)
        s = k * seg
        v = 0.5 + 0.5 * math.sin(s * 0.9 + p1) * math.cos(s * 0.37 + p2)
        dz = drop[0] + (drop[1] - drop[0]) * (v ** 1.3) * rng.uniform(0.7, 1.0)
        if k % 2:
            dz *= rng.uniform(0.25, 0.5)
        o = out * rng.uniform(0.85, 1.1)
        tp, bp, ip = p + n * o, p + n * (o + 0.06), p - n * inn
        rows.append((bm.verts.new((ip.x, ip.y, z + 0.03)), bm.verts.new((tp.x, tp.y, z + 0.04)),
                     bm.verts.new((bp.x, bp.y, z - dz))))
    for k in range(len(rows) - 1):
        r0, r1 = rows[k], rows[k + 1]
        if r0 is None or r1 is None:
            continue
        f1 = bm.faces.new((r0[0], r0[1], r1[1], r1[0]))
        f2 = bm.faces.new((r0[1], r0[2], r1[2], r1[1]))
        t = rng.uniform(0.97, 1.05)
        paint(a, [f1], mat, t, 0.03)
        paint(a, [f2], mat, t * 0.98, 0.04)


@prof
def cliff(a, pts, z0, ztop, depth=3.6, wr=(2.6, 5.2), out=0.55, drop=(0.0, 0.35), steps=0.15, step_h=(0.25, 0.55),
          lean=0.3, ztop_fn=None, zbot_fn=None, mat=ROCK, top="cliff_rock_light", jag=0.9, min_h=0.5,
          sunk=0.4, bulge=0.45, moss=0.32, gap=0.9, foot=0.0):
    """Irregular full-height rock columns along a polyline (face to the right):
    mixed widths, slightly leaning and staggered in depth, bevelled lit tops a
    touch proud of the grass, mossy patches running down the faces.
    Returns ledge spots (pos2, z, n)."""
    rng = a.rng
    path = Path2(pts)
    L = path.L
    ledges = []
    s = 0.0
    while s < L - 0.3:
        w = min(rng.uniform(*wr), L - s)
        if L - s - w < 1.2:
            w = L - s
        sc = s + w / 2
        c = path.at(sc)
        u = path.tan(sc)
        n = Vector((u.y, -u.x))
        s += w
        zt = ztop_fn(c) if ztop_fn else ztop
        zb = zbot_fn(c) if zbot_fn else z0
        Ht = zt - zb
        if Ht < min_h:
            continue
        hi = zt - rng.uniform(*drop)
        tp = top
        off = out + rng.uniform(-jag, jag) * 0.6
        join = s - w < 2.5 or s > L - 2.5          # keep the ends flush where tiles meet
        if Ht > 3.5 and not join:                  # uneven skyline: tops step up and down
            r = rng.random()
            if r < sunk:
                hi = zt - Ht * rng.uniform(0.08, 0.22)
                tp = (GRASS, 0.97)
                off += rng.uniform(0.5, 0.9)       # stepped columns stand a little proud
                ledges.append((c + n * (off - depth * 0.4), hi, n))
            elif r < sunk + 0.15:
                hi = zt + rng.uniform(0.2, 0.6)
        lo = zb - 0.35
        cc = c - n * (depth / 2) + n * off
        ln = (rng.uniform(-lean, lean), -rng.uniform(0.0, lean))
        block(a, cc, u, w * gap, depth, hi - lo, lo, mat=mat, top=tp, lean=ln, bulge=bulge)
        if foot and zb < 1.2 and rng.random() < foot:  # big boulders sunk at the foot
            q = c + n * (off + rng.uniform(0.6, 1.6)) + u * rng.uniform(-w * 0.4, w * 0.4)
            boulder(a, q.x, q.y, zb - 0.25, rng.uniform(1.6, 3.0), rng.uniform(0.8, 1.0))
        if Ht > 2.5 and rng.random() < moss:  # moss running down the face
            for k in range(rng.randint(1, 2)):
                zm = hi - rng.uniform(0.9, min(Ht * 0.45, 3.5))
                q = c + n * (off + 0.08) + u * rng.uniform(-w * 0.3, w * 0.3)
                a.ico((rng.uniform(0.3, 0.6) * min(1.0, w / 3), 0.18, rng.uniform(1.0, 2.2)), loc=(q.x, q.y, zm),
                      rot=(0, 0, math.atan2(u.y, u.x)), subdiv=1, jitter=0.08,
                      mat=rng.choice(["leaf", "grass_dark", "leaf_dark"]), face_tint_var=0.05)
        if Ht > 5.0 and rng.random() < steps:
            sh = zb + Ht * rng.uniform(*step_h)
            fw = w * rng.uniform(0.6, 0.95)
            fo = off + rng.uniform(1.3, 2.2)
            block(a, c - n * (depth / 2) + n * fo + u * rng.uniform(-0.4, 0.4), u, fw, depth * 0.85, sh - lo, lo,
                  mat=mat, top=(GRASS, 0.97), bulge=bulge)
            ledges.append((c + n * (fo - 0.7), sh, n))
    return ledges


@prof
def fill_prism(a, poly, z0, z1, mat="cliff_rock_dark", tint=0.6):
    """Hidden occluder walls (no caps) so no gaps show between columns."""
    bm = a.bm
    P = poly.resample(3.4).p
    bot = [bm.verts.new((p.x, p.y, z0)) for p in P]
    top = [bm.verts.new((p.x, p.y, z1)) for p in P]
    n = len(P)
    faces = [bm.faces.new((bot[i], bot[(i + 1) % n], top[(i + 1) % n], top[i])) for i in range(n)]
    paint(a, faces, mat, tint, 0.03)


@prof
def grass_patches(a, H, ok, box, count, rad=(1.2, 3.0), lift=0.07, seg=12, seed=0, light=0.6):
    """Soft wobbly light (and some darker) grass patches laid over a surface."""
    bm = a.bm
    r = random.Random(seed)
    x0, x1, y0, y1 = box
    placed = 0
    for _ in range(count * 12):
        if placed >= count:
            break
        bx, by = r.uniform(x0, x1), r.uniform(y0, y1)
        br = r.uniform(*rad)
        p1, p2 = r.uniform(0, 2 * PI), r.uniform(0, 2 * PI)
        ring = []
        good = ok(bx, by)
        for k in range(seg):
            if not good:
                break
            ang = 2 * PI * k / seg
            re = br * (1 + 0.25 * math.sin(2 * ang + p1) + 0.12 * math.sin(5 * ang + p2))
            x, y = bx + math.cos(ang) * re, by + math.sin(ang) * re
            if not ok(x, y):
                good = False
            ring.append((x, y))
        if not good:
            continue
        mat = ("grass_light", 1.0) if r.random() < light else (GRASS, 0.86)
        c = bm.verts.new((bx, by, H(bx, by) + lift))
        vs = [bm.verts.new((x, y, H(x, y) + lift)) for x, y in ring]
        faces = [bm.faces.new((c, vs[k], vs[(k + 1) % seg])) for k in range(seg)]
        paint(a, faces, mat, 1.0, 0.02)
        placed += 1


def blob_poly(cx, cy, r, seed, seg=18, amp=(0.22, 0.12), sx=1.0, sy=1.0):
    rr = random.Random(seed)
    p1, p2 = rr.uniform(0, 2 * PI), rr.uniform(0, 2 * PI)
    pts = []
    for k in range(seg):
        ang = 2 * PI * k / seg
        re = r * (1 + amp[0] * math.sin(3 * ang + p1) + amp[1] * math.sin(5 * ang + p2))
        pts.append((cx + math.cos(ang) * re * sx, cy + math.sin(ang) * re * sy))
    return Poly(pts)


def catmull(p0, p1, p2, p3, t):
    t2, t3 = t * t, t * t * t
    return 0.5 * ((2 * p1) + (-p0 + p2) * t + (2 * p0 - 5 * p1 + 4 * p2 - p3) * t2
                  + (-p0 + 3 * p1 - 3 * p2 + p3) * t3)


def smooth_path(pts, step=1.0):
    P = [Vector((p[0], p[1])) for p in pts]
    out = []
    for k in range(len(P) - 1):
        p0, p1, p2, p3 = P[max(k - 1, 0)], P[k], P[k + 1], P[min(k + 2, len(P) - 1)]
        n = max(1, int((p2 - p1).length / step))
        for s in range(n):
            out.append(catmull(p0, p1, p2, p3, s / n))
    out.append(P[-1])
    return out


@prof
def ribbon(a, pts, width, H, mat="dirt", lift=0.09, step=0.9, wobble=0.0, tint=1.0, taper=True,
           smooth=True, seed=None, clip=None, maxdz=0.6, across=1, var=0.04):
    """Strip draped over H (`across` subdivisions across the width so it follows
    curved ground). `wobble` modulates each edge's width; `clip` keeps it inside."""
    bm = a.bm
    r = random.Random(seed if seed is not None else a.rng.random())
    ph = [r.uniform(0, 2 * PI) for _ in range(4)]
    S = smooth_path(pts, step) if smooth else [Vector((p[0], p[1])) for p in pts]
    rows = []
    for k, p in enumerate(S):
        t = (S[min(k + 1, len(S) - 1)] - S[max(k - 1, 0)]).normalized()
        nn = Vector((-t.y, t.x))
        f = 0.65 if taper and (k == 0 or k == len(S) - 1) else 1.0
        wl = width / 2 * f * (1 + wobble * (0.6 * math.sin(k * 0.55 + ph[0]) + 0.4 * math.sin(k * 1.7 + ph[1])))
        wr = width / 2 * f * (1 + wobble * (0.6 * math.sin(k * 0.6 + ph[2]) + 0.4 * math.sin(k * 1.5 + ph[3])))
        l, rr = p + nn * wl, p - nn * wr
        if clip is not None:
            l = Vector(clip.pull_inside(l.x, l.y, 0.25))
            rr = Vector(clip.pull_inside(rr.x, rr.y, 0.25))
        hc = H(p.x, p.y)
        row = []
        for i in range(across + 1):
            q = rr.lerp(l, i / across)
            hq = H(q.x, q.y)
            if abs(hq - hc) > maxdz:
                hq = hc
            row.append(bm.verts.new((q.x, q.y, hq + lift)))
        rows.append(row)
    for k in range(len(S) - 1):
        for i in range(across):
            f = bm.faces.new((rows[k][i], rows[k + 1][i], rows[k + 1][i + 1], rows[k][i + 1]))
            paint(a, [f], mat, tint, var)


def path(a, pts, width, H, lift=0.12, clip=None, across=1):
    """Tan path: sandy fringe with a warm core, soft wobbly edges."""
    ribbon(a, pts, width, H, mat=("sand", 1.0), lift=lift, wobble=0.08, step=0.8, clip=clip, across=across, var=0.0)
    ribbon(a, pts, width * 0.72, H, mat=("thatch", 1.02), lift=lift + 0.05, wobble=0.1, step=0.8, clip=clip,
           across=across, var=0.0)


def clamp_fp(a, x0, x1, y0, y1):
    for v in a.bm.verts:
        v.co.x = min(max(v.co.x, x0), x1)
        v.co.y = min(max(v.co.y, y0), y1)
        v.co.z = max(v.co.z, 0.0)


# ---------------------------------------------------------------------------
# Vegetation and props
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
    paint(a, faces, mat, tint if tint is not None else a.rng.uniform(0.95, 1.1), 0.05)


@prof
def tuft(a, x, y, z, s=1.0, n=3, dark=True):
    """Spiky grass tuft: dark green (the sheet's shadow tufts) or bright."""
    rng = a.rng
    mats = ["grass_dark", "leaf_dark", "grass_dark", "leaf"] if dark else ["grass_light", "grass_light", GRASS]
    for i in range(n):
        ang = 2 * PI * i / n + rng.uniform(-0.5, 0.5)
        frond(a, (x + rng.uniform(-0.25, 0.25) * s, y + rng.uniform(-0.25, 0.25) * s, z - 0.05),
              ang, rng.uniform(1.0, 1.35), rng.uniform(0.8, 1.3) * s, 0.3 * s, rng.choice(mats), droop=0.12)


@prof
def moss(a, x, y, z, s=1.0):
    a.ico((0.95 * s, 0.95 * s, 0.32 * s), loc=(x, y, z + 0.05), subdiv=1, jitter=0.1,
          mat=a.rng.choice([GRASS, "grass_dark", GRASS]), face_tint_var=0.05)
    if a.rng.random() < 0.7:
        tuft(a, x + 0.3, y, z, 0.75 * s)


@prof
def fern(a, x, y, z, s=1.0):
    rng = a.rng
    k = 8
    for i in range(k):
        ang = 2 * PI * i / k + rng.uniform(-0.25, 0.25)
        frond(a, (x, y, z - 0.05), ang, rng.uniform(0.6, 0.95), rng.uniform(1.8, 2.4) * s,
              0.8 * s, rng.choice(["leaf_dark", "leaf", "pine", "leaf"]), droop=0.45)


@prof
def bush(a, x, y, z, s=1.0):
    """Round fluffy bush: dark lobes round the base, a brighter crown on top."""
    rng = a.rng
    R = 1.2 * s
    n = 3
    for i in range(n):
        ang = 2 * PI * i / n + rng.uniform(-0.35, 0.35)
        r = R * rng.uniform(0.58, 0.74)
        a.ico(r, loc=(x + math.cos(ang) * R * 0.52, y + math.sin(ang) * R * 0.52, z + r * 0.7), subdiv=1,
              jitter=0.12, mat=rng.choice(["leaf_dark", "pine", "leaf_dark"]), face_tint_var=0.08,
              tint=0.85)
    r = R * rng.uniform(0.62, 0.75)
    a.ico(r, loc=(x + rng.uniform(-0.2, 0.2) * R, y + rng.uniform(-0.2, 0.2) * R, z + R * 1.0), subdiv=2,
          jitter=0.1, facets=26, mat="leaf", face_tint_var=0.07)


@prof
def broadleaf(a, x, y, z, s=1.0):
    s *= 0.95
    rng = a.rng
    a.cyl(0.55 * s, 0.38 * s, 3.2 * s, 6, loc=(x, y, z - 0.3), mat="bark", jitter=0.05)
    for k in range(3):
        ang = rng.uniform(0, 2 * PI)
        a.cyl(0.24 * s, 0.05, 1.5 * s, 4, loc=(x, y, z + 2.3 * s), rot=(0.8, 0, ang), mat="bark")
    for k in range(4):
        ang = 2 * PI * k / 4 + rng.uniform(-0.3, 0.3)
        a.cyl(0.35 * s, 0.05, 1.3 * s, 4, loc=(x, y, z + 0.35 * s), rot=(1.25, 0, ang), mat="bark")
    blobs = [(0, 0, 4.7, 2.05)] + [(math.cos(t) * 1.5, math.sin(t) * 1.5, 4.0 + rng.uniform(-0.2, 0.4), 1.45)
                                   for t in (0.3, 2.4, 4.4)] + [(0.2, 0.1, 5.9, 1.35)]
    for bx, by, bz, r in blobs:
        a.ico(r * s * rng.uniform(0.92, 1.08), loc=(x + bx * s, y + by * s, z + bz * s), subdiv=2,
              jitter=0.08, facets=9, mat=rng.choice(["leaf", "leaf", "leaf_dark", "leaf_light"]),
              face_tint_var=0.07)


@prof
def star_cone(a, x, y, z, r, h, pts=9, inner=0.62, droop=0.35, mat="pine", rot=0.0):
    """Jagged pine tier: star-shaped cone whose tips droop."""
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
    paint(a, faces[0::2], mat, rng.uniform(0.92, 1.08), 0.08)
    paint(a, faces[1::2], "pine_dark", 0.7, 0.05)


@prof
def pine(a, x, y, z, s=1.0):
    s *= 0.8
    rng = a.rng
    a.cyl(0.42 * s, 0.32 * s, 2.2 * s, 6, loc=(x, y, z - 0.3), mat="bark")
    for k in range(5):
        r = (2.3 - 0.36 * k) * s
        star_cone(a, x, y, z + (1.5 + 1.15 * k) * s, r, 2.3 * s, pts=8 if k < 3 else 7,
                  mat="pine" if k % 2 == 0 else "pine_dark", rot=rng.uniform(0, PI))


@prof
def boulder(a, x, y, z, s, tall=1.0, mat=ROCK, round_=0.62):
    """Rounded faceted boulder."""
    rng = a.rng
    chunk(a, (x, y, z + s * 0.32 * tall), (s * rng.uniform(1.0, 1.25), s * rng.uniform(0.85, 1.05), s * 0.92 * tall),
          rough=0.1, n=26, exp=round_, clip=lambda p: Vector((p.x, p.y, max(p.z, z - 0.2))), mat=mat, facets=6.0)


def pebble(a, x, y, z, s=0.7):
    boulder(a, x, y, z, s * a.rng.uniform(0.8, 1.2), 0.7)


def shore_rock(a, x, y, z, s):
    """Rounded, chunky water-worn rock sitting at the waterline."""
    boulder(a, x, y, z, s * 1.05, 1.05, round_=0.6)


class Scatter:
    """Random placement with spacing, shared by everything on a tile."""

    def __init__(self, a):
        self.a = a
        self.pts = []

    def free(self, x, y, r):
        return all((x - px) ** 2 + (y - py) ** 2 > (r + pr) ** 2 for px, py, pr in self.pts)

    def add(self, x, y, r):
        self.pts.append((x, y, r))

    def put(self, x, y, r, fn, H):
        fn(x, y, H(x, y))
        self.add(x, y, r)

    def many(self, n, ok, H, fn, box, r=1.5, keep=True):
        rng = self.a.rng
        placed = 0
        for _ in range(n * 40):
            if placed >= n:
                break
            x, y = rng.uniform(box[0], box[1]), rng.uniform(box[2], box[3])
            if not ok(x, y) or not self.free(x, y, r):
                continue
            fn(x, y, H(x, y))
            if keep:
                self.add(x, y, r)
            placed += 1
        return placed


@prof
def clump(a, x, y, z, s=1.0):
    """Low dark grass clump."""
    rng = a.rng
    for k in range(2):
        r = s * rng.uniform(0.55, 0.8)
        a.ico((r, r * rng.uniform(0.8, 1.0), r * 0.55), loc=(x + rng.uniform(-0.4, 0.4) * s, y + rng.uniform(-0.4, 0.4) * s,
                                                             z + r * 0.12), subdiv=1, jitter=0.12,
              mat=rng.choice(["grass_dark", "grass_dark", "leaf_dark"]), face_tint_var=0.06)


@prof
def flower(a, x, y, z):
    rng = a.rng
    m = rng.choice(["flower_yellow", "flower_yellow", "flower_white", "berry"])
    a.cyl(0.22, 0.0, 0.3, 3, loc=(x, y, z + 0.22), rot=(PI, 0, rng.uniform(0, PI)), mat=m, cap=False)


def rim_boulders(a, pts, z, every=(3.5, 6.0), size=(1.6, 2.6), inset=0.4, chance=0.8, grassy=0.4):
    """Rounded stones bedded along a rim (outside to the right), some grass-capped."""
    rng = a.rng
    pth = Path2(pts)
    s = rng.uniform(0.5, every[0])
    while s < pth.L - 0.5:
        c, u = pth.at(s), pth.tan(s)
        n = Vector((u.y, -u.x))
        if rng.random() < chance:
            sz = rng.uniform(*size)
            q = c - n * inset
            g = rng.random() < grassy
            chunk(a, (q.x, q.y, z - sz * 0.1), (sz * rng.uniform(1.1, 1.5), sz * rng.uniform(0.9, 1.1), sz * 0.85),
                  rough=0.1, n=24, exp=0.6, clip=lambda p, z=z: Vector((p.x, p.y, max(p.z, z - 1.2))),
                  top=(GRASS, 0.97) if g else None)
        s += rng.uniform(*every)


def decorate(a, sc, poly, H, bushes=0, boulders=0, pebbles=0, tufts=0, margin=1.6, avoid=None, bs=(0.95, 1.3),
             rs=(2.0, 3.0), clumps=None, flowers=None, light_tufts=None):
    """Scatter dressing; `tufts` are the dark tufts the sheet is covered in."""
    rng = a.rng
    x0, y0, x1, y1 = poly.bbox()
    box = (x0, x1, y0, y1)
    clumps = tufts // 6 if clumps is None else clumps
    flowers = tufts // 3 if flowers is None else flowers
    light_tufts = tufts // 3 if light_tufts is None else light_tufts

    def ok(m):
        return lambda x, y: poly.sdist(x, y) > m and not (avoid and avoid(x, y))

    sc.many(boulders, ok(margin + 0.6), H, lambda x, y, z: boulder(a, x, y, z, rng.uniform(*rs)), box, r=2.0)
    sc.many(bushes, ok(margin), H, lambda x, y, z: bush(a, x, y, z, rng.uniform(*bs)), box, r=1.5)
    sc.many(pebbles, ok(0.8), H, lambda x, y, z: pebble(a, x, y, z, rng.uniform(0.6, 1.0)), box, r=0.7)
    sc.many(clumps, ok(0.7), H, lambda x, y, z: clump(a, x, y, z, rng.uniform(0.8, 1.3)), box, r=0.6, keep=False)
    sc.many(tufts, ok(0.5), H, lambda x, y, z: tuft(a, x, y, z, rng.uniform(1.0, 1.4)), box, r=0.4, keep=False)
    sc.many(light_tufts, ok(0.5), H, lambda x, y, z: tuft(a, x, y, z, rng.uniform(0.9, 1.2), 4, False), box,
            r=0.4, keep=False)
    sc.many(flowers, ok(0.5), H, lambda x, y, z: flower(a, x, y, z), box, r=0.3, keep=False)


def ledge_decor(a, ledges, chance=0.85, bush_p=0.3):
    for p, z, n in ledges:
        r = a.rng.random()
        if r < bush_p:
            bush(a, p.x, p.y, z - 0.1, a.rng.uniform(0.6, 0.8))
        elif r < chance:
            moss(a, p.x, p.y, z, a.rng.uniform(0.7, 1.05))


def torch_post(a, x, y, z, h=3.6):
    """Standing torch on the cave floor: post, iron cup, flame."""
    a.cyl(0.2, 0.16, h, 6, loc=(x, y, z - 0.2), mat="wood", jitter=0.02)
    a.cyl(0.32, 0.42, 0.5, 6, loc=(x, y, z + h - 0.3), mat="iron_dark")
    a.flame(1.2, 0.36, loc=(x, y, z + h + 0.15), tongues=5)
    for k in range(3):
        ang = 2 * PI * k / 3
        a.cyl(0.12, 0.04, 1.0, 4, loc=(x, y, z + 0.5), rot=(2.6, 0, ang), mat="wood_dark")
    return Vector((x, y, z + h + 0.6))


@prof
def root(a, x, y, z, ang, r0, L, zg=None):
    """Sprawling tapered root: arches out of the stump and snakes along the ground."""
    rng = a.rng
    zg = z - r0 * 1.6 if zg is None else zg
    pts = []
    n = 4
    bend = rng.uniform(-0.5, 0.5)
    for k in range(n + 1):
        t = k / n
        aa = ang + bend * t * t
        rr = L * t
        h = zg + (z - zg) * (1 - t) ** 1.6 + 0.35 * math.sin(PI * t) * r0
        pts.append(Vector((x + math.cos(aa) * rr, y + math.sin(aa) * rr, h)))
    for k in range(n):
        p, q = pts[k], pts[k + 1]
        d = q - p
        ra = r0 * (1 - 0.8 * k / n)
        rb = r0 * (1 - 0.8 * (k + 1) / n)
        rot = d.to_track_quat("Z", "Y").to_euler()
        a.cyl(ra, max(rb, 0.06), d.length + ra * 0.3, 5, loc=tuple(p), rot=tuple(rot), mat="bark", jitter=0.03)


@prof
def stump(a, x, y, z, r=1.6, h=3.0):
    rng = a.rng
    a.cyl(r * 1.45, r * 1.05, h * 0.32, 10, loc=(x, y, z - 0.3), mat="bark", jitter=0.08)
    a.cyl(r * 1.05, r * 0.98, h * 0.68, 10, loc=(x, y, z - 0.3 + h * 0.32), mat="bark", jitter=0.07)
    zt = z - 0.3 + h
    a.cyl(r * 0.98, r * 0.92, 0.12, 10, loc=(x, y, zt), mat="wood_end")
    a.cyl(r * 0.55, r * 0.5, 0.18, 10, loc=(x, y, zt), mat="wood_light")
    for k in range(3):
        ang = rng.uniform(0, PI)
        a.box((r * rng.uniform(0.9, 1.5), 0.14, 0.12), loc=(x + math.cos(ang) * r * 0.3, y + math.sin(ang) * r * 0.3,
                                                            zt + 0.1), rot=(0, 0, ang), mat="wood_dark")
    nroots = rng.randint(6, 7)
    for k in range(nroots):
        ang = 2 * PI * k / nroots + rng.uniform(-0.25, 0.25)
        root(a, x + math.cos(ang) * r * 0.7, y + math.sin(ang) * r * 0.7, z + r * 0.95, ang,
             r * 0.42, r * rng.uniform(1.9, 2.7), zg=z - 0.15)


def vfx_add(o, kind, loc, **kw):
    """VFX socket at a build-space location (tiles whose bottom is above z=0 shift down)."""
    return vfx.add(o, kind, (loc[0], loc[1], loc[2] - o.get("build_z0", 0.0)), **kw)


def done(a, fp):
    """Clamp to the grid footprint, finish, and keep the origin at the nominal
    footprint's bottom centre even when the organic outline sits inset."""
    clamp_fp(a, *fp)
    xs = [v.co.x for v in a.bm.verts]
    ys = [v.co.y for v in a.bm.verts]
    bc = Vector(((min(xs) + max(xs)) / 2, (min(ys) + max(ys)) / 2, 0))
    nominal = Vector(((fp[0] + fp[1]) / 2, (fp[2] + fp[3]) / 2, 0))
    zmin = min(v.co.z for v in a.bm.verts)
    o = a.finish()
    o.data.transform(Matrix.Translation(bc - nominal))
    o["build_z0"] = zmin  # build-space height of the tile bottom (origin)
    o.data.update()
    print(f"TILE {o.name}: tris={o['tris']} studs={o['studs']}")
    if PROF is not None:
        print("PROF", o.name, sorted(PROF.items(), key=lambda kv: -kv[1]))
        PROF.clear()
    return o


# ---------------------------------------------------------------------------
# Composite builders
# ---------------------------------------------------------------------------


def plateau(a, poly, z, cliff_pred, z0=0.0, seed=0, spacing=3.2, patches=None, fill=True, cliff_kw=None,
            drape_kw=None, zbot_fn=None, rim=None, edge_bushes=0.0):
    """Grass-topped rock mass: the grass sits flush on a ring of full-height
    columns (their bevelled tops just proud of it) and drapes over the edge."""
    H = lambda x, y: z  # noqa: E731
    cap(a, poly, H, spacing=spacing, seed=seed, jz=0.08)
    x0, y0, x1, y1 = poly.bbox()
    if patches is None:
        patches = max(2, int((x1 - x0) * (y1 - y0) / 40))
    grass_patches(a, H, lambda x, y: poly.sdist(x, y) > 0.6, (x0, x1, y0, y1), patches, seed=seed * 3 + 1)
    ledges = []
    kw = dict(cliff_kw or {})
    for arc in poly.arcs(cliff_pred):
        ledges += cliff(a, arc, z0, z + 0.05, zbot_fn=zbot_fn, **kw)
        dk = dict(out=kw.get("out", 0.55) + 0.05)
        dk.update(drape_kw or {})
        drape(a, arc, z, **dk)
        if rim is not None:
            rim_boulders(a, arc, z, **rim)
        if edge_bushes:
            pth = Path2(arc)
            s = a.rng.uniform(1.0, 4.0)
            while s < pth.L - 1.0:
                c, u = pth.at(s), pth.tan(s)
                q = c - Vector((u.y, -u.x)) * a.rng.uniform(1.2, 2.0)
                if poly.sdist(q.x, q.y) > 0.9 and a.rng.random() < edge_bushes:
                    bush(a, q.x, q.y, z, a.rng.uniform(0.8, 1.15))
                s += a.rng.uniform(4.0, 7.0)
    if fill:
        fill_prism(a, poly.offset(-2.3), z0, z - 0.5)
    return ledges


def ledge(a, sc, poly, lz, pred, seed, z0=0.0, bushes=1, tufts=6, rim=None):
    """Grassy ledge on a short group of columns standing proud of a cliff face."""
    led = plateau(a, poly, lz, pred, z0=z0, seed=seed, spacing=2.2, patches=2, rim=rim, fill=False,
                  cliff_kw=dict(depth=3.6, wr=(2.4, 4.6), drop=(0.0, 0.6), sunk=0.0, steps=0.0, bulge=0.45, out=0.5,
                                foot=0.3),
                  drape_kw=dict(drop=(0.2, 0.8)))
    lh = lambda x, y: lz  # noqa: E731
    x0, y0, x1, y1 = poly.bbox()
    sc.many(bushes, lambda x, y: poly.sdist(x, y) > 1.1, lh, lambda x, y, z: bush(a, x, y, z, a.rng.uniform(0.75, 0.95)),
            (x0, x1, y0, y1), r=1.3)
    sc.many(tufts, lambda x, y: poly.sdist(x, y) > 0.4, lh, lambda x, y, z: tuft(a, x, y, z, 1.15),
            (x0, x1, y0, y1), keep=False)
    return led


def ground(a, poly, z=0.35, seed=0, mat=(DIRT, 0.95), patches=6, spacing=3.0, skirt_mat=DIRT):
    """Base apron: tan dirt with grass patches and a low lumpy dirt skirt."""
    H = lambda x, y: z  # noqa: E731
    cap(a, poly, H, mat=mat, spacing=spacing, seed=seed, jz=0.04)
    x0, y0, x1, y1 = poly.bbox()
    grass_patches(a, H, lambda x, y: poly.sdist(x, y) > 0.3, (x0, x1, y0, y1), patches, rad=(1.2, 2.6),
                  seed=seed + 5, light=0.5)
    skirt(a, poly.p, z, 0.0, closed=True, mat=skirt_mat, lumpy=0.25)


def mound_skirt(a, poly, H, seed, mat="earth", zmax=1.2):
    """Low rounded dirt skirt round a mound's outline (no tall slab sides)."""
    skirt(a, poly.p, lambda p: min(H(p.x, p.y), zmax), 0.0, closed=True, mat=mat, lumpy=0.35)


# ---------------------------------------------------------------------------
# Tiles
# ---------------------------------------------------------------------------


def cliff_section():
    """Long cliff: full-height columns, a grassy ledge front-left (~45%) and a low
    step front-right (~20%), big boulders and a dirt skirt at the foot."""
    a = fk.Asset("CliffSection", "Terrain", seed=701)
    sc = Scatter(a)
    TOP, FY, G = 18.0, -5.8, 0.35
    gpoly = organic(box_pts(-16, 16, -10, 10), [5.0, 5.0, 1.0, 1.0], seed=11,
                    tight=lambda p: p.y > 0 or abs(p.x) > 15.7)
    ground(a, gpoly, G, seed=12, patches=7)
    top = organic(box_pts(-16, 16, FY, 10), [4.0, 4.0, 1.0, 1.0], seed=13, wob=1.1,
                  tight=lambda p: p.y > 9.0 or abs(p.x) > 15.6)
    led = plateau(a, top, TOP, lambda p: p.y < 9.2, seed=14, edge_bushes=0.4, cliff_kw=dict(foot=0.4))
    lp1 = organic(box_pts(-16, -3.0, FY - 3.8, FY + 1.6), [3.0, 3.0, 0, 0], seed=21, wob=0.9,
                  tight=lambda p: p.x < -15.5)
    led += ledge(a, sc, lp1, 8.0, lambda p: p.y < FY + 0.6, 21, bushes=2, tufts=8)
    lp2 = organic(box_pts(3.0, 14.5, FY - 3.4, FY + 1.6), [3.0, 3.0, 0, 0], seed=22, wob=0.9)
    led += ledge(a, sc, lp2, 3.6, lambda p: p.y < FY + 0.6, 22, bushes=1, tufts=6)
    ledge_decor(a, led)
    T = lambda x, y: TOP  # noqa: E731
    path(a, [(-9.5, 10.2), (-7.0, 6.5), (-2.5, 5.2), (1.5, 6.4)], 2.0, T, clip=top)
    sc.put(-10.5, 4.0, 2.2, lambda x, y, z: boulder(a, x, y, z, 3.0, 0.9), T)
    sc.put(9.0, -1.5, 2.0, lambda x, y, z: boulder(a, x, y, z, 2.4, 0.85), T)
    for x, y, s in ((-8.0, 8.0, 1.3), (-2.0, 5.0, 1.25), (5.0, 3.0, 1.3), (12.5, 2.0, 1.4), (1.0, -0.6, 1.0),
                    (-12.5, 0.5, 1.1), (7.5, 7.5, 1.1), (-4.5, -1.5, 0.95)):
        sc.put(x, y, 1.6, lambda x, y, z, s=s: bush(a, x, y, z, s), T)
    decorate(a, sc, top, T, pebbles=5, tufts=55, margin=1.0)
    g = lambda x, y: G  # noqa: E731
    for x, y, s in ((8.0, -8.3, 3.4), (12.6, -8.0, 2.8), (15.0, -8.9, 1.8), (-0.5, -8.6, 2.0)):
        sc.put(x, y, 2.0, lambda x, y, z, s=s: boulder(a, x, y, z, s), g)
    for x, y, s in ((1.8, -9.0, 0.8), (-6.0, -9.0, 0.85), (-11.0, -9.1, 0.8), (-14.6, -8.6, 0.75), (5.2, -9.3, 0.7)):
        sc.put(x, y, 1.1, lambda x, y, z, s=s: bush(a, x, y, z, s), g)
    decorate(a, sc, gpoly, g, pebbles=6, tufts=24, margin=0.4, avoid=lambda x, y: y > FY - 3.3)
    return done(a, (-16, 16, -10, 10))


def cliff_outer_corner():
    """Convex corner: full-height columns wrapping the corner, the front corner
    stepped down by low grassy column groups, tree and pine at the back."""
    a = fk.Asset("CliffOuterCorner", "Terrain", seed=702)
    sc = Scatter(a)
    TOP, F, G = 18.0, -10.5, 0.35
    gpoly = organic(box_pts(-16, 16, -16, 16), [8.0, 2.0, 1.0, 2.0], seed=31,
                    tight=lambda p: p.x > 15.6 or p.y > 15.6)
    ground(a, gpoly, G, seed=32, patches=8)
    top = organic(box_pts(F, 16, F, 16), [9.0, 2.0, 1.0, 2.0], seed=33, wob=1.0,
                  tight=lambda p: p.x > 15.5 or p.y > 15.5)
    led = plateau(a, top, TOP, lambda p: p.x < F + 2.5 or p.y < F + 2.5, seed=34, edge_bushes=0.3,
                  cliff_kw=dict(foot=0.2, wr=(3.0, 5.6)))
    steps = (
        (box_pts(-15.4, -6.5, -15.4, -6.5), [3.5, 1.5, 0, 1.5], 9.0, 35, lambda p: p.x < -8.0 or p.y < -8.0),
        (box_pts(-15.8, -10.5, -15.8, -10.5), [2.4, 1.0, 0, 1.0], 4.0, 36, lambda p: p.x < -12.0 or p.y < -12.0),
        (box_pts(-15.2, F + 1.8, -3.0, 7.0), [2.2, 0, 0, 2.2], 7.0, 37, lambda p: p.x < F),
        (box_pts(-15.6, F + 0.8, 7.0, 12.0), [1.6, 0, 0, 1.6], 3.5, 38, lambda p: p.x < F - 1.5),
        (box_pts(-3.0, 5.0, -15.4, F + 1.2), [2.0, 2.0, 0, 0], 4.5, 39, lambda p: p.y < F),
        (box_pts(5.0, 14.6, -15.0, F + 1.8), [2.0, 2.0, 0, 0], 8.5, 40, lambda p: p.y < F),
    )
    polys = [(organic(c, r, seed=sd, wob=0.6), lz, sd, pred) for c, r, lz, sd, pred in steps]
    surfaces = [(top, TOP)] + [(p, lz) for p, lz, _, _ in polys]

    def open_sky(x, y, lz, m=0.9):
        return all(q.sdist(x, y) < -m for q, z in surfaces if z > lz)

    for poly, lz, sd, pred in polys:
        led += plateau(a, poly, lz, pred, seed=sd, spacing=2.2, patches=1, fill=False,
                       cliff_kw=dict(depth=3.0, wr=(3.0, 5.0), drop=(0.0, 0.6), sunk=0.0, steps=0.0, foot=0.12),
                       drape_kw=dict(drop=(0.2, 0.8)))
        lh = lambda x, y, lz=lz: lz  # noqa: E731
        x0, y0, x1, y1 = poly.bbox()
        sc.many(1 if lz > 5 else 2, lambda x, y, poly=poly, lz=lz: poly.sdist(x, y) > 1.0 and open_sky(x, y, lz, 1.2),
                lh, lambda x, y, z: bush(a, x, y, z, a.rng.uniform(0.75, 0.95)), (x0, x1, y0, y1), r=1.2)
        sc.many(5, lambda x, y, poly=poly, lz=lz: poly.sdist(x, y) > 0.4 and open_sky(x, y, lz), lh,
                lambda x, y, z: tuft(a, x, y, z, 1.15), (x0, x1, y0, y1), keep=False)
    led = [(p, z, n) for p, z, n in led if open_sky(p.x, p.y, z + 0.5, 0.3)]
    ledge_decor(a, led)
    T = lambda x, y: TOP  # noqa: E731
    path(a, [(-4.0, 16.3), (-1.0, 9.0), (3.5, 3.5), (9.0, -2.5), (16.3, -5.0)], 2.4, T, clip=top)
    sc.put(-3.5, 10.5, 2.6, lambda x, y, z: broadleaf(a, x, y, z, 1.15), T)
    sc.put(3.5, 12.5, 2.4, lambda x, y, z: pine(a, x, y, z, 1.2), T)
    sc.put(4.0, -4.5, 2.0, lambda x, y, z: boulder(a, x, y, z, 2.6, 0.85), T)
    sc.put(-6.0, 0.0, 1.8, lambda x, y, z: boulder(a, x, y, z, 2.0, 0.8), T)
    for x, y, s in ((-8.0, 7.0, 1.2), (12.0, 11.0, 1.3), (11.5, 1.5, 1.2), (-1.5, -6.5, 1.0), (8.5, 6.0, 1.0)):
        sc.put(x, y, 1.6, lambda x, y, z, s=s: bush(a, x, y, z, s), T)
    decorate(a, sc, top, T, pebbles=3, tufts=18, margin=1.0)
    g = lambda x, y: G  # noqa: E731
    for x, y, s in ((-14.8, 13.8, 2.2), (9.0, -15.0, 2.4), (14.0, -15.0, 1.8)):
        sc.put(x, y, 2.0, lambda x, y, z, s=s: boulder(a, x, y, z, s), g)
    decorate(a, sc, gpoly, g, pebbles=4, tufts=14, margin=0.4, avoid=lambda x, y: x > F - 0.8 and y > F - 0.8)
    return done(a, (-16, 16, -16, 16))


def cliff_inner_corner():
    """High wall at the back-left and right round a bright, wide grass terrace at
    mid height that opens to the front."""
    a = fk.Asset("CliffInnerCorner", "Terrain", seed=703)
    sc = Scatter(a)
    TOP, TZ = 18.0, 10.0
    LX, BY, RX, RY = -9.0, 5.0, 9.5, -3.0
    terr = organic(box_pts(-16, 16, -16, BY + 1.6), [4.0, 4.0, 0, 0], seed=51,
                   tight=lambda p: abs(p.x) > 15.6)
    led = plateau(a, terr, TZ, lambda p: p.y < RY - 0.5 or abs(p.x) > 15.0, seed=52, spacing=2.4, patches=6,
                  cliff_kw=dict(depth=3.2, wr=(2.8, 5.2)))
    hi = organic([(-16, RY), (LX, RY), (LX, BY), (RX, BY), (RX, RY), (16, RY), (16, 16), (-16, 16)],
                 [2.5, 2.5, 3.0, 3.0, 2.5, 1.0, 1.0, 1.0], seed=53,
                 tight=lambda p: p.x < -15.6 or p.y > 15.6 or p.x > 15.6)

    def inner(c):  # wall standing on the terrace
        return c.y < BY + 1.2

    led += plateau(a, hi, TOP, lambda p: p.y < 15.5, seed=54, zbot_fn=lambda c: TZ - 0.4 if inner(c) else 0.0,
                   edge_bushes=0.35)
    ledge_decor(a, led)
    T = lambda x, y: TOP  # noqa: E731
    tz = lambda x, y: TZ  # noqa: E731
    on_terr = lambda x, y: terr.sdist(x, y) > 1.0 and hi.sdist(x, y) < -2.0  # noqa: E731
    path(a, [(-16.3, 11.0), (-9.0, 12.0), (-1.0, 11.0), (6.0, 12.5), (16.3, 11.5)], 2.0, T, clip=hi)
    path(a, [(1.0, -16.3), (1.5, -10.0), (-0.5, -4.0), (1.0, 3.6)], 2.8, tz, clip=terr)
    sc.put(-1.0, 13.5, 2.0, lambda x, y, z: boulder(a, x, y, z, 2.6, 0.85), T)
    for x, y, s in ((-12.0, 12.5, 1.25), (5.0, 14.0, 1.3), (12.5, 12.0, 1.3), (13.0, 3.0, 1.15), (-12.5, 3.0, 1.15),
                    (-12.8, -1.0, 1.0), (12.8, -1.0, 1.0)):
        sc.put(x, y, 1.6, lambda x, y, z, s=s: bush(a, x, y, z, s), T)
    decorate(a, sc, hi, T, pebbles=3, tufts=18, margin=1.0)
    for x, y, s in ((-5.0, 1.5, 2.6), (7.0, -8.0, 2.8)):
        sc.put(x, y, 2.0, lambda x, y, z, s=s: boulder(a, x, y, z, s, 0.9), tz)
    for x, y, s in ((5.0, 2.5, 1.1), (-6.0, -10.0, 1.05), (-11.5, -6.0, 0.95), (11.0, -12.0, 0.95)):
        sc.put(x, y, 1.5, lambda x, y, z, s=s: bush(a, x, y, z, s), tz)
    decorate(a, sc, terr, tz, pebbles=3, tufts=20, margin=1.0, avoid=lambda x, y: not on_terr(x, y))
    return done(a, (-16, 16, -16, 16))


def rock_shelf():
    """Two stepped levels, each edged by a ring of big blocks."""
    a = fk.Asset("RockShelfTwoLevels", "Terrain", seed=704)
    sc = Scatter(a)
    LO, HI = 5.0, 8.5
    low = organic(box_pts(-16, 16, -12, 12), [7.0, 7.0, 1.0, 1.0], seed=61,
                  tight=lambda p: p.y > 11.0 or abs(p.x) > 15.6)
    sk = dict(depth=3.8, wr=(3.6, 6.8), drop=(-0.7, 0.2), lean=0.15, out=0.9, moss=0.4)
    led = plateau(a, low, LO, lambda p: p.y < 11.2, seed=62, cliff_kw=sk,
                  rim=dict(every=(5.0, 8.0), size=(1.6, 2.4), chance=0.5, grassy=0.5))
    up = organic(box_pts(-11.0, 16, 0.5, 12), [5.0, 1.5, 0.0, 0.0], seed=63,
                 tight=lambda p: p.y > 11.0 or p.x > 15.6)
    led += plateau(a, up, HI, lambda p: p.y < 11.2, z0=LO - 0.3, seed=64, cliff_kw=dict(sk, wr=(4.0, 7.0)),
                   rim=dict(every=(3.5, 5.5), size=(2.0, 3.0), chance=0.8, grassy=0.4))
    ledge_decor(a, led, 0.6)
    lo = lambda x, y: LO  # noqa: E731
    hi = lambda x, y: HI  # noqa: E731
    path(a, [(-16.3, -2.0), (-9.0, -4.0), (-2.0, -2.5), (5.0, -5.0), (16.3, -4.0)], 3.0, lo, clip=low)
    path(a, [(-3.0, 12.3), (-1.5, 8.0), (4.0, 6.0), (10.0, 7.0), (16.3, 5.5)], 2.8, hi, clip=up)
    on_low = lambda x, y: up.sdist(x, y) < -2.2  # noqa: E731
    sc.put(11.5, 9.0, 1.8, lambda x, y, z: pine(a, x, y, z, 0.65), hi)
    sc.put(-7.0, 9.5, 2.0, lambda x, y, z: boulder(a, x, y, z, 2.6, 0.85), hi)
    for x, y, s in ((-3.5, 10.0, 1.3), (14.0, 10.5, 1.1), (6.5, 9.5, 1.0)):
        sc.put(x, y, 1.6, lambda x, y, z, s=s: bush(a, x, y, z, s), hi)
    for x, y, s in ((-12.5, -8.0, 1.45), (-10.2, -9.2, 1.1), (-13.6, -5.8, 1.0), (5.5, -9.0, 1.15),
                    (13.0, -2.0, 1.1), (-13.0, 4.5, 1.1), (0.0, -7.8, 1.0), (9.0, -6.5, 0.9)):
        sc.put(x, y, 1.5, lambda x, y, z, s=s: bush(a, x, y, z, s), lo)
    sc.put(-7.5, -0.5, 1.8, lambda x, y, z: boulder(a, x, y, z, 2.2, 0.8), lo)
    decorate(a, sc, up, hi, pebbles=3, tufts=22, margin=1.0)
    decorate(a, sc, low, lo, pebbles=4, tufts=36, margin=1.0, avoid=lambda x, y: not on_low(x, y))
    return done(a, (-16, 16, -12, 12))


def earth_face(a, pts, zt_fn, depth=1.5, wr=(1.0, 2.2), out=0.25):
    """Exposed earth bank along a polyline: warm brown vertical ribs of soil."""
    rng = a.rng
    pth = Path2(pts)
    L = pth.L
    mats = [("earth", 0.95), (DIRT, 0.86), ("earth", 1.05), (DIRT, 0.95), ("earth", 0.88)]
    s = 0.0
    while s < L - 0.05:
        w = min(rng.uniform(*wr), L - s)
        if L - s - w < 0.6:
            w = L - s
        c = pth.at(s + w / 2)
        u = pth.tan(s + w / 2)
        n = Vector((u.y, -u.x))
        zt = min(zt_fn(pth.at(s)), zt_fn(pth.at(s + w)), zt_fn(c)) - 0.15
        s += w
        if zt < 0.35:
            continue
        mt = rng.choice(mats)
        off = out + rng.uniform(-0.25, 0.2)
        cc = c - n * (depth / 2) + n * off
        block(a, cc, u, w * 0.97, depth, zt + 0.1, -0.1, mat=mt[0], top=mt[0], tint=mt[1] * rng.uniform(0.94, 1.06),
              cham=0.25, bulge=0.2)


def grass_ramp():
    """Lumpy grass ramp sloping down to the front-right, a warm earth face on the
    left with grass hanging over it, a smooth wide path and rounded boulders."""
    a = fk.Asset("GrassRamp", "Terrain", seed=705)
    sc = Scatter(a)
    FY = -7.8

    def H(x, y):
        t = max(0.0, min(1.0, (16 - x) / 32)) ** 1.05
        crown = 0.9 * max(0.0, 1 - ((y - 1.0) / 9.5) ** 2) * math.sin(PI * min(1.0, max(0.0, (x + 16) / 32)))
        lumps = 0.25 * math.sin(x * 0.55 + 1.0) * math.sin(y * 0.7)
        return 0.45 + 9.55 * t + crown + lumps * min(1.0, (16 - abs(x)) / 4)

    surf = organic(box_pts(-16, 16, FY, 10), [3.0, 6.0, 6.0, 1.5], seed=71,
                   tight=lambda p: p.x < -15.6 or p.y > 9.6)
    cap(a, surf, H, spacing=1.8, seed=72, jz=0.0)
    grass_patches(a, H, lambda x, y: surf.sdist(x, y) > 0.6, (-16, 16, FY, 10), 12, seed=73)
    face = lambda p: (p.y < FY + 2.5 or p.x < -15.2)  # noqa: E731
    for arc in surf.arcs(face):
        earth_face(a, arc, lambda c: H(c.x, c.y))
        drape(a, arc, lambda p: H(p.x, p.y), out=0.35, drop=(0.4, 1.3))
    for arc in surf.arcs(lambda p: not face(p)):
        skirt(a, arc, lambda p: H(p.x, p.y), 0.0, mat="earth", lumpy=0.2)
    base = organic(box_pts(-16, 16, -10, FY + 2.0), [3.0, 6.0, 0, 0], seed=74, wob=0.6)
    ground(a, base, 0.3, seed=75, patches=4, spacing=2.6)
    path(a, [(-5.0, 10.4), (-2.0, 6.0), (2.5, 2.0), (8.0, -1.5), (13.0, -3.0), (16.4, -3.2)], 7.0, H, clip=surf,
         across=4)
    S = smooth_path([(-5.0, 10.4), (-2.0, 6.0), (2.5, 2.0), (8.0, -1.5), (13.0, -3.0), (16.4, -3.2)], 0.8)
    on_path = lambda x, y: min((p.x - x) ** 2 + (p.y - y) ** 2 for p in S) < 4.6 ** 2  # noqa: E731
    for x, y, s in ((-12.0, 6.5, 2.8), (-0.5, 8.8, 2.4), (13.0, 1.8, 2.2)):
        sc.put(x, y, 2.0, lambda x, y, z, s=s: boulder(a, x, y, z, s, 0.9), H)
    for x, y, s in ((-9.0, 8.0, 1.15), (-13.5, 1.0, 1.0), (-4.0, 1.5, 1.1), (9.5, 4.5, 1.15), (1.5, -4.5, 1.0),
                    (12.5, -6.0, 0.95), (-10.0, -4.5, 0.95), (-7.0, -1.0, 0.9), (5.5, 7.5, 1.0)):
        if not on_path(x, y):
            sc.put(x, y, 1.5, lambda x, y, z, s=s: bush(a, x, y, z, s), H)
    decorate(a, sc, surf, H, pebbles=6, tufts=50, margin=1.0, avoid=on_path)
    g = lambda x, y: 0.3  # noqa: E731
    for x, y, s in ((-9.0, -9.0, 3.2), (4.0, -9.1, 3.4)):
        sc.put(x, y, 2.0, lambda x, y, z, s=s: boulder(a, x, y, z, s, 1.0), g)
    for x, y, s in ((-6.0, -9.3, 0.95), (7.5, -9.3, 0.85), (-12.5, -9.2, 0.8), (-0.5, -9.4, 0.8)):
        sc.put(x, y, 1.1, lambda x, y, z, s=s: bush(a, x, y, z, s), g)
    decorate(a, sc, base, g, pebbles=3, tufts=12, margin=0.4, avoid=lambda x, y: y > FY + 0.5)
    return done(a, (-16, 16, -10, 10))


def earth_switchback():
    """Oval rocky hill: a dirt path climbs three ramped lanes between tapering
    rock tiers to the top, chunky cobbles along its edges, a low dirt skirt."""
    a = fk.Asset("EarthSwitchback", "Terrain", seed=706)
    sc = Scatter(a)
    B0, B1, B2, B3 = 0.6, 5.0, 9.5, 14.0
    lanes = [lambda x: lerpc(x, 12, -11, B0, B1), lambda x: lerpc(x, -12, 11, B1, B2),
             lambda x: lerpc(x, 11, -9, B2, B3), lambda x: B3]
    Y = [-16, -5.0, 3.0, 10.0, 16]
    isl = organic(box_pts(-16, 16, -16, 16), [12.0, 12.0, 6.0, 8.0], seed=81, wob=0.9,
                  tight=lambda p: p.y > 15.4)

    def mound(x, y):
        return 0.5 + max(0.0, isl.sdist(x, y)) * 2.2

    def lane(y):
        for k in range(4):
            if y < Y[k + 1] or k == 3:
                return k

    def Hk(k):
        return lambda x, y: min(lanes[k](x), mound(x, y))

    def H(x, y):
        return Hk(lane(y))(x, y)

    for k in range(4):
        bp = isl.clip(0, 1, -Y[k]).clip(0, -1, Y[k + 1])
        if len(bp) < 3:
            continue
        cap(a, bp, Hk(k), spacing=1.8, seed=82 + k, jz=0.0)
        x0, y0, x1, y1 = bp.bbox()
        grass_patches(a, Hk(k), lambda x, y, bp=bp: bp.sdist(x, y) > 0.5, (x0, x1, y0, y1), 4, seed=90 + k)
    led = []
    for k in range(1, 4):  # tapering rock tiers between the lanes
        y = Y[k]
        xs = [p.x for p in isl.clip(0, 1, -(y - 0.01)).clip(0, -1, y + 0.01).p]
        if not xs:
            continue
        xa, xb = min(xs) + 0.3, max(xs) - 0.3
        lo, hi_ = Hk(k - 1), Hk(k)
        led += cliff(a, [(xa, y), (xb, y)], 0, B3, depth=3.2, wr=(3.0, 5.4), drop=(-0.3, 0.3), out=0.45,
                     ztop_fn=lambda c, f=hi_: f(c.x, c.y + 0.3), zbot_fn=lambda c, f=lo: f(c.x, c.y - 0.5),
                     min_h=0.8, lean=0.12, bulge=0.5, sunk=0.0, moss=0.5)
        drape(a, [(xa, y - 0.05), (xb, y - 0.05)], lambda p, f=hi_: f(p.x, p.y + 0.3), out=0.5, inn=0.3,
              drop=(0.3, 1.0), mask=lambda p, f=hi_, g=lo: f(p.x, p.y + 0.3) - g(p.x, p.y - 0.5) > 0.9)
    skirt(a, isl.p, lambda p: min(H(p.x, p.y), 0.9), 0.0, closed=True, mat="earth", lumpy=0.35)
    ledge_decor(a, led, 0.5)
    pts = [(8.5, -16.4), (9.5, -12.5), (5.0, -10.5), (-4.0, -10.2), (-10.5, -9.0), (-12.8, -5.0), (-10.0, -1.2),
           (-2.0, -1.0), (7.0, -1.0), (11.8, 0.8), (11.5, 5.0), (6.0, 6.6), (-2.0, 6.6), (-8.5, 7.6), (-10.0, 11.5),
           (-8.5, 16.4)]
    path(a, pts, 3.7, H, clip=isl, across=3)
    S = smooth_path(pts, 0.8)
    on_path = lambda x, y: min((p.x - x) ** 2 + (p.y - y) ** 2 for p in S) < 3.6 ** 2  # noqa: E731
    # chunky cobbles along the path edges
    for k in range(3, len(S) - 3, 3):
        p, q = S[k], S[min(k + 1, len(S) - 1)]
        t = (q - p).normalized() if (q - p).length > 1e-6 else Vector((1, 0))
        side = 1 if (k // 3) % 2 else -1
        c = p + Vector((-t.y, t.x)) * side * 2.9
        if isl.sdist(c.x, c.y) > 1.0 and a.rng.random() < 0.7 and not any(abs(c.y - w) < 0.9 for w in Y[1:4]):
            boulder(a, c.x, c.y, H(c.x, c.y), a.rng.uniform(1.1, 1.7), 0.8)
    sc.put(-12.0, -11.0, 2.4, lambda x, y, z: broadleaf(a, x, y, z, 0.9), H)
    sc.put(-12.5, 6.0, 2.0, lambda x, y, z: pine(a, x, y, z, 0.85), H)
    sc.put(12.0, -6.5, 2.0, lambda x, y, z: pine(a, x, y, z, 0.8), H)
    sc.put(9.0, 12.0, 2.0, lambda x, y, z: pine(a, x, y, z, 0.9), H)
    sc.put(1.0, 13.0, 2.2, lambda x, y, z: broadleaf(a, x, y, z, 0.8), H)
    for x, y, s in ((-6.0, -14.0, 1.0), (2.0, -14.5, 0.9), (13.0, -11.0, 0.85), (-5.5, -6.5, 1.0), (4.0, -6.6, 0.9),
                    (-6.5, 1.5, 0.9), (4.0, 1.4, 1.0), (13.0, 8.0, 0.9), (-13.0, 12.0, 0.9), (5.0, 9.0, 0.85),
                    (-4.0, 13.5, 0.9), (-14.0, -2.0, 0.85), (14.2, -1.5, 0.8)):
        if not on_path(x, y):
            sc.put(x, y, 1.4, lambda x, y, z, s=s: bush(a, x, y, z, s), H)
    for x, y, s in ((-1.0, -14.0, 2.2), (9.0, -3.4, 1.9), (-8.0, 4.0, 2.0), (6.0, 12.5, 2.0)):
        if not on_path(x, y):
            sc.put(x, y, 1.6, lambda x, y, z, s=s: boulder(a, x, y, z, s, 0.85), H)
    decorate(a, sc, isl, H, pebbles=6, tufts=44, margin=1.0,
             avoid=lambda x, y: on_path(x, y) or any(abs(y - w) < 1.0 for w in Y[1:4]))
    return done(a, (-16, 16, -16, 16))


def arch_rocks(a, cx, zs, rx, rz, y0, y1, count, thick=(2.0, 3.2), mat=ROCK, lip=0.0):
    """Irregular ring of big chunky rocks framing an elliptical opening."""
    rng = a.rng
    cuts = [0.0] + sorted(rng.uniform(0.12, 0.88) * PI for _ in range(count - 1)) + [PI]
    for k in range(1, len(cuts) - 1):
        cuts[k] = max(cuts[k], cuts[k - 1] + 0.3)
    cuts[-1] = PI
    for a0, a1 in zip(cuts, cuts[1:]):
        if a1 - a0 < 0.12:
            continue
        a0 += 0.02
        a1 -= 0.02
        t = rng.uniform(*thick)
        pts = []
        for yy in (y0 - lip * rng.uniform(0.6, 1.0), y1):
            for ang in (a0, (a0 + a1) / 2, a1):
                pts.append(Vector((cx + rx * math.cos(ang), yy + rng.uniform(-0.1, 0.1), zs + rz * math.sin(ang))))
            for ang, tt in ((a0, t * rng.uniform(0.85, 1.1)), ((a0 + a1) / 2, t * rng.uniform(1.0, 1.25)),
                            (a1, t * rng.uniform(0.85, 1.1))):
                pts.append(Vector((cx + (rx + tt) * math.cos(ang), yy + rng.uniform(-0.2, 0.2),
                                   zs + (rz + tt) * math.sin(ang))))
        hull(a, pts, stone_paint(mat, FAM[mat][0], rng.uniform(0.88, 1.05)), facets=3.0)


def cave_entrance():
    """Rounded rock mass with a tall black arched mouth in a bulbous rock frame,
    standing torches either side, a wide sand apron, boulders and bushes."""
    a = fk.Asset("CaveEntrance", "Terrain", seed=707)
    sc = Scatter(a)
    TOP, FY, OW, ZS, RZ = 18.0, -1.0, 6.6, 3.4, 7.8     # opening 13.2 wide x 11.2 tall
    DEPTH, RT, G = 11.5, 2.8, 0.35
    outer = lambda x: ZS + (RZ + RT) * math.sqrt(max(0.0, 1 - (x / (OW + RT)) ** 2))  # noqa: E731
    gpoly = organic(box_pts(-16, 16, -12, 12), [9.0, 9.0, 3.0, 3.0], seed=101, tight=lambda p: p.y > 6.0)
    ground(a, gpoly, G, seed=102, patches=5)
    # fills kept clear of the mouth, and a black interior
    for sx in (-1, 1):
        a.box((11.0 - OW - 0.7, 10.0 - FY, 17.4), loc=(sx * (11.0 + OW + 0.7) / 2, (FY + 12.0) / 2, 0),
              mat="cliff_rock_dark", base=True)
    a.box((2 * OW + 1.4, 11.0 - FY, 17.4 - (ZS + RZ + 0.8)), loc=(0, (FY + 12.0) / 2, ZS + RZ + 0.8),
          mat="cliff_rock_dark", base=True)
    for sx in (-1, 1):
        v = a.box((0.6, DEPTH, ZS + RZ + 0.6), loc=(sx * (OW - 0.1), FY + DEPTH / 2, 0), mat="charcoal", base=True)
        for vv in v:
            t = (vv.co.y - FY) / DEPTH
            vv.co.x -= sx * 2.0 * max(0.0, t)
        a.bm.normal_update()
        for f in fk._faces_of(v):
            cy = f.calc_center_median().y
            paint(a, [f], ("charcoal", 0.75 if cy < FY + 2.5 else 0.42), 1.0, 0.05)
    a.box((2 * OW - 3.0, 0.6, ZS + RZ + 0.6), loc=(0, FY + DEPTH - 0.3, 0), mat="charcoal", base=True, tint=0.3)
    a.box((2 * OW + 1.0, DEPTH, 0.6), loc=(0, FY + DEPTH / 2, ZS + RZ + 0.2), mat="charcoal", base=True, tint=0.35)
    cap(a, Poly(box_pts(-OW, OW, FY + 0.4, FY + DEPTH - 0.4)), lambda x, y: G, spacing=2.5, seed=103, jz=0.0,
        matfn=lambda x, y, z: (DIRT, 0.55) if y < FY + 1.4 else ("charcoal", 0.3))
    # plateau: grass on top, draped over rounded boulders round the rim
    top = organic(box_pts(-16, 16, FY, 12), [9.0, 9.0, 4.0, 4.0], seed=104, wob=1.2, tight=lambda p: p.y > 11.0)
    mouth = lambda p: abs(p.x) <= OW + RT + 0.6 and p.y < FY + 1.5  # noqa: E731
    led = plateau(a, top, TOP, lambda p: p.y < 11.2 and not mouth(p), seed=105, fill=False,
                  cliff_kw=dict(wr=(3.4, 6.0), bulge=0.6, out=0.6),
                  rim=dict(every=(2.8, 4.5), size=(2.4, 3.4), inset=0.1, chance=0.8, grassy=0.65), edge_bushes=0.5)
    for arc in top.arcs(mouth):
        drape(a, arc, TOP, drop=(0.5, 1.4))
        rim_boulders(a, arc, TOP, every=(2.6, 4.0), size=(2.6, 3.6), inset=0.1, chance=0.9, grassy=0.65)
    cliff(a, [(-OW - RT, FY), (OW + RT, FY)], 0, TOP, zbot_fn=lambda c: outer(c.x) - 0.3, wr=(4.0, 6.0),
          out=0.5, bulge=0.6, moss=0.4)
    arch_rocks(a, 0.0, ZS, OW, RZ, FY - 0.9, FY + 2.8, 6, thick=(RT * 0.8, RT * 1.1), lip=0.4)
    xl, xr = -OW - 0.7, OW + 0.7
    for cx, cy, cz, sx, sy, sz, side in ((-11.0, FY - 0.8, 6.0, 7.0, 5.0, 12.5, -1),
                                         (11.0, FY - 0.6, 5.2, 7.0, 4.6, 10.6, 1),
                                         (-7.0, FY - 0.4, 15.2, 8.0, 4.6, 5.6, 0),
                                         (7.2, FY - 0.3, 14.8, 7.6, 4.4, 6.0, 0)):
        def clip(p, side=side):
            x = min(p.x, xl) if side < 0 else (max(p.x, xr) if side > 0 else p.x)
            z = max(p.z, -0.3)
            if side == 0:
                z = max(z, ZS + RZ + RT - 0.6)
            return Vector((max(-14.8, min(14.8, x)), max(FY - 3.2, p.y), min(z, TOP + 0.4)))
        chunk(a, (cx, cy, cz), (sx, sy, sz), rough=0.1, n=44, clip=clip, exp=0.62)
    ledge_decor(a, led)
    g = lambda x, y: G  # noqa: E731
    ribbon(a, [(0, FY + 0.6), (0.3, FY - 4.0), (-0.4, -12.4)], 20.0, g, mat=("sand", 0.95), lift=0.05,
           wobble=0.14, step=0.5, taper=False, clip=gpoly)
    ribbon(a, [(0, FY + 0.6), (0.3, FY - 4.0), (-0.4, -12.4)], 13.0, g, mat=(DIRT, 1.05), lift=0.08,
           wobble=0.2, step=0.5, taper=False, clip=gpoly)
    torches = [torch_post(a, sx * (OW - 1.4), FY - 0.6, G) for sx in (-1, 1)]
    for k in range(7):
        x, y = a.rng.uniform(-5.5, 5.5), a.rng.uniform(-11.0, FY - 0.5)
        pebble(a, x, y, G, a.rng.uniform(0.5, 0.9))
    for x, y, s in ((-9.6, FY - 4.4, 3.4), (9.4, FY - 4.2, 3.2), (-13.4, FY - 5.0, 2.4), (13.0, FY - 4.8, 2.2),
                    (-6.6, -10.6, 1.8), (7.4, -10.4, 1.6)):
        sc.put(x, y, 1.8, lambda x, y, z, s=s: boulder(a, x, y, z, s), g)
    for x, y, s in ((-14.2, -8.6, 1.1), (4.8, -10.8, 0.9), (13.8, -8.8, 1.05), (-11.0, -11.0, 0.9),
                    (10.5, -11.0, 0.9), (-7.6, -7.0, 0.85), (8.0, -7.6, 0.85), (-1.5, -11.4, 0.7)):
        sc.put(x, y, 1.1, lambda x, y, z, s=s: bush(a, x, y, z, s), g)
    decorate(a, sc, gpoly, g, tufts=18, margin=0.4, avoid=lambda x, y: abs(x) < 6.0 or y > FY - 1.0)
    T = lambda x, y: TOP  # noqa: E731
    sc.put(11.0, 6.0, 2.0, lambda x, y, z: pine(a, x, y, z, 0.95), T)
    for x, y, s in ((-11.0, 7.0, 1.3), (-5.5, 4.0, 1.2), (3.0, 9.0, 1.25), (6.5, 3.0, 1.15), (-1.0, 6.5, 1.0),
                    (-12.0, 2.0, 1.0)):
        sc.put(x, y, 1.6, lambda x, y, z, s=s: bush(a, x, y, z, s), T)
    decorate(a, sc, top, T, pebbles=3, tufts=36, margin=1.4)
    o = done(a, (-16, 16, -12, 12))
    for k, t in enumerate(torches):
        vfx_add(o, "torch_fire", tuple(t), name=f"VFX_torch_fire_{'LR'[k]}")
    vfx_add(o, "heat_glow", (0.0, FY + DEPTH - 3.0, 3.0), scale=1.5)
    return o


def rock_arch():
    """Free-standing rock bridge: two grassy rock masses joined by a thin arched
    bridge; the path runs under it and out the back."""
    a = fk.Asset("RockArch", "Terrain", seed=708)
    sc = Scatter(a)
    TOP, G, AX = 16.0, 0.35, 2.0
    Y0, Y1 = -3.0, 7.0                  # rock masses' depth (the tile centre sits 2.5 in front)
    gpoly = organic(box_pts(-16, 16, -12.5, 7.5), [7.0, 7.0, 6.0, 6.0], seed=111, tight=lambda p: abs(p.x) > 15.6)
    gz = lambda x, y: G  # noqa: E731
    cap(a, gpoly, gz, mat=(DIRT, 0.95), spacing=3.0, seed=112)
    skirt(a, gpoly.p, G, 0.0, closed=True, mat=DIRT, lumpy=0.25)
    grass_patches(a, gz, lambda x, y: gpoly.sdist(x, y) > 0.3 and abs(x - AX + 0.15 * y) > 4.0,
                  (-16, 16, -12.5, 7.5), 18, rad=(1.8, 3.6), lift=0.08, seed=113, light=0.55)
    path(a, [(AX + 2.0, -12.9), (AX + 0.8, -6), (AX, 0), (AX - 0.6, 4.0), (AX - 2.0, 7.9)], 5.6, gz, clip=gpoly)
    led = []
    masses = (organic(box_pts(-16, AX - 6.0, Y0, Y1), [3.5, 4.0, 3.5, 3.0], seed=114, wob=0.8,
                      tight=lambda p: p.x < -15.6),
              organic(box_pts(AX + 6.0, 16, Y0, Y1), [4.0, 3.5, 3.0, 3.5], seed=115, wob=0.8,
                      tight=lambda p: p.x > 15.6))
    for m, sd in zip(masses, (116, 117)):
        led += plateau(a, m, TOP, lambda p: True, seed=sd, cliff_kw=dict(wr=(3.0, 5.6)))
    # the bridge: a thin arched span of rock with a grass deck
    x0, x1 = AX - 7.6, AX + 7.6
    BY0, BY1 = -0.4, 5.4
    zu = lambda x: 2.5 + 7.6 * math.sin(PI * max(0.0, min(1.0, (x - x0) / (x1 - x0)))) ** 0.5  # noqa: E731
    zt = lambda x: TOP - 0.35  # noqa: E731
    x = x0
    while x < x1 - 0.2:
        w = min(a.rng.uniform(1.6, 2.2), x1 - x)
        xc = x + w / 2
        for yy, uu in ((BY0, (1, 0)), (BY1, (-1, 0))):
            n = (uu[1], -uu[0])
            c = (xc - n[0] * 1.1, yy - n[1] * 1.1 - (0 if yy == BY0 else 0))
            block(a, (xc, yy + (1.5 if yy == BY0 else -1.5)), uu, w * 1.2, 3.2, zt(xc) - zu(xc) - 0.1, zu(xc),
                  bulge=0.35)
        x += w
    deck = organic(box_pts(x0 - 0.5, x1 + 0.5, BY0 - 0.2, BY1 + 0.2), 1.0, seed=118, wob=0.4)
    cap(a, deck, lambda x, y: zt(x) + 0.1, spacing=1.6, seed=119, jz=0.0)
    drape(a, [(x0, BY0 - 0.2), (x1, BY0 - 0.2)], lambda p: zt(p.x) + 0.1, out=0.35, drop=(0.3, 1.0))
    drape(a, [(x1, BY1 + 0.2), (x0, BY1 + 0.2)], lambda p: zt(p.x) + 0.1, out=0.35, drop=(0.3, 1.0))
    for k in range(4):
        tuft(a, a.rng.uniform(x0 + 1, x1 - 1), a.rng.uniform(BY0 + 0.6, BY1 - 0.6), zt(AX) + 0.1, 1.1)
    bush(a, AX - 2.5, 2.4, zt(AX - 2.5) + 0.05, 0.75)
    ledge_decor(a, led)
    T = lambda x, y: TOP  # noqa: E731
    sc.put(-11.0, 2.5, 2.0, lambda x, y, z: pine(a, x, y, z, 1.0), T)
    sc.put(-5.5, 2.8, 2.4, lambda x, y, z: broadleaf(a, x, y, z, 0.9), T)
    sc.put(12.5, 3.5, 2.2, lambda x, y, z: boulder(a, x, y, z, 3.4, 1.05), T)
    for x, y, s in ((-14.2, 0.5, 1.0), (-8.0, 5.5, 1.0), (9.5, 0.5, 1.0), (14.0, 6.0, 0.9)):
        sc.put(x, y, 1.4, lambda x, y, z, s=s: bush(a, x, y, z, s), T)
    for m in masses:
        decorate(a, sc, m, T, pebbles=2, tufts=12, margin=1.2)
    for x, y, s in ((-13.0, -8.4, 3.0), (-8.0, -9.4, 2.2), (AX + 7.8, -8.6, 2.6), (13.0, -9.2, 2.0),
                    (-3.0, -11.0, 1.4), (AX + 4.4, -11.2, 1.2), (-11.0, 6.0, 2.0), (12.0, 6.0, 1.8)):
        sc.put(x, y, 1.6, lambda x, y, z, s=s: boulder(a, x, y, z, s), gz)
    sc.put(AX - 6.0, -7.8, 1.5, lambda x, y, z: pine(a, x, y, z, 0.6), gz)
    sc.put(AX + 6.5, -10.4, 1.5, lambda x, y, z: pine(a, x, y, z, 0.55), gz)
    for x, y, s in ((-15.0, -8.8, 0.9), (-10.5, -11.0, 0.95), (AX + 10.5, -10.6, 0.9), (14.8, -6.5, 0.9),
                    (-6.0, -11.5, 0.8), (-6.0, 6.8, 0.8), (AX + 8.0, 7.0, 0.8), (-14.5, -4.6, 0.8)):
        sc.put(x, y, 1.2, lambda x, y, z, s=s: bush(a, x, y, z, s), gz)
    decorate(a, sc, gpoly, gz, pebbles=6, tufts=30, margin=0.5,
             avoid=lambda x, y: abs(x - AX + 0.15 * y) < 3.4 or (Y0 - 0.8 < y < Y1 + 0.8 and abs(x - AX) > 7))
    return done(a, (-16, 16, -12.5, 7.5))


def water_bands(a, shore, side, WZ, clip, widths=((14.0, 16.0, "water_deep"), (1.7, 0.85, "water_shallow")), foam=0.7):
    """Saturated blue from the shore, a light shallow band hugging it and a soft
    white foam edge. `side` is +1 when the water lies to the right of `shore`."""
    def off(d):
        P = resample(shore, 0.8)
        out = []
        for k, p in enumerate(P):
            t = (P[min(k + 1, len(P) - 1)] - P[max(k - 1, 0)]).normalized()
            n = Vector((t.y, -t.x)) * side
            q = p + n * d
            if clip.sdist(q.x, q.y) > 0.15:
                out.append(q)
        return out

    for w, d, m in widths:
        ribbon(a, off(d), w, lambda x, y: WZ, mat=m, lift=0.03 if m == "water_deep" else 0.045, taper=False,
               wobble=0.1, smooth=False, clip=clip)
    ribbon(a, off(0.05), foam, lambda x, y: WZ, mat="foam", lift=0.07, taper=False, wobble=0.35, clip=clip)


def water_surface(a, poly, WZ, seed, depth=0.4):
    """Organic water body: deep blue base with a thin edge (no slab)."""
    cap(a, poly, lambda x, y: WZ, mat="water", spacing=3.0, jz=0.0, seed=seed, var=0.01)
    skirt(a, poly.p, WZ, WZ - depth, closed=True, mat="water_deep", tint=0.9, var=0.01)


def along(f, step=0.7):
    def curve(p0, p1):
        n = max(1, int(abs(p1.x - p0.x) / step))
        return [Vector((p0.x + (p1.x - p0.x) * k / n, f(p0.x + (p1.x - p0.x) * k / n))) for k in range(1, n)]
    return curve


def around(C, rfn, step=0.7):
    def curve(p0, p1):
        a0 = math.atan2(p0.y - C.y, p0.x - C.x)
        a1 = math.atan2(p1.y - C.y, p1.x - C.x)
        da = (a1 - a0 + PI) % (2 * PI) - PI
        r = rfn(a0)
        n = max(1, int(abs(da) * r / step))
        return [C + Vector((math.cos(a0 + da * k / n), math.sin(a0 + da * k / n))) * rfn(a0 + da * k / n)
                for k in range(1, n)]
    return curve


def riverbank():
    a = fk.Asset("Riverbank", "Terrain", seed=709)
    sc = Scatter(a)
    WZ, SAND_TOP, GZ, BAND = 2.1, 2.7, 3.3, 4.6

    def ys(x):  # curved shoreline, same y at both tile edges
        return 0.0 - 3.6 * math.sin(PI * x / 16) * (1 - 0.15 * math.cos(PI * x / 16))

    def Hs(x, y):
        d = y - ys(x)
        return 1.4 + max(0.0, min(1.0, (d + 1.5) / (BAND + 1.5))) * (SAND_TOP - 1.4)

    dw = (WZ - 1.4) / (SAND_TOP - 1.4) * (BAND + 1.5) - 1.5
    edge = lambda x: ys(x) + BAND + 0.4 + 0.4 * math.sin(x * 0.9) + 0.25 * math.sin(x * 2.3)  # noqa: E731
    foot = organic(box_pts(-16, 16, -12, 12), [9.0, 6.0, 1.0, 1.0], seed=121,
                   tight=lambda p: abs(p.x) > 15.6 or p.y > 11)
    water_poly = foot.clip_fn(lambda p: ys(p.x) + dw + 0.5 - p.y, along(lambda x: ys(x) + dw + 0.5))
    water_surface(a, water_poly, WZ, seed=122)
    sand = foot.clip_fn(lambda p: p.y - (ys(p.x) - 1.6), along(lambda x: ys(x) - 1.6))
    sand = sand.clip_fn(lambda p: edge(p.x) + 0.8 - p.y, along(lambda x: edge(x) + 0.8))
    cap(a, sand, Hs, mat=("sand", 1.0), spacing=1.8, seed=123, jz=0.03)
    bank = foot.clip_fn(lambda p: p.y - edge(p.x), along(edge))

    def gh(x, y):  # bank rising into a rounded mound inland, back to GZ at the joining edges
        rise = min(1.0, max(0.0, (y - edge(x)) / 4.0))
        mnd = 1.6 * math.sin(PI * (x + 16) / 32) * min(1.0, max(0.0, (y - edge(x)) / 5.0)) \
            * min(1.0, max(0.0, (12 - y) / 4.0))
        return Hs(x, edge(x)) + (GZ - Hs(x, edge(x))) * rise + mnd

    cap(a, bank, gh, spacing=2.0, seed=124, jz=0.0)
    grass_patches(a, gh, lambda x, y: bank.sdist(x, y) > 0.5, (-16, 16, -6, 12), 8, seed=125)
    face = sorted([p for p in bank.p if abs(p.y - edge(p.x)) < 0.05 and foot.sdist(p.x, p.y) > 0.25],
                  key=lambda p: p.x)
    drape(a, face, lambda p: gh(p.x, p.y + 0.2), out=0.3, inn=0.4, drop=(0.2, 0.6))
    rim_boulders(a, face, SAND_TOP, every=(3.0, 5.0), size=(1.2, 2.0), inset=-0.3, chance=0.6, grassy=0.3)

    def edge_z(p):
        if p.y > edge(p.x) - 0.1:
            return gh(p.x, p.y)
        return max(Hs(p.x, p.y), WZ) if p.y > ys(p.x) - 1.6 else WZ

    for arc in foot.arcs(lambda p: p.y > ys(p.x) + dw - 0.3):
        skirt(a, arc, edge_z, WZ - 0.6, mat="earth", lumpy=0.3)
    water_bands(a, [(x / 2, ys(x / 2) + dw) for x in range(-34, 35)], 1, WZ, water_poly,
                widths=((1.7, 0.85, "water_shallow"),))
    deep = water_poly.clip_fn(lambda p: ys(p.x) + dw - 8.5 - p.y, along(lambda x: ys(x) + dw - 8.5))
    if len(deep) > 2:
        cap(a, deep, lambda x, y: WZ + 0.02, mat="water_deep", spacing=3.0, jz=0.0, seed=126, var=0.01)
    rr = random.Random(909)
    for k in range(17):
        x = -14.5 + k * 29.0 / 16 + rr.uniform(-0.6, 0.6)
        o = rr.uniform(-2.2, 1.6) if k % 3 else rr.uniform(-4.5, -2.5)
        s = rr.uniform(1.4, 2.6) if k % 4 else rr.uniform(2.4, 3.2)
        y = ys(x) + dw + o
        if foot.sdist(x, y) < 1.0:
            continue
        z = Hs(x, y)
        shore_rock(a, x, y, min(z, WZ - 0.3), s * 1.05)
        if z < WZ + 0.3:
            a.torus(s * 0.55, 0.13, loc=(x, y, WZ + 0.06), seg=8, rseg=3, mat="foam", squash=0.4)
        sc.add(x, y, s * 0.6)
    sc.put(-12.0, 9.6, 2.0, lambda x, y, z: pine(a, x, y, z, 1.0), gh)
    sc.put(-3.0, 9.5, 2.2, lambda x, y, z: broadleaf(a, x, y, z, 1.0), gh)
    for x, y, s in ((-8.0, 7.0, 2.4), (7.5, 9.0, 2.2)):
        sc.put(x, y, 1.8, lambda x, y, z, s=s: boulder(a, x, y, z, s, 0.9), gh)
    on_bank = lambda x, y: y - edge(x) > 1.4  # noqa: E731
    for x, y, s in ((2.5, 7.5, 1.1), (12.0, 7.0, 1.0), (-14.5, 5.5, 0.95), (5.5, 10.5, 0.9), (-7.0, 10.5, 0.9),
                    (10.0, 3.5, 0.9), (14.5, 2.0, 0.85), (0.0, 4.5, 0.9), (-10.0, 6.5, 0.85), (8.0, 11.0, 0.85),
                    (-14.0, 10.5, 0.85)):
        if on_bank(x, y):
            sc.put(x, y, 1.3, lambda x, y, z, s=s: bush(a, x, y, z, s), gh)
    decorate(a, sc, bank, gh, pebbles=3, tufts=40, margin=0.8, avoid=lambda x, y: not on_bank(x, y))
    decorate(a, sc, sand, Hs, pebbles=6, margin=0.6, avoid=lambda x, y: y < ys(x) + dw + 0.5)
    o = done(a, (-16, 16, -12, 12))
    for x in (-9.0, 1.0, 11.0):
        vfx_add(o, "water_foam", (x, ys(x) + dw, WZ + 0.05), name=f"VFX_water_foam_{x:+.0f}")
    return o


def rocky_lakeshore():
    """Concave bay: water filling the front-left, a narrow sand strip hugging it,
    tall columnar rocks spread round the bay and onto the grass."""
    a = fk.Asset("RockyLakeshore", "Terrain", seed=710)
    sc = Scatter(a)
    WZ, GZ = 2.0, 3.3
    C, R = Vector((-5.0, -7.0)), 13.5

    def s_of(x, y):
        return (Vector((x, y)) - C).length - R

    def Hs(x, y):
        return 1.4 + max(0.0, min(1.0, (s_of(x, y) + 1.5) / 4.5)) * 1.6

    sw = 0.6 / 1.6 * 4.5 - 1.5
    bw = lambda t: 2.8 + 0.4 * math.sin(7 * t) + 0.25 * math.sin(17 * t)  # noqa: E731
    ang = lambda p: math.atan2(p.y - C.y, p.x - C.x)  # noqa: E731
    foot = organic(box_pts(-16, 16, -14, 14), [8.0, 5.0, 2.5, 4.0], seed=131,
                   tight=lambda p: p.y > 13.6)
    water_poly = foot.clip_fn(lambda p: sw + 0.5 - s_of(p.x, p.y), around(C, lambda t: R + sw + 0.5))
    water_surface(a, water_poly, WZ, seed=132)
    sand = foot.clip_fn(lambda p: s_of(p.x, p.y) + 1.6, around(C, lambda t: R - 1.6))
    sand = sand.clip_fn(lambda p: bw(ang(p)) + 0.8 - s_of(p.x, p.y), around(C, lambda t: R + bw(t) + 0.8))
    cap(a, sand, Hs, mat=("sand", 1.0), spacing=1.6, seed=133, jz=0.03)
    bank = foot.clip_fn(lambda p: s_of(p.x, p.y) - bw(ang(p)), around(C, lambda t: R + bw(t)))

    def gh(x, y):  # grass mound rising behind the beach, easing down at the outer edges
        s = s_of(x, y)
        rise = min(1.0, max(0.0, (s - bw(ang(Vector((x, y))))) / 3.0))
        base = 3.0 + (GZ + 1.2 - 3.0) * rise
        edge = min(1.0, max(0.0, foot.sdist(x, y) / 4.0))
        return 2.3 + (base - 2.3) * (0.35 + 0.65 * edge) if y < 13 else base

    cap(a, bank, gh, spacing=2.0, seed=134, jz=0.0)
    grass_patches(a, gh, lambda x, y: bank.sdist(x, y) > 0.5, (-16, 16, -14, 14), 7, seed=135)
    face = [p for p in bank.p if abs(s_of(p.x, p.y) - bw(ang(p))) < 0.05 and foot.sdist(p.x, p.y) > 0.25]
    face.sort(key=ang, reverse=True)
    drape(a, face, lambda p: gh(p.x, p.y), out=0.3, inn=0.4, drop=(0.2, 0.6))

    def edge_z(p):
        s = s_of(p.x, p.y)
        if s > bw(ang(p)) - 0.1:
            return gh(p.x, p.y)
        return max(Hs(p.x, p.y), WZ)

    for arc in foot.arcs(lambda p: s_of(p.x, p.y) > sw - 0.3):
        skirt(a, arc, edge_z, WZ - 0.6, mat="earth", lumpy=0.3)
    shore = [C + Vector((math.cos(t), math.sin(t))) * (R + sw) for t in [2.4 - 3.3 * k / 90 for k in range(91)]]
    water_bands(a, shore, 1, WZ, water_poly, widths=((1.7, 0.85, "water_shallow"),))
    deep = Poly([water_poly.pull_inside(p.x, p.y, 1.5) for p in blob_poly(C.x, C.y, R - 6.0, seed=136, seg=30).p])
    cap(a, deep, lambda x, y: WZ + 0.02, mat="water_deep", spacing=3.0, jz=0.0, seed=137, var=0.01)
    rr = random.Random(1010)

    def P(t, s):
        return C + Vector((math.cos(t), math.sin(t))) * (R + s)

    # tall columnar rock blocks round the bay and up onto the grass
    for k in range(14):
        t = -0.55 + 2.75 * k / 13 + rr.uniform(-0.05, 0.05)
        s = rr.uniform(2.2, 4.8) if k % 3 else rr.uniform(5.5, 9.0)
        p = P(t, s)
        if foot.sdist(p.x, p.y) < 2.0:
            continue
        w = rr.uniform(2.6, 4.2)
        h = rr.uniform(3.8, 6.8) if k % 2 else rr.uniform(2.6, 4.0)
        u = (math.sin(t), -math.cos(t))
        z = (Hs(p.x, p.y) if s < 3.4 else gh(p.x, p.y)) - 0.5
        block(a, (p.x, p.y), u, w, w * rr.uniform(0.8, 1.0), h, z,
              top=(GRASS, 0.95) if rr.random() < 0.35 else "cliff_rock_light", bulge=0.45)
        sc.add(p.x, p.y, w * 0.6)
    for k in range(11):
        t = -0.5 + 2.6 * k / 10 + rr.uniform(-0.04, 0.04)
        s = rr.uniform(1.4, 2.6)
        p = P(t, sw + rr.uniform(-2.4, 1.0))
        if foot.sdist(p.x, p.y) < 1.2:
            continue
        z = Hs(p.x, p.y)
        shore_rock(a, p.x, p.y, min(z, WZ - 0.3), s)
        if z < WZ + 0.3:
            a.torus(s * 0.55, 0.13, loc=(p.x, p.y, WZ + 0.06), seg=8, rseg=3, mat="foam", squash=0.4)
        sc.add(p.x, p.y, s * 0.5)
    for t, o, s in ((0.3, -4.0, 2.0), (1.1, -5.0, 1.8), (1.9, -3.5, 1.9)):
        p = P(t, o)
        if water_poly.sdist(p.x, p.y) > 1.2:
            shore_rock(a, p.x, p.y, WZ - 0.4, s)
            a.torus(s * 0.55, 0.13, loc=(p.x, p.y, WZ + 0.06), seg=8, rseg=3, mat="foam", squash=0.4)
    sc.put(8.0, 10.0, 2.4, lambda x, y, z: broadleaf(a, x, y, z, 1.0), gh)
    sc.put(12.5, 11.5, 2.0, lambda x, y, z: pine(a, x, y, z, 1.05), gh)
    on_bank = lambda x, y: s_of(x, y) > bw(ang(Vector((x, y)))) + 1.4  # noqa: E731
    decorate(a, sc, bank, gh, bushes=10, pebbles=3, tufts=40, margin=0.9, avoid=lambda x, y: not on_bank(x, y))
    decorate(a, sc, sand, Hs, pebbles=6, margin=0.6, avoid=lambda x, y: s_of(x, y) < sw + 0.5)
    o = done(a, (-16, 16, -14, 14))
    for k, t in enumerate((0.0, 0.9, 1.8)):
        p = P(t, sw)
        vfx_add(o, "water_foam", (p.x, p.y, WZ + 0.05), name=f"VFX_water_foam_{k + 1}")
    return o


def waterfall_cliff():
    """Two cliff halves either side of a wide curved fall, a stream across the
    top, a big round pool filling the front with rocks round it."""
    a = fk.Asset("WaterfallCliff", "Terrain", seed=711)
    sc = Scatter(a)
    TOP, FY, CW, PZ, GZ = 20.0, 4.0, 4.4, 1.8, 2.5
    AX = -1.0
    WZ = TOP - 0.6
    foot = organic(box_pts(-16, 16, -14, 14), [9.0, 9.0, 6.0, 6.0], seed=141, wob=0.8, tight=lambda p: p.y > 13.4)
    cx, cy, rx, ry = AX + 0.8, -5.6, 14.0, 7.7
    pool = blob_poly(cx, cy, 1.0, seed=142, seg=40, amp=(0.06, 0.04), sx=rx, sy=ry)
    pool = Poly([foot.pull_inside(p.x, p.y, 0.6) for p in pool.p])
    gp = Poly(foot.clip(0, -1, FY + 0.8).p)
    cap(a, gp, lambda x, y: GZ, spacing=2.6, holes=(pool,), seed=143)
    grass_patches(a, lambda x, y: GZ, lambda x, y: gp.sdist(x, y) > 0.4 and pool.sdist(x, y) < -0.5,
                  (-16, 16, -14, FY), 6, seed=144)
    for arc in foot.arcs(lambda p: p.y < FY + 1.0):
        skirt(a, arc, GZ, 0.0, mat="earth", lumpy=0.3)
    skirt(a, list(reversed(pool.p)), GZ, PZ - 0.1, closed=True, mat="earth")
    cap(a, pool, lambda x, y: PZ, mat="water_deep", spacing=2.8, jz=0.0, seed=145, var=0.015)
    for k, wd, mt, lf in ((0.7, 4.6, "water", 0.03), (0.93, 1.1, "water_shallow", 0.045)):
        ring = blob_poly(cx, cy, k, seed=142, seg=40, amp=(0.06, 0.04), sx=rx, sy=ry)
        pts = [(p.x, p.y) for p in ring.p] + [(ring.p[0].x, ring.p[0].y)]
        ribbon(a, pts, wd, lambda x, y: PZ, mat=mt, lift=lf, taper=False, wobble=0.1, smooth=False, clip=pool)
    rim = [(p.x, p.y) for p in pool.offset(-0.35).p]
    ribbon(a, rim + rim[:1], 0.6, lambda x, y: PZ, mat="foam", lift=0.07, taper=False, wobble=0.35, clip=pool)
    # the two cliff halves
    halves = (organic([(-16, FY), (AX - CW, FY), (AX - CW, 14), (-16, 14)], [7.0, 1.0, 0.0, 6.0], seed=146,
                      wob=0.7, inset=0.9, tight=lambda p: p.y > 13.4 or p.x > AX - CW - 0.4),
              organic([(AX + CW, FY), (16, FY), (16, 14), (AX + CW, 14)], [1.0, 7.0, 6.0, 0.0], seed=147,
                      wob=0.7, inset=0.9, tight=lambda p: p.y > 13.4 or p.x < AX + CW + 0.4))
    led = []
    for hp, sd in zip(halves, (148, 149)):
        led += plateau(a, hp, TOP, lambda p: p.y < 13.3 and abs(p.x - AX) > CW + 0.3, seed=sd,
                       edge_bushes=0.6, cliff_kw=dict(foot=0.3))
        for arc in hp.arcs(lambda p: abs(p.x - AX) <= CW + 0.3 and p.y > FY + 1.2):
            cliff(a, arc, WZ - 1.6, TOP + 0.05, depth=1.8, wr=(2.4, 3.6), out=0.2, moss=0.3, steps=0.0, sunk=0.0)
            drape(a, arc, TOP, out=0.25, drop=(0.3, 0.8))
    cliff(a, [(AX - CW - 0.5, FY + 1.0), (AX + CW + 0.5, FY + 1.0)], 0, TOP - 1.6, depth=2.0, mat=ROCK,
          top="cliff_rock_dark", moss=0.2)
    # stream channel across the top
    v = a.box((2 * CW + 0.4, 14 - FY + 0.3, 1.4), loc=(AX, (14 + FY - 0.3) / 2, WZ - 1.4), mat="water", base=True)
    a.bm.normal_update()
    for f in fk._faces_of(v):
        paint(a, [f], "water" if f.normal.z > 0.5 else "water_deep", 1.0, 0.01)
    ribbon(a, [(AX + 0.6, 14), (AX + 1.0, 9), (AX - 0.4, 4), (AX, FY - 0.2)], 2.4, lambda x, y: WZ,
           mat="water_shallow", lift=0.02, taper=False, wobble=0.25)
    for x, y, s in ((AX - CW + 0.6, 11.5, 1.8), (AX + CW - 0.5, 8.5, 2.0), (AX - CW + 0.4, 5.6, 1.6),
                    (AX + CW - 0.6, FY + 0.6, 2.0), (AX - 3.0, 13.2, 2.6), (AX + 3.4, 13.0, 2.4)):
        boulder(a, x, y, WZ - 0.6, s)
        a.torus(s * 0.5, 0.11, loc=(x, y, WZ + 0.05), seg=8, rseg=3, mat="foam", squash=0.4)
    # the falls: a smooth curved sheet, white at the lip and base, blue-white between
    bm = a.bm
    rr = random.Random(1111)
    nx, nz = 18, 14
    noise = [[rr.random() for _ in range(nx)] for _ in range(3)]
    for layer, (dy, wide_k) in enumerate(((0.0, 1.0),)):
        rows = []
        for j in range(nz + 1):
            t = j / nz
            y = FY - 0.3 - 1.1 * math.sin(min(1.0, t * 3.5) * PI / 2) - 1.6 * t * t + dy
            z = WZ + 0.15 - t * (WZ - PZ)
            wide = CW * wide_k * (1.0 + 0.2 * t)
            rows.append([bm.verts.new((AX - wide + 2 * wide * i / nx,
                                       y - 1.3 * math.sin(PI * i / nx), z)) for i in range(nx + 1)])
        for j in range(nz):
            t = j / nz
            for i in range(nx):
                band = 0.7 * noise[0][i] + 0.3 * noise[1][(i + 1) % nx]  # vertical streaks
                white = t < 0.07 or t > 0.78 or band < 0.22 + 0.3 * t * t
                if layer == 1 and not (white and rr.random() < 0.55):
                    continue
                mt = ("foam", 1.0) if white else (("water", 1.0) if band > 0.82 else ("water_shallow", 1.08))
                f = bm.faces.new((rows[j + 1][i], rows[j + 1][i + 1], rows[j][i + 1], rows[j][i]))
                paint(a, [f], mt, 1.0, 0.03)
    for k in range(20):  # foam burst at the foot of the fall
        ang = a.rng.uniform(0, 2 * PI)
        r2 = a.rng.uniform(0, 1.0) ** 0.6 * 4.6
        a.ico(a.rng.uniform(0.7, 1.7), loc=(AX + math.cos(ang) * r2 * 1.35, FY - 3.4 + math.sin(ang) * r2 * 0.65,
                                            PZ + a.rng.uniform(0.0, 0.8)),
              subdiv=1, jitter=0.12, mat=a.rng.choice(["foam", "foam", "foam", "water_shallow"]),
              face_tint_var=0.03)
    # mid ledges: pines on the left one, a bush on the right
    LY = FY - 3.6
    for (lx0, lx1, lz, sd) in ((-15.6, AX - CW - 1.4, 8.0, 150), (AX + CW + 2.0, 15.4, 6.0, 151)):
        lp = organic(box_pts(lx0, lx1, LY, FY + 1.4), [3.0, 2.0, 0, 0] if lx0 < 0 else [2.0, 3.0, 0, 0], seed=sd,
                     wob=0.5)
        lp = Poly([foot.pull_inside(p.x, p.y, 0.1) for p in lp.p])
        led += ledge(a, sc, lp, lz, lambda p: p.y < FY + 0.4, sd, z0=GZ - 0.4, bushes=1, tufts=6)
    ledge_decor(a, led)
    sc.put(-10.2, LY + 2.0, 1.4, lambda x, y, z: pine(a, x, y, z, 0.8), lambda x, y: 8.0)
    sc.put(-7.2, LY + 2.8, 1.2, lambda x, y, z: pine(a, x, y, z, 0.65), lambda x, y: 8.0)
    sc.put(9.0, LY + 2.2, 1.2, lambda x, y, z: pine(a, x, y, z, 0.6), lambda x, y: 6.0)
    for x, y, s in ((-13.2, -5.6, 3.2), (13.0, -4.2, 3.4), (-12.6, -10.6, 3.4), (12.8, -10.0, 2.8),
                    (5.2, -12.6, 2.8), (-5.5, -12.8, 2.4), (8.2, -2.2, 2.2), (-1.0, -13.4, 1.8)):
        sc.put(x, y, 1.6, lambda x, y, z, s=s: boulder(a, x, y, z, s), lambda x, y: PZ - 0.2)
    for x, y in ((14.4, -1.6), (-14.6, -2.2), (14.6, -12.0), (-9.0, -13.2), (2.0, -13.6)):
        sc.put(x, y, 1.1, lambda x, y, z: bush(a, x, y, z, 0.85), lambda x, y: GZ)
    decorate(a, sc, gp, lambda x, y: GZ, tufts=14, margin=0.4, avoid=lambda x, y: pool.sdist(x, y) > -0.8)
    T = lambda x, y: TOP  # noqa: E731
    sc.put(-9.0, 10.0, 2.0, lambda x, y, z: pine(a, x, y, z, 0.8), T)
    sc.put(9.5, 10.0, 2.0, lambda x, y, z: pine(a, x, y, z, 0.75), T)
    for hp in halves:
        decorate(a, sc, hp, T, bushes=2, boulders=1, pebbles=2, tufts=12, margin=1.2, rs=(1.8, 2.6))
    o = done(a, (-16, 16, -14, 14))
    vfx_add(o, "waterfall_mist", (AX, FY - 3.4, PZ + 0.4), scale=1.4)
    vfx_add(o, "water_foam", (cx + 0.6 * rx, cy - 0.55 * ry, PZ + 0.05), name="VFX_water_foam_A")
    vfx_add(o, "water_foam", (cx - 0.7 * rx, cy - 0.4 * ry, PZ + 0.05), name="VFX_water_foam_B")
    return o


def forest_floor():
    """Rounded patch of forest floor: a tan dirt clearing, two root-flared stumps,
    a big rounded boulder, ferns and bushes, a low lumpy dirt skirt."""
    a = fk.Asset("ForestFloor", "Terrain", seed=712)
    sc = Scatter(a)
    TZ = 3.0

    def H(x, y):
        return TZ + 0.35 * math.sin(PI * (x + 16) / 32) * math.sin(PI * (y + 16) / 32) \
            + 0.12 * math.sin(x * 0.8) * math.sin(y * 0.7)

    isl = organic(box_pts(-16, 16, -16, 16), [6.0, 5.0, 6.0, 5.0], seed=161, inset=0.2, wob=0.9)
    cap(a, isl, H, spacing=2.2, seed=162, jz=0.0)
    grass_patches(a, H, lambda x, y: isl.sdist(x, y) > 0.5, (-16, 16, -16, 16), 10, seed=163)
    clearing = blob_poly(-0.5, 0.5, 9.2, seed=164, seg=28, amp=(0.18, 0.1), sx=1.05, sy=0.95)
    side = blob_poly(-9.0, -9.5, 3.4, seed=165, seg=16)
    for k, cp in enumerate((clearing, side)):
        cap(a, cp, lambda x, y: H(x, y) + 0.1, mat=(DIRT, 1.0), spacing=2.6, jz=0.0, seed=166 + k)
        inner = cp.offset(-1.3)
        cap(a, inner, lambda x, y: H(x, y) + 0.13, mat=(DIRT, 1.12), spacing=2.6, jz=0.0, seed=168 + k)
    skirt(a, isl.p, lambda p: H(p.x, p.y), 0.0, closed=True, mat="earth", lumpy=0.45)
    rng = a.rng
    for k, p in enumerate(isl.resample(2.6).p):  # rounded clods of soil along the base
        if rng.random() < 0.55:
            n = isl.normals()[min(k, len(isl.p) - 1)] if False else None
            q = p * (1 - 0.01)
            chunk(a, (q.x, q.y, rng.uniform(0.4, 1.0)), (rng.uniform(1.4, 2.4), 1.2, rng.uniform(1.0, 1.8)),
                  rough=0.12, n=18, exp=0.65, mat=rng.choice(["earth", DIRT]), top=rng.choice(["earth", DIRT]),
                  clip=lambda v: Vector((v.x, v.y, max(v.z, 0.0))))
    drape(a, isl.p + [isl.p[0]], lambda p: H(p.x, p.y), out=0.3, inn=0.5, drop=(0.3, 1.0))
    sc.put(-7.0, 8.0, 3.4, lambda x, y, z: stump(a, x, y, z, 2.2, 6.0), H)
    sc.put(10.0, 6.5, 3.0, lambda x, y, z: stump(a, x, y, z, 1.8, 4.4), H)
    sc.put(5.0, -5.5, 3.0, lambda x, y, z: boulder(a, x, y, z, 5.4, 1.05, round_=0.62), H)
    for x, y, s in ((-12.0, -3.0, 1.6), (0.5, 12.0, 1.8), (3.0, -13.0, 1.6), (-3.0, -4.0, 1.2), (13.0, -3.0, 1.4),
                    (8.0, -9.5, 1.6)):
        sc.put(x, y, 1.0, lambda x, y, z, s=s: boulder(a, x, y, z, s, 0.8), H)
    in_clear = lambda x, y: clearing.sdist(x, y) > -0.3 or side.sdist(x, y) > -0.3  # noqa: E731
    for x, y, s in ((-12.5, 1.0, 1.25), (-3.0, 13.0, 1.2), (12.5, -12.0, 1.15), (13.5, 11.5, 1.2),
                    (-13.0, -12.5, 1.1), (1.0, -12.0, 1.05), (-12.5, 12.5, 1.1), (6.0, 13.5, 1.0),
                    (10.5, -7.0, 1.0), (-1.0, -9.0, 0.95), (14.0, 3.0, 1.0), (-13.5, -6.0, 1.0), (8.5, 2.5, 0.9)):
        if not in_clear(x, y):
            sc.put(x, y, 1.5, lambda x, y, z, s=s: bush(a, x, y, z, s), H)
    for x, y, s in ((-13.0, 6.5, 1.3), (-1.0, -12.5, 1.3), (13.5, 2.0, 1.25), (9.5, -12.0, 1.2), (-5.5, 13.5, 1.2),
                    (2.5, -8.0, 1.1), (-13.5, -9.0, 1.2), (14.0, -7.5, 1.1), (4.0, 13.0, 1.1), (11.0, 13.0, 1.1),
                    (-9.5, 3.0, 1.0), (7.0, 9.5, 1.0)):
        if sc.free(x, y, 1.2) and not in_clear(x, y):
            fern(a, x, y, H(x, y), s * 1.3)
            sc.add(x, y, 1.2)
    decorate(a, sc, isl, H, pebbles=5, tufts=40, margin=0.6, avoid=lambda x, y: clearing.sdist(x, y) > 1.5)
    return done(a, (-16, 16, -16, 16))


# ---------------------------------------------------------------------------
# Render
# ---------------------------------------------------------------------------

VIEWS = {  # name: (azimuth, elevation, margin); positive azimuth = camera at the front-right, like the sheet
    "CliffSection": (26, 26, 1.1),
    "CliffOuterCorner": (-35, 26, 1.1),
    "CliffInnerCorner": (14, 27, 1.1),
    "RockShelfTwoLevels": (20, 32, 1.1),
    "GrassRamp": (28, 33, 1.1),
    "EarthSwitchback": (18, 35, 1.1),
    "CaveEntrance": (14, 30, 1.1),
    "RockArch": (14, 30, 1.1),
    "Riverbank": (32, 38, 1.1),
    "RockyLakeshore": (30, 38, 1.1),
    "WaterfallCliff": (30, 42, 1.06),
    "ForestFloor": (38, 33, 1.1),
}
CELL = (540, 400)


FLOOR = {"rgb": None}


def studio(scene):
    """flintkit studio plus this sheet: soft high key (short contact shadows), neutral light."""
    fk._studio(scene)
    for ln in ("FB_Key", "FB_Fill"):
        bpy.data.objects[ln].data.specular_factor = 0.15
    bpy.data.objects["FB_Key"].data.color = (1.0, 0.97, 0.92)
    bpy.data.objects["FB_Key"].data.angle = math.radians(28)
    bpy.data.objects["FB_Key"].data.energy = 3.0
    bpy.data.objects["FB_Fill"].data.energy = 1.8
    for nd in scene.world.node_tree.nodes:
        if nd.type == "BACKGROUND" and nd.inputs["Strength"].default_value < 0.9:
            nd.inputs["Strength"].default_value = 0.6
            nd.inputs["Color"].default_value = (0.62, 0.62, 0.62, 1)
    if FLOOR["rgb"] is not None:
        bsdf = bpy.data.materials["FB_GroundMat"].node_tree.nodes["Principled BSDF"]
        bsdf.inputs["Base Color"].default_value = (*FLOOR["rgb"], 1)


def calibrate_floor(scene):
    """Render the empty lit floor once and rescale its albedo so it matches the
    backdrop under this sheet's lights (only the contact shadows then show)."""
    studio(scene)
    aim_lights(30)
    bsdf = bpy.data.materials["FB_GroundMat"].node_tree.nodes["Principled BSDF"]
    target = fk.hex_rgb(fk.BG_HEX)
    rgb = [c * fk.GROUND_ALBEDO for c in target]
    hidden = [o for o in scene.objects if o.type == "MESH" and o.name != "FB_Ground" and not o.hide_render]
    for o in hidden:
        o.hide_render = True
    cam = bpy.data.objects["FB_Cam"]
    cam.data.type = "ORTHO"
    cam.data.ortho_scale = 4.0
    cam.location = (0, 0, 30)
    cam.rotation_euler = (0, 0, 0)
    bpy.data.objects["FB_Ground"].location = (0, 0, 0)
    scene.render.resolution_x = scene.render.resolution_y = 16
    probe = os.path.join(ROOT, "renders", "_floor_probe.png")
    for _ in range(2):
        bsdf.inputs["Base Color"].default_value = (*rgb, 1)
        scene.render.filepath = probe
        bpy.ops.render.render(write_still=True)
        img = bpy.data.images.load(probe, check_existing=False)
        px = np.array(img.pixels[:], dtype=np.float32).reshape(-1, 4)[:, :3].mean(0)
        bpy.data.images.remove(img)
        got = [fk.srgb_to_linear(float(c)) for c in px]
        rgb = [min(1.0, c * t / max(g, 1e-4)) for c, t, g in zip(rgb, target, got)]
    os.remove(probe)
    for o in hidden:
        o.hide_render = False
    FLOOR["rgb"] = rgb


def aim_lights(az):
    """Keep the sheet's lighting fixed relative to the viewer: key from the upper
    left of the camera (so right-hand faces fall into shade, as on the sheet)."""
    cam_ang = math.atan2(-math.cos(math.radians(az)), math.sin(math.radians(az)))  # camera position bearing
    for name, off, elev in (("FB_Key", -1.1, 44.0), ("FB_Fill", 1.9, 22.0)):
        b = cam_ang + off
        e = math.radians(elev)
        toward = Vector((math.cos(b) * math.cos(e), math.sin(b) * math.cos(e), math.sin(e)))
        bpy.data.objects[name].rotation_euler = (-toward).to_track_quat("-Z", "Y").to_euler()


def render_cell(obj, path, res, az, el, margin, samples=32):
    scene = bpy.context.scene
    studio(scene)
    scene.render.resolution_x, scene.render.resolution_y = res
    scene.render.resolution_percentage = 100
    try:
        scene.eevee.taa_render_samples = samples
    except AttributeError:
        pass
    hidden = []
    for o in scene.objects:
        if o.type == "MESH" and o is not obj and o.name != "FB_Ground" and not o.hide_render:
            hidden.append(o)
            o.hide_render = True
    bpy.context.view_layer.update()
    fk.frame(obj, az, el, margin)
    aim_lights(az)
    cam = bpy.data.objects["FB_Cam"]
    cam.data.type = "ORTHO"
    azr, elr = math.radians(az), math.radians(el)
    d = Vector((math.sin(azr), -math.cos(azr), math.tan(elr))).normalized()
    rot = (-d).to_track_quat("-Z", "Y")
    R = rot.to_matrix()
    right, up = R.col[0], R.col[1]
    mw = obj.matrix_world
    pts = [mw @ v.co for v in obj.data.vertices]
    xs = [p.dot(right) for p in pts]
    ys = [p.dot(up) for p in pts]
    zs = [p.dot(d) for p in pts]
    cx, cy = (min(xs) + max(xs)) / 2, (min(ys) + max(ys)) / 2
    aspect = res[0] / res[1]
    cam.data.ortho_scale = max(max(xs) - min(xs), (max(ys) - min(ys)) * aspect) * margin
    cam.data.clip_end = 2000
    cam.location = right * cx + up * cy + d * (max(zs) + 200)
    cam.rotation_euler = rot.to_euler()
    scene.render.filepath = path
    os.makedirs(os.path.dirname(path), exist_ok=True)
    bpy.ops.render.render(write_still=True)
    for o in hidden:
        o.hide_render = False


def render_sheet(objs, path, cols=4, cell=CELL, compose=True, samples=32):
    base, _ = os.path.splitext(path)
    calibrate_floor(bpy.context.scene)
    cells = []
    for o in objs:
        i = NAMES.index(o.name)
        p = f"{base}_cells/{i + 1:02d}_{o.name}.png"
        az, el, m = VIEWS.get(o.name, (-30, 32, 1.04))
        render_cell(o, p, cell, az, el, m, samples)
        cells.append(p)
    if not compose:
        return
    rows = math.ceil(len(objs) / cols)
    w, h = cell
    sheet = np.ones((rows * h, cols * w, 4), dtype=np.float32)
    for i, p in enumerate(cells):
        img = bpy.data.images.load(p, check_existing=False)
        px = np.array(img.pixels[:], dtype=np.float32).reshape(img.size[1], img.size[0], 4)
        r, c = divmod(i, cols)
        y0 = (rows - 1 - r) * h
        sheet[y0:y0 + h, c * w:c * w + w] = px[:h, :w]
        bpy.data.images.remove(img)
    out = bpy.data.images.new("FB_Sheet", cols * w, rows * h, alpha=True)
    out.pixels = sheet.ravel()
    out.filepath_raw = path
    out.file_format = "PNG"
    out.save()
    bpy.data.images.remove(out)


BUILDERS = [cliff_section, cliff_outer_corner, cliff_inner_corner, rock_shelf,
            grass_ramp, earth_switchback, cave_entrance, rock_arch,
            riverbank, rocky_lakeshore, waterfall_cliff, forest_floor]
NAMES = ["CliffSection", "CliffOuterCorner", "CliffInnerCorner", "RockShelfTwoLevels", "GrassRamp",
         "EarthSwitchback", "CaveEntrance", "RockArch", "Riverbank", "RockyLakeshore", "WaterfallCliff",
         "ForestFloor"]


def main():
    fk.reset_file()
    only = [s for s in os.environ.get("FB_ONLY", "").split(",") if s]
    samples = int(os.environ.get("FB_SAMPLES", "32"))
    objs = [b() for b, n in zip(BUILDERS, NAMES) if not only or n in only]
    fk.layout_row(objs)
    for o in objs:
        assert tuple(o.rotation_euler) == (0.0, 0.0, 0.0)
        if o["tris"] > 10000:
            print("OVER BUDGET", o.name, o["tris"])
        for s in vfx.sockets(o):
            print(f"SOCKET {o.name}: {s.name} {s['vfx_kind']} at {tuple(round(c, 2) for c in s.location)}")
    if not only:
        fk.save(os.path.join(ROOT, "assets", "07_terrain_kit.blend"))
    render_sheet(objs, os.path.join(ROOT, "renders", "07_terrain_kit.png"), cols=4, compose=not only,
                 samples=samples)
    print("DONE")


main()
