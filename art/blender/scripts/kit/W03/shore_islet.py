"""W03 row 3: SHORE ISLET, a small rocky island standing in open cyan water.

A craggy pinnacle of chunky columnar rock prisms (chamfered tops, deep crevice
facets) stands slightly back-left of centre on an octagonal (clipped corner)
water slab. A small grass cap with bushes, a fern and daisies crowns the summit;
plants tuck into the lower column tops and the foot. An irregular warm sand
collar (z 1.6 at the rock sloping to the waterline) rings the stack and runs out
into a little beach at the front-right; satellite boulders of strongly varied
size stand in the water.

Assets
  ShoreIslet (hero)                 32 x 32 water slab, ~16 tall
  ShoreIsletGrassCap (part)         summit grass slab with plants
  ShoreIsletRockPieces (part)       the column stack plus the loose boulders
  ShoreIsletSandCollar (part)       flat irregular sand slab
  ShoreIsletSeaStack / ShoreIsletLowIsland / ShoreIsletSteppingRock (variants)

Water and foam are VFX: the reference's "Foam Ring" part is not a mesh but the
water_foam sockets VFX_ShoreIsletFoamRing_N round each collar waterline and each
boulder; VFX_ShoreIsletSpray_N is a faint vapour sea-spray haze and
VFX_ShoreIsletFlow_N a slow water_flow beam lying on the hero's open water.

Shared W03 levels: water surface z=1.0, seabed z=0.2. Each slab is a flat
octagon of w03_water with a w03_water skirt 0.2->1.0 over a w03_riverbed band
0->0.2. Everything below the water surface (seabed, the collar's under-water
slope, rock and boulder bases cut at z=1.0) is w03_riverbed, so the
see-through water reads deep cyan; sand sits only above the waterline. One
palette key per material; the studio light and Roblox shade the facets.
"""

import math
import random

import bmesh
import numpy as np
from mathutils import Vector
from mathutils.geometry import delaunay_2d_cdt

SUBJECT = "ShoreIslet"
ROW = 3
# The W03 sheet palette, identical in all four W03 modules. ONE colour per
# material (its lit mid-tone); the light tops and dark sides in the reference
# are lighting. The sheet's existing keys (pine #3A6C28, bark #93653A,
# flower_white #F5F2EA, flower_yellow #F2C230) come from flintkit.PALETTE as they
# are; the runner only accepts w03_-prefixed keys here. This module uses
# flower_white / flower_yellow (daisies) and no pine or bark.
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
GRASS, SOIL = "w03_grass", "w03_soil"
# bush and fern leaves (and daisy stems): one leaf green, distinct from the turf
FOLIAGE = "w03_bush"
ROCK = "w03_rock"
# the ONE water surface key (slab and edge skirt)
WATER = "w03_water"
# sand: the collar above the waterline only
SAND = "w03_sand"
# everything under the water surface: seabed, the collar's under-water slope,
# rock and boulder bases below z=1.0, the slab's edge band under the skirt
RIVERBED = "w03_riverbed"
WATER_Z, BED_Z, BANK_Z = 1.0, 0.2, 1.6
FOAM_Z = WATER_Z + 0.05
FLOW_Z = WATER_Z + 0.03
# socket names: VFX_ShoreIsletFoamRing_N / VFX_ShoreIsletSpray_N, numbered
# across the module so names stay unique in the .blend
_SOCK_N = {}


def sock_name(base):
    _SOCK_N[base] = _SOCK_N.get(base, 0) + 1
    return f"VFX_{base}_{_SOCK_N[base]}"


# ---------------------------------------------------------------------------
# low-level helpers (from waterfall_module.py)
# ---------------------------------------------------------------------------


def paint(a, faces, mat, tint=1.0, var=0.04):
    mi = a._mi(mat)
    for f in faces:
        f.material_index = mi
        f.smooth = False
        t = tint * (1.0 + a.rng.uniform(-var, var))
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
        return Poly(out)

    def bbox(self):
        return (float(self.a[:, 0].min()), float(self.a[:, 1].min()),
                float(self.a[:, 0].max()), float(self.a[:, 1].max()))


def cap(a, poly, z, mat=GRASS, spacing=2.8, seed=0, jz=0.0, bstep=1.3, matfn=None, var=0.03):
    """Flat triangulated surface filling `poly` at height z (interior verts jittered by jz)."""
    bnd = poly.resample(bstep)
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
            vmap[k] = bm.verts.new((p.x, p.y, z + (0.0 if border else r.uniform(-jz, jz))))
        return vmap[k]

    out = []
    for f in faces:
        cx = sum(vco[k].x for k in f) / len(f)
        cy = sum(vco[k].y for k in f) / len(f)
        if not poly.inside(cx, cy):
            continue
        bf = face(a, [V(k) for k in f], matfn(cx, cy) if matfn else mat, 1.0, var, out=(0, 0, 1))
        if bf:
            out.append(bf)
    return out


def skirt(a, pts, ztop, zbot, mat, out, tint=1.0, var=0.05):
    """Vertical band under a 2D polyline. out: 2D outward direction or fn(mid) -> dir."""
    bm = a.bm
    cols = [(bm.verts.new((p[0], p[1], ztop)), bm.verts.new((p[0], p[1], zbot))) for p in pts]
    for k in range(len(cols) - 1):
        (t0, b0), (t1, b1) = cols[k], cols[k + 1]
        mid = ((pts[k][0] + pts[k + 1][0]) / 2, (pts[k][1] + pts[k + 1][1]) / 2)
        o = out(mid) if callable(out) else out
        face(a, (t0, b0, b1, t1), mat, tint, var, out=(o[0], o[1], 0))


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
    faces = list({f for v in verts for f in v.link_faces})
    bmesh.ops.recalc_face_normals(bm, faces=faces)
    if facets:
        bmesh.ops.dissolve_limit(bm, angle_limit=math.radians(facets), verts=verts,
                                 edges=list({e for v in verts for e in v.link_edges}))
        verts = [v for v in verts if v.is_valid]
    bm.normal_update()
    faces = list({f for v in verts for f in v.link_faces})
    for f in sorted(faces, key=lambda f: tuple(f.calc_center_median())):
        m, t = paint_fn(f)
        paint(a, [f], m, t, 0.05)
    return verts


def rock_fn(rng):
    """One rock colour (w03_rock, the reference's lit mid-tone) with a small
    random per-face tint. Light bevelled tops and dark crevices come from the
    geometry and the lighting, never from paint."""

    def fn(f):
        return ROCK, 1.0

    return fn


# ---------------------------------------------------------------------------
# rock: columns and boulders
# ---------------------------------------------------------------------------


def column(a, c, u, w, d, h, z0, all_round=False, bulge=0.3, cham=None, lean=(0.0, 0.0), taper=0.06,
           crown=(0.0, 0.0)):
    """Chunky columnar rock prism (hull of jittered 8-point rings) with a chamfered
    top and two big front planes meeting at an off-centre vertical crease.
    c = footprint centre, u = unit vector along the face, front normal
    n = (u.y, -u.x). lean shifts the top by (dx, dy), growing with height;
    crown = (along u, toward the front n) height change across the top, so
    the crown slopes. Returns the (x, y, z) centre of its top."""
    rng = a.rng
    n = (u[1], -u[0])
    hw, hd = w / 2, d / 2
    ch = cham if cham is not None else min(1.0, 0.18 * min(w, h) + 0.3) * rng.uniform(0.85, 1.2)
    ch = min(ch, hw * 0.6, h * 0.45)

    def P(lu, lv, z):
        t = (z - z0) / h
        return Vector((c[0] + u[0] * lu + n[0] * lv + lean[0] * t, c[1] + u[1] * lu + n[1] * lv + lean[1] * t, z))

    hd0 = hd
    fc = hd * rng.uniform(0.7, 1.1)
    rr = rng.uniform(-0.4, 0.4)
    sf = rng.choice((-1, 1)) * rng.uniform(0.2, 0.34)

    def ring(shift=0.0, out=0.0, sc=1.0):
        r = max(-0.6, min(0.6, rr + shift))
        # the depth tapers too (a little less than the width): flared, pyramidal columns
        hd = hd0 * (1.0 - (1.0 - sc) * 0.6)
        return [(-hw * sc, -hd), (hw * sc, -hd), (hw * sc, hd - fc), (-hw * sc, hd - fc),
                (hw * sc * r, hd + out), (hw * sc * (r + sf), hd + out - fc * abs(sf) * 0.9),
                (hw * sc * 0.78, hd - fc * 0.3 + out * 0.5), (-hw * sc * 0.8, hd - fc * 0.35 + out * 0.4)]

    # few levels and little jitter: each column is a handful of big side planes
    # (the hull's near-coplanar triangles dissolve into n-gons below)
    j = 0.05
    pts = []
    zs = z0 + h - ch
    nlev = 2 if h < 9 else 3
    for k in range(nlev):
        t = k / (nlev - 1)
        z = z0 + (zs - z0) * t + (rng.uniform(-0.2, 0.2) * min(1, h / 6) if 0 < k < nlev - 1 else 0.0)
        sc = 1.0 + (rng.uniform(0.02, 0.05) if 0 < k < nlev - 1 else 0.0) - taper * t
        out = rng.uniform(0.0, bulge) if 0 < k < nlev - 1 else 0.0
        for lu, lv in ring(0.0, out, sc):
            pts.append(P(lu + rng.uniform(-j, j), lv + rng.uniform(-j, j), z))
    tilt = rng.uniform(-0.15, 0.15) * min(1.0, h / 3)
    for lu, lv in ring(0.0, 0.0, 1.0 - taper):
        ilu = lu - math.copysign(ch, lu) * (1.0 if abs(lu) > hw * 0.7 else 0.3)
        if lv > 0:
            ilv = lv - ch
        elif all_round:
            ilv = lv + ch * 0.8
        else:
            ilv = lv
        cz = crown[0] * ilu / hw + crown[1] * ilv / max(hd0, 1e-6)
        pts.append(P(ilu, ilv, z0 + h + tilt * lu / hw + cz + rng.uniform(-0.05, 0.05)))
    hull(a, pts, rock_fn(rng), facets=6.0)
    return (c[0] + lean[0], c[1] + lean[1], z0 + h)


def dome(a, x, y, z, w, h):
    """Rounded faceted boulder (the stepping rock): stacked, twisted rings of
    points (near-vertical skirt, round shoulder, broad low top) whose hull
    gives a dozen big chiselled facets; w wide, h tall, base at z."""
    rng = a.rng
    R = w / 2
    # (height fraction, radius fraction, points)
    rings = ((0.0, 0.92, 7), (0.45, 1.0, 7), (0.75, 0.86, 7), (0.93, 0.52, 5), (1.0, 0.12, 3))
    pts = []
    for k, (fz, fr, n) in enumerate(rings):
        off = rng.uniform(0, TAU)
        for i in range(n):
            th = off + TAU * i / n + rng.uniform(-0.2, 0.2)
            r = R * fr * rng.uniform(0.92, 1.06)
            pts.append(Vector((x + math.cos(th) * r * 1.04, y + math.sin(th) * r * 0.96,
                               z + h * fz + (rng.uniform(-0.15, 0.15) if 0 < fz < 1 else 0.0))))
    hull(a, pts, rock_fn(rng), facets=8.0)


def chunk(a, x, y, z, s, tall=1.0):
    """Upright chunky sea boulder like the reference's: a near-vertical skirt,
    a broad shoulder and a chamfered, flat-ish top (taller ones get a smaller,
    more pointed top). Hull of twisted rings, ~10-14 big facets; s wide,
    ~0.8 * s * tall high, base at z."""
    rng = a.rng
    R = s / 2
    h = s * 0.8 * tall
    topr = 0.5 if tall < 1.25 else 0.3
    rings = ((0.0, 0.95, 7), (0.5, 1.0, 7), (0.8, 0.84, 6), (1.0, topr, 5))
    pts = []
    for fz, fr, n in rings:
        off = rng.uniform(0, TAU)
        for i in range(n):
            th = off + TAU * i / n + rng.uniform(-0.2, 0.2)
            r = R * fr * rng.uniform(0.9, 1.06)
            pts.append(Vector((x + math.cos(th) * r * 1.06, y + math.sin(th) * r * 0.94,
                               z + h * fz + (rng.uniform(-0.12, 0.12) * h / 4 if fz > 0 else 0.0))))
    hull(a, pts, rock_fn(rng), facets=8.0)
    return z + h


def boulder(a, x, y, z, s, tall=1.0, exp=0.6, n=16):
    """Rounded faceted boulder, base at z (s ~ its width). Returns its top z."""
    rng = a.rng
    sx, sy, sz = s * rng.uniform(1.0, 1.15) / 2, s * rng.uniform(0.85, 1.0) / 2, s * 0.92 * tall / 2
    cz = z + s * 0.32 * tall
    pts = []
    sp = lambda v: math.copysign(abs(v) ** exp, v)  # noqa: E731
    top = z
    for _ in range(n):
        th = rng.uniform(0, TAU)
        ph = math.acos(rng.uniform(-1, 1))
        px, py, pz = math.sin(ph) * math.cos(th), math.sin(ph) * math.sin(th), math.cos(ph)
        r = 1 + rng.uniform(-0.1, 0.1)
        p = Vector((x + sp(px) * sx * r, y + sp(py) * sy * r, max(z - 0.2, cz + sp(pz) * sz * r)))
        top = max(top, p.z)
        pts.append(p)
    hull(a, pts, rock_fn(rng), facets=9.0)
    return top


# ---------------------------------------------------------------------------
# vegetation (lobby build_07 recipes in the W03 colours)
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
    paint(a, faces, mat, tint if tint is not None else 1.0, 0.05)


def tuft(a, x, y, z, s=1.0, n=3):
    rng = a.rng
    for i in range(n):
        ang = TAU * i / n + rng.uniform(-0.5, 0.5)
        frond(a, (x + rng.uniform(-0.25, 0.25) * s, y + rng.uniform(-0.25, 0.25) * s, z - 0.05),
              ang, rng.uniform(1.0, 1.35), rng.uniform(0.8, 1.2) * s, 0.3 * s,
              FOLIAGE, droop=0.12)


def fern(a, x, y, z, s=1.0, k=7):
    rng = a.rng
    for i in range(k):
        ang = TAU * i / k + rng.uniform(-0.25, 0.25)
        frond(a, (x, y, z - 0.05), ang, rng.uniform(0.6, 0.95), rng.uniform(1.6, 2.2) * s,
              0.8 * s, FOLIAGE, droop=0.4)


def bush(a, x, y, z, s=1.0, lobes=3):
    """Chunky round leafy bush (darker leaf green so it reads on the lime
    grass): lobes round the base, a crown on top."""
    rng = a.rng
    R = 1.2 * s
    for i in range(lobes):
        ang = TAU * i / lobes + rng.uniform(-0.35, 0.35)
        r = R * rng.uniform(0.62, 0.76)
        a.ico(r, loc=(x + math.cos(ang) * R * 0.55, y + math.sin(ang) * R * 0.55, z + r * 0.7), subdiv=1,
              jitter=0.12, mat=FOLIAGE, tint=1.0, face_tint_var=0.05)
    r = R * rng.uniform(0.66, 0.78)
    a.ico(r, loc=(x + rng.uniform(-0.2, 0.2) * R, y + rng.uniform(-0.2, 0.2) * R, z + R * 1.0), subdiv=1,
          jitter=0.1, mat=FOLIAGE, tint=1.0, face_tint_var=0.05)


def daisy(a, x, y, z, s=1.0, lift=0.0):
    """White five-petal daisy (one flat star n-gon) with a yellow centre. With
    `lift` it stands on a thin stem above the surrounding foliage."""
    bm, rng = a.bm, a.rng
    k = 5
    rot = rng.uniform(0, TAU)
    zz = z + 0.3 * s + lift
    if lift > 0:
        sw = 0.09 * s
        sv = [bm.verts.new((x - sw, y, z - 0.05)), bm.verts.new((x + sw, y, z - 0.05)),
              bm.verts.new((x, y + 0.02, zz - 0.02))]
        face(a, sv, FOLIAGE, 1.0, 0.03, out=(0, -1, 0))
        sv = [bm.verts.new((x, y - sw, z - 0.05)), bm.verts.new((x, y + sw, z - 0.05)),
              bm.verts.new((x + 0.02, y, zz - 0.02))]
        face(a, sv, FOLIAGE, 1.0, 0.03, out=(1, 0, 0))
    ring = []
    for i in range(2 * k):
        ang = rot + PI * i / k
        rr = (0.45 if i % 2 == 0 else 0.22) * s
        ring.append(bm.verts.new((x + math.cos(ang) * rr, y + math.sin(ang) * rr, zz)))
    face(a, ring, "flower_white", rng.uniform(0.97, 1.03), 0.0, out=(0, 0, 1))
    c = [bm.verts.new((x + math.cos(rot + TAU * i / 3) * 0.14 * s, y + math.sin(rot + TAU * i / 3) * 0.14 * s,
                       zz + 0.02)) for i in range(3)]
    ap = bm.verts.new((x, y, zz + 0.12 * s))
    for i in range(3):
        face(a, (c[i], c[(i + 1) % 3], ap), "flower_yellow", 1.0, 0.0, out=(0, 0, 1))


def grass_fn(seed):
    """One turf colour (w03_grass) everywhere: the reference cap is a single lime."""

    def fn(x, y):
        return GRASS
    return fn


# ---------------------------------------------------------------------------
# outlines: octagon slab, shore, foam bands
# ---------------------------------------------------------------------------


def octagon(W, D, clip):
    hw, hd = W / 2, D / 2
    return [(-hw + clip, -hd), (hw - clip, -hd), (hw, -hd + clip), (hw, hd - clip),
            (hw - clip, hd), (-hw + clip, hd), (-hw, hd - clip), (-hw, -hd + clip)]


def ray_poly(ox, oy, dx, dy, pts):
    """Distance from (ox, oy) along unit (dx, dy) to a convex polygon's edge."""
    best = 1e9
    n = len(pts)
    for i in range(n):
        ax, ay = pts[i]
        bx, by = pts[(i + 1) % n]
        ex, ey = bx - ax, by - ay
        den = dx * ey - dy * ex
        if abs(den) < 1e-9:
            continue
        t = ((ax - ox) * ey - (ay - oy) * ex) / den
        s = ((ax - ox) * dy - (ay - oy) * dx) / den
        if t > 1e-6 and -1e-6 <= s <= 1 + 1e-6:
            best = min(best, t)
    return best


class Shore:
    """Star-shaped waterline round (cx, cy): a wobbly ellipse with an optional
    bulge (a beach) toward angle `bdir` of extra radius `bamt`."""

    def __init__(self, cx, cy, rx, ry, bdir=0.0, bamt=0.0, amp=0.05, seed=0):
        self.cx, self.cy, self.rx, self.ry = cx, cy, rx, ry
        self.bdir, self.bamt, self.amp = bdir, bamt, amp
        r = random.Random(seed)
        self.p1, self.p2, self.p3 = r.uniform(0, TAU), r.uniform(0, TAU), r.uniform(0, TAU)

    def R(self, th):
        c, s = math.cos(th), math.sin(th)
        re = self.rx * self.ry / math.sqrt((self.ry * c) ** 2 + (self.rx * s) ** 2)
        re *= 1 + self.amp * (math.sin(3 * th + self.p1) + 0.6 * math.sin(5 * th + self.p2))
        b = max(0.0, math.cos(th - self.bdir))
        return re + self.bamt * b * b

    def pt(self, th, dr=0.0, k=1.0):
        r = self.R(th) * k + dr
        return (self.cx + math.cos(th) * r, self.cy + math.sin(th) * r)

    def angles(self, n, extra=()):
        th = [TAU * k / n for k in range(n)]
        for px, py in extra:
            th.append(math.atan2(py - self.cy, px - self.cx) % TAU)
        th.sort()
        out = []
        for t in th:
            if not out or t - out[-1] > 0.012:
                out.append(t)
        if TAU - out[-1] + out[0] < 0.012:
            out.pop()
        return out


def loop_faces(a, L0, L1, mats, out=(0, 0, 1), var=0.02, tint=1.0):
    """Quads between two closed vertex loops of the same length; mats[i] per segment."""
    n = len(L0)
    for i in range(n):
        j = (i + 1) % n
        if callable(mats):
            m = mats(i, sum(v.co.x for v in (L0[i], L0[j], L1[j], L1[i])) / 4,
                     sum(v.co.y for v in (L0[i], L0[j], L1[j], L1[i])) / 4)
        else:
            m = mats[i] if isinstance(mats, list) else mats
        if m is None:
            continue
        face(a, (L0[i], L0[j], L1[j], L1[i]), m, tint, var, out=out)


def water_slab(a, W, D, clip, shore, n=64, seed=0, fill=False):
    """Octagonal flat water slab round a shore line: ONE w03_water surface at
    z=1.0 from the shore out to the clipped-corner rim, a w03_water edge skirt
    1.0->0.2 over a w03_riverbed band 0.2->0, and a flat w03_riverbed seabed at
    z=0.2 (seen through the water). With `fill` the water also covers the
    shore outline (no sand collar inside it). Foam, ripples and streaks are NOT
    geometry: water_foam / water_flow sockets carry them. Returns the octagon."""
    bm = a.bm
    oc = octagon(W, D, clip)
    angs = shore.angles(n, oc)
    loops = [[], []]
    for th in angs:
        dx, dy = math.cos(th), math.sin(th)
        Rc = shore.R(th)
        Ro = max(ray_poly(shore.cx, shore.cy, dx, dy, oc), Rc + 0.05)
        for k, r in enumerate((Rc, Ro)):
            loops[k].append(bm.verts.new((shore.cx + dx * r, shore.cy + dy * r, WATER_Z)))
    loop_faces(a, loops[0], loops[1], WATER)
    if fill:
        face(a, [bm.verts.new(v.co) for v in loops[0]], WATER, 1.0, 0.0, out=(0, 0, 1))
    ring = oc + [oc[0]]
    for p, q in zip(ring, ring[1:]):
        mid = ((p[0] + q[0]) / 2, (p[1] + q[1]) / 2)
        skirt(a, [p, q], WATER_Z, BED_Z, WATER, mid, var=0.03)
        skirt(a, [p, q], BED_Z, 0.0, RIVERBED, mid, var=0.03)
    cap(a, Poly(oc), BED_Z, RIVERBED, spacing=7.0, seed=seed + 1, bstep=4.0)
    return oc


def shore_foam_sockets(shore, step=5.0, dr=0.35, scale=0.7):
    """water_foam sockets every ~`step` studs along the waterline (the foam
    ring, VFX_ShoreIsletFoamRing_N): (kind, loc, scale, name) tuples."""
    th = [TAU * k / 360 for k in range(361)]
    pts = [shore.pt(t, dr) for t in th]
    per = sum(math.dist(pts[k], pts[k + 1]) for k in range(360))
    n = max(3, int(round(per / step)))
    out, acc, k = [], 0.0, 0
    targets = [per * i / n for i in range(n)]
    for i in range(360):
        d = math.dist(pts[i], pts[i + 1])
        while k < n and acc + d >= targets[k]:
            f = (targets[k] - acc) / d if d else 0.0
            x = pts[i][0] + (pts[i + 1][0] - pts[i][0]) * f
            y = pts[i][1] + (pts[i + 1][1] - pts[i][1]) * f
            out.append(("water_foam", (x, y, FOAM_Z), scale, "ShoreIsletFoamRing"))
            k += 1
        acc += d
    return out


def boulder_foam_sockets(boulders, lo=0.6, hi=0.8):
    """One water_foam socket round each boulder standing in the water, scaled
    0.6-0.8 by its size."""
    out = []
    for x, y, s, _ in boulders:
        sc = max(lo, min(hi, lo + (s - 1.2) / (5.2 - 1.2) * (hi - lo)))
        out.append(("water_foam", (x, y, FOAM_Z), round(sc, 2), "ShoreIsletFoamRing"))
    return out


def sand_collar(a, shore, angs, zs=(1.06, 1.2, 1.45, 1.6), skirt_bot=BED_Z, bottom=False, rim=0.6, apron=1.4):
    """Irregular w03_sand slab inside the shore line: a flat `rim` band at the
    waterline rising to BANK_Z at the rock, and a shore slope running `apron`
    studs out and down to skirt_bot (vertical when apron=0; optionally a
    bottom). In the water assets finish(submerge=True) cuts it at z=1.0 and the
    under-water part of the slope becomes w03_riverbed."""
    bm = a.bm
    ks = [None, None, 0.7, 0.42]
    loops = [[] for _ in range(4)]
    bots = []
    for th in angs:
        Rc = shore.R(th)
        dx, dy = math.cos(th), math.sin(th)
        rs = [Rc, Rc - rim, min(Rc * ks[2], Rc - rim - 0.4), Rc * ks[3]]
        for k in range(4):
            loops[k].append(bm.verts.new((shore.cx + dx * rs[k], shore.cy + dy * rs[k], zs[k])))
        bots.append(bm.verts.new((shore.cx + dx * (Rc + apron), shore.cy + dy * (Rc + apron), skirt_bot)))
    loop_faces(a, loops[0], loops[1], SAND, var=0.03)
    loop_faces(a, loops[1], loops[2], SAND, var=0.03)
    loop_faces(a, loops[2], loops[3], SAND, var=0.03)
    c = bm.verts.new((shore.cx, shore.cy, zs[3]))
    n = len(angs)
    for i in range(n):
        face(a, (loops[3][i], loops[3][(i + 1) % n], c), SAND, 1.0, 0.03, out=(0, 0, 1))
    for i in range(n):
        j = (i + 1) % n
        th = (angs[i] + angs[j]) / 2 if j else (angs[i] + angs[j] + TAU) / 2
        face(a, (loops[0][i], loops[0][j], bots[j], bots[i]), SAND, 1.0, 0.03,
             out=(math.cos(th), math.sin(th), 0.3 if apron else 0.0))
    if bottom:
        face(a, bots, SAND, 1.0, 0.0, out=(0, 0, -1))


def grass_cap(a, cx, cy, hx, hy, z, seed, soil=0.8, bottom=None, n=16, band=SOIL):
    """Rounded grass slab on a thin soil band. Returns its Poly."""
    rr = random.Random(seed)
    p1 = rr.uniform(0, TAU)
    pts = []
    for k in range(n):
        th = TAU * k / n
        c, s = math.cos(th), math.sin(th)
        r = 1.0 / ((abs(c) / hx) ** 3 + (abs(s) / hy) ** 3) ** (1 / 3)
        r *= 1 + 0.06 * math.sin(3 * th + p1) + rr.uniform(-0.03, 0.03)
        pts.append((cx + c * r, cy + s * r))
    poly = Poly(pts)
    # flat top on an inset outline, then a rounded grass lip sloping down to the
    # outer outline, so the cap reads as a chunky lime slab over its soil band
    lip, drop = 0.4, 0.35
    k = 1.0 - lip / min(hx, hy)
    inner = Poly([(cx + (x - cx) * k, cy + (y - cy) * k) for x, y in pts])
    cap(a, inner, z, spacing=2.0, seed=seed, jz=0.06, bstep=99.0, matfn=grass_fn(seed))
    bm = a.bm
    L0 = [bm.verts.new((p.x, p.y, z)) for p in inner.p]
    L1 = [bm.verts.new((p.x, p.y, z - drop)) for p in poly.p]
    if len(L0) == len(L1):
        gf = grass_fn(seed)
        loop_faces(a, L0, L1, lambda i, x, y: gf(x, y))
    loop = [(p.x, p.y) for p in poly.p] + [(poly.p[0].x, poly.p[0].y)]
    skirt(a, loop, z - drop, z - soil, band, lambda m: (m[0] - cx, m[1] - cy))
    if bottom is not None:
        bm = a.bm
        face(a, [bm.verts.new((p.x, p.y, z - soil)) for p in poly.p], SOIL, 1.0, 0.0, out=(0, 0, -1))
    return poly


def scatter_daisies(a, poly, z, n, seed, avoid=(), tufts=0.5):
    rr = random.Random(seed)
    x0, y0, x1, y1 = poly.bbox()
    placed, tries = 0, 0
    taken = list(avoid)
    while placed < n and tries < 300:
        tries += 1
        x, y = rr.uniform(x0, x1), rr.uniform(y0, y1)
        if poly.sdist(x, y) < 0.5:
            continue
        if any((x - px) ** 2 + (y - py) ** 2 < r * r for px, py, r in taken):
            continue
        daisy(a, x, y, z, rr.uniform(1.25, 1.45), lift=rr.uniform(0.25, 0.4))
        if rr.random() < tufts:
            tuft(a, x + rr.uniform(-0.7, 0.7), y + rr.uniform(-0.7, 0.7), z, 0.75)
        taken.append((x, y, 0.9))
        placed += 1


# ---------------------------------------------------------------------------
# island builder
# ---------------------------------------------------------------------------


def submerge(a):
    """Cut the rock and sand at the water surface (z=1.0) and give everything
    below it the one under-water key, w03_riverbed: rock column and boulder
    bases, fully submerged rocks and the collar's under-water slope. The water
    slab itself (exactly z=1.0, w03_water) is untouched."""
    bm = a.bm
    idx = {a.mats.index(k) for k in (ROCK, SAND) if k in a.mats}
    faces = [f for f in bm.faces if f.material_index in idx]
    if not faces:
        return
    verts = list({v for f in faces for v in f.verts})
    edges = list({e for f in faces for e in f.edges})
    bmesh.ops.bisect_plane(bm, geom=faces + edges + verts, dist=1e-4,
                           plane_co=(0, 0, WATER_Z), plane_no=(0, 0, 1))
    under = [f for f in bm.faces if f.material_index in idx
             and max(v.co.z for v in f.verts) <= WATER_Z + 1e-3]
    paint(a, under, RIVERBED, 1.0, 0.03)


def finish(kit, a, role, collision, budget, notes, sockets=(), shading_ok=None, two_tone_ok=None,
           submerged=False):
    """Clamp to z>=0, (water assets) colour everything under the water
    riverbed, write the mesh, tag it and attach VFX sockets (locs in build
    coordinates; each socket is (kind, loc, scale[, name base]) or a dict with
    kind, loc, scale, name and kind-specific keys such as end / width)."""
    for v in a.bm.verts:
        v.co.z = max(v.co.z, 0.0)
    if submerged:
        submerge(a)
    xs = [v.co.x for v in a.bm.verts]
    ys = [v.co.y for v in a.bm.verts]
    zs = [v.co.z for v in a.bm.verts]
    off = ((min(xs) + max(xs)) / 2, (min(ys) + max(ys)) / 2, min(zs))
    obj = a.finish()
    kit.tag(obj, role, collision=collision, budget=budget, notes=notes)
    if shading_ok:
        obj["kit_shading_ok"] = shading_ok
    if two_tone_ok:
        obj["kit_two_tone_ok"] = two_tone_ok
    for s in sockets:
        extra = {}
        if isinstance(s, dict):
            s = dict(s)
            kind, loc, scale = s.pop("kind"), s.pop("loc"), s.pop("scale", 1.0)
            base = s.pop("name", None)
            if "end" in s:
                e = s.pop("end")
                extra["end"] = (e[0] - off[0], e[1] - off[1], e[2] - off[2])
            extra.update(s)
        else:
            kind, loc, scale = s[:3]
            base = s[3] if len(s) > 3 else None
        name = sock_name(base) if base else None
        if kind == "vapour":
            extra.setdefault("emitters", spray_emitters(kit))
        elif kind == "water_foam":
            extra.setdefault("emitters", foam_emitters(kit))
        kit.vfx.add(obj, kind, (loc[0] - off[0], loc[1] - off[1], loc[2] - off[2]), scale=scale, name=name,
                    **extra)
    return obj


def spray_emitters(kit):
    """The vapour kind tuned to a faint, low sea-spray haze that hangs at the
    stack's foot (no tall drifting steam plume, no wisps)."""
    em = dict(kit.vfx.KINDS["vapour"]["emitters"][0])
    em.update({"name": "Spray", "size": [2.0, 4.5], "transparency": [0.88, 0.8, 1.0], "lifetime": [2.0, 3.5],
               "rate": 2, "speed": [0.3, 0.7], "spread": 35, "drag": 0.8, "acceleration": [0.0, 0.15, 0.0],
               "shape": [2.5, 0.4, 2.5]})
    return [em]


def foam_emitters(kit):
    """water_foam made bolder: denser, more opaque, slightly larger patches so
    the ring reads as the reference's solid white surf line on the cyan sea."""
    em = dict(kit.vfx.KINDS["water_foam"]["emitters"][0])
    em.update({"rate": 12, "transparency": [0.0, 0.1, 0.75], "size": [2.6, 3.8], "lifetime": [2.2, 3.2]})
    return [em]


def rocky(a):
    """Register the rock key first (material order only)."""
    a._mi(ROCK)
    return a


def build_columns(a, cols):
    """cols: (cx, cy, ux, uy, w, d, h, z0, all_round, lean[, taper[, crown]]) -> list of top centres."""
    tops = []
    for col in cols:
        cx, cy, ux, uy, w, d, h, z0, rnd, lean = col[:10]
        taper = col[10] if len(col) > 10 else 0.06
        crown = col[11] if len(col) > 11 else (0.0, 0.0)
        tops.append(column(a, (cx, cy), (ux, uy), w, d, h, z0, all_round=rnd, lean=lean, taper=taper,
                           crown=crown))
    return tops


def build_boulders(a, boulders):
    """(x, y, s, tall) standing on the bed in the water (foam = sockets)."""
    for x, y, s, tall in boulders:
        chunk(a, x, y, BED_Z + 0.1, s, tall=tall)


# ---------------------------------------------------------------------------
# hero layout
# ---------------------------------------------------------------------------

HERO_SHORE = dict(cx=0.4, cy=-0.6, rx=8.4, ry=7.4, bdir=math.radians(-35), bamt=2.4, amp=0.06, seed=31)
COL_Z0 = 1.2
# cx, cy, ux, uy, w, d, h, z0, all_round, lean, taper, crown
# a tall narrow pinnacle (~12 x 9.5 footprint, rock top z ~14): the main
# column is fat and tapers hard to a ~6-wide sloping crown; a back-right
# shoulder and two lower front steps cluster round it and leave deep vertical
# crevices where their faces meet
HERO_COLS = [
    (-1.4, 1.6, 1, 0, 10.4, 8.8, 13.6, COL_Z0, True, (0.4, -0.3), 0.36, (-0.5, -0.8)),  # A: pinnacle, carries the cap
    (3.6, 2.8, 1, 0, 5.0, 5.2, 9.4, COL_Z0, True, (-0.2, -0.1), 0.18, (-0.7, 0.0)),     # B: back-right shoulder
    (-4.2, -2.2, 1, 0, 5.0, 3.6, 6.6, COL_Z0, True, (0.15, 0.1), 0.16, (-0.5, -0.4)),   # C: front-left step
    (2.6, -2.4, 1, 0, 4.4, 3.2, 4.2, COL_Z0, True, (0.0, 0.0), 0.1, (0.3, -0.3)),       # D: low front-right step
    (-2.2, -1.5, 1, 0, 4.0, 3.4, 10.4, COL_Z0, True, (0.2, 0.2), 0.16, (-0.4, -0.6)),   # E: front rib -> deep crevices
]
# x, y, size, tall: two big (front-left, back-right), medium left and
# front-right, small back-left, right and front
HERO_BOULDERS = [
    (-9.6, -8.8, 6.8, 1.12),   # big front-left (~6 tall)
    (10.8, 7.0, 6.2, 1.35),    # big tall back-right (~6.5 tall)
    (10.0, -10.0, 4.4, 1.15),  # medium front-right
    (-12.6, 1.0, 4.2, 1.1),    # medium left
    (-6.0, 11.2, 3.0, 1.1),    # small back-left
    (13.4, -1.0, 2.8, 1.05),   # small right
    (-2.0, -12.8, 2.0, 1.0),   # small front
]
HERO_PEBBLES = [(5.0, -5.8, 0.9), (7.2, -3.4, 0.7), (-1.0, -6.4, 0.6)]


def build_hero(kit):
    a = rocky(kit.flintkit.Asset("ShoreIslet", "Terrain", seed=3301))
    sh = Shore(**HERO_SHORE)
    water_slab(a, 32.0, 32.0, 7.0, sh, n=72, seed=3)
    angs = sh.angles(72, octagon(32.0, 32.0, 7.0))
    sand_collar(a, sh, angs)
    tops = build_columns(a, HERO_COLS)
    build_boulders(a, HERO_BOULDERS)
    for x, y, s in HERO_PEBBLES:
        boulder(a, x, y, collar_z(sh, x, y) - 0.25, s, tall=0.8, n=10)
    summit(a, tops)
    socks = hero_sockets(sh)
    nr = sum(1 for s in socks if isinstance(s, tuple) and s[0] == "water_foam")
    return finish(kit, a, "hero", "precise", 6000,
                  "32x32 shore islet: tall narrow columnar rock pinnacle (~12 x 9.5 base, rock top z~14, ~16 with "
                  "the tiny grass cap) on a sand collar in an octagonal sea slab with 7 satellite boulders; "
                  "precise so players can walk the sand, ledges and summit (the w03_water surface and skirt export "
                  "as see-through non-colliding water; the seabed, the collar's under-water slope and the rock "
                  "bases below z=1.0 are w03_riverbed). The reference's 'Foam Ring' part is NOT a mesh: it is the "
                  f"water_foam sockets VFX_ShoreIsletFoamRing_N ({nr}: one every ~5 studs round the sand "
                  f"collar waterline at z 1.05 (scale 0.7), plus one round each of the {len(HERO_BOULDERS)} "
                  "boulders standing in the "
                  "water, scale 0.6-0.8 by size; emitter made denser and more opaque for a bold white surf line). "
                  "VFX_ShoreIsletSpray_N: two faint vapour sea-spray hazes (0.6) at the windward front-left foot "
                  "of the stack and the big front-left boulder. VFX_ShoreIsletFlow_N: one slow water_flow beam "
                  "lying across the back water at z 1.03 (west -> east drift).", socks, submerged=True)


def hero_sockets(sh):
    socks = shore_foam_sockets(sh)
    socks += boulder_foam_sockets(HERO_BOULDERS)
    x, y = sh.pt(math.radians(215), 0.2)
    socks.append(("vapour", (x, y, WATER_Z + 0.3), 0.6, "ShoreIsletSpray"))
    bx, by = HERO_BOULDERS[0][:2]
    socks.append(("vapour", (bx + 1.6, by + 2.0, WATER_Z + 0.3), 0.6, "ShoreIsletSpray"))
    socks.append(flow_socket((-12.5, 11.0), (12.5, 9.5), 5.0))
    return socks


def flow_socket(p, q, width):
    """A slow water_flow beam lying on the water at z~1.03 from p to q (the
    drift direction): faint streaks, slower than the river's."""
    return dict(kind="water_flow", loc=(p[0], p[1], FLOW_Z), end=(q[0], q[1], FLOW_Z), scale=1.0,
                name="ShoreIsletFlow", width=width, beams=flow_beams())


def flow_beams():
    import vfx
    b = dict(vfx.KINDS["water_flow"]["beams"][0])
    b.update({"texture_speed": 1.6, "transparency": [0.95, 0.8, 0.8, 0.95]})
    return [b]


def summit(a, tops, cap_only=False, bottom=False):
    """Grass cap + plants on the tallest column, ledge plants on the lower
    columns and the foot dressing."""
    ax, ay, az = tops[0]
    # centred a little toward the front-left of the crown (the crown slopes
    # down to the front-right, so the cap covers its high part)
    ax, ay = ax - 0.3, ay - 0.3
    cz = az + 0.3
    # a small bright cap (~5.6 x 5.0) perched on the pinnacle's tapered crown
    poly = grass_cap(a, ax, ay, 2.8, 2.5, cz, seed=7, soil=0.9, bottom=True if bottom else None, n=16)
    # two small bushes at the back, one spiky fern, 4 daisies on stems
    bush(a, ax - 1.3, ay + 1.0, cz, 0.5)
    bush(a, ax + 1.4, ay + 0.9, cz, 0.42)
    fern(a, ax - 0.1, ay + 0.3, cz, 0.85)
    for dx, dy, lift in ((-1.3, -1.0, 0.35), (0.9, -1.2, 0.45), (1.8, -0.1, 0.4), (-0.2, -1.7, 0.3)):
        daisy(a, ax + dx, ay + dy, cz, 1.3, lift=lift)
    tuft(a, ax - 1.9, ay - 0.2, cz, 0.7)
    if cap_only:
        return poly
    # ledges: a fern on the back-right shoulder, a bush clump + daisy cluster
    # on each of the two lower front steps
    bx, by, bz = tops[1]
    fern(a, bx + 0.3, by - 0.4, bz - 0.25, 0.9)
    cx, cy, cz2 = tops[2]
    bush(a, cx - 0.6, cy + 0.2, cz2 - 0.2, 0.75)
    for ddx, ddy in ((0.8, -0.6), (1.3, 0.3)):
        daisy(a, cx + ddx, cy + ddy, cz2 - 0.15, 1.2, lift=0.3)
    dx, dy, dz = tops[3]
    bush(a, dx + 0.6, dy + 0.3, dz - 0.15, 0.7)
    fern(a, dx - 0.9, dy - 0.2, dz - 0.1, 0.7)
    daisy(a, dx - 0.2, dy - 0.9, dz - 0.1, 1.2, lift=0.3)
    if len(tops) > 4:
        ex, ey, ez = tops[4]
        tuft(a, ex + 0.4, ey - 0.6, ez - 0.25, 0.8)
    # the foot (heights follow the collar slope): a big fern front-left, bushes
    # and a daisy cluster
    sh = Shore(**HERO_SHORE)
    for kind, x, y, s in (("fern", -4.4, -5.0, 1.5), ("bush", -7.0, -2.6, 0.9), ("fern", 5.8, -4.0, 1.1),
                          ("tuft", -6.8, 1.8, 0.9), ("bush", 6.6, 1.6, 0.75), ("bush", 0.4, -4.8, 0.7)):
        z = collar_z(sh, x, y) - 0.05
        {"bush": bush, "fern": fern, "tuft": tuft}[kind](a, x, y, z, s)
    for x, y, s in ((-3.0, -5.6, 1.15), (-5.8, -4.0, 1.05), (1.4, -5.0, 1.05)):
        daisy(a, x, y, collar_z(sh, x, y) - 0.05, s, lift=0.25)
    return poly


def collar_z(shore, x, y, zs=(1.06, 1.2, 1.45, 1.6), rim=0.6):
    """Height of the sand collar's top at (x, y) (matches sand_collar's loops)."""
    th = math.atan2(y - shore.cy, x - shore.cx)
    r = math.hypot(x - shore.cx, y - shore.cy)
    Rc = shore.R(th)
    rs = [Rc, Rc - rim, min(Rc * 0.7, Rc - rim - 0.4), Rc * 0.42]
    if r >= rs[0]:
        return zs[0]
    for k in range(3):
        if r >= rs[k + 1]:
            t = (rs[k] - r) / max(1e-6, rs[k] - rs[k + 1])
            return zs[k] + (zs[k + 1] - zs[k]) * t
    return zs[3]


# ---------------------------------------------------------------------------
# parts
# ---------------------------------------------------------------------------


def part_grass_cap(kit):
    a = kit.flintkit.Asset("ShoreIsletGrassCap", "Terrain", seed=3301)
    cx, cy, _, _, _, _, _, _, _, lean = HERO_COLS[0][:10]
    summit(a, [(cx + lean[0], cy + lean[1], 0.7)], cap_only=True, bottom=True)
    return finish(kit, a, "part", "precise", 1500,
                  "small summit grass slab ~5.6 x 5.0 x 0.9 (grass on a thin soil band) with 2 small bushes, a "
                  "fern, 4 daisies and a tuft; sits on the pinnacle's crown; precise so it is walkable")


def part_rock_pieces(kit):
    a = kit.flintkit.Asset("ShoreIsletRockPieces", "Terrain", seed=3301)
    # the stack and the hero's 7 boulders, spread round it as in the hero, on
    # one base level
    build_columns(a, [c[:7] + (BED_Z + 0.1,) + c[8:] for c in HERO_COLS])
    build_boulders(a, HERO_BOULDERS)
    return finish(kit, a, "part", "hull", 4000,
                  "the columnar rock pinnacle (5 prisms ~13.6 / 10.4 / 9.4 / 6.6 / 4.2 tall) plus the 7 loose satellite "
                  "boulders (1.6-6 studs, two tall big ones), spread round it as in the hero; one rock colour "
                  "(w03_rock); hull collision")


def part_sand_collar(kit):
    a = kit.flintkit.Asset("ShoreIsletSandCollar", "Terrain", seed=3303)
    sh = Shore(**HERO_SHORE)
    angs = sh.angles(40)
    sand_collar(a, sh, angs, zs=(0.48, 0.54, 0.6, 0.62), skirt_bot=0.0, bottom=True, rim=0.7, apron=0.0)
    return finish(kit, a, "part", "precise", 800,
                  "irregular flat w03_sand slab ~18.7 x 16 x 0.6 with a beach tongue toward the front-right; "
                  "precise (walkable). Its foam edge is the hero's VFX_ShoreIsletFoamRing_N water_foam sockets.")


# ---------------------------------------------------------------------------
# variants
# ---------------------------------------------------------------------------


def build_sea_stack(kit):
    a = rocky(kit.flintkit.Asset("ShoreIsletSeaStack", "Terrain", seed=3311))
    sh = Shore(0.2, -0.3, 5.8, 5.0, bdir=math.radians(-40), bamt=1.0, amp=0.05, seed=12)
    W = 20.0
    water_slab(a, W, W, 4.6, sh, n=48, seed=13)
    angs = sh.angles(48, octagon(W, W, 4.6))
    sand_collar(a, sh, angs)
    tops = build_columns(a, [
        (-0.2, 0.4, 1, 0, 7.0, 6.0, 13.4, COL_Z0, True, (-0.2, 0.1), 0.1),   # main pillar, carries the cap
        (-1.8, -2.0, 1, 0, 4.6, 3.2, 8.6, COL_Z0, True, (0.1, 0.1), 0.1),   # front-left step
        (2.6, -0.4, 0, 1, 4.6, 3.0, 10.6, COL_Z0, True, (-0.1, 0.0), 0.1),  # right column
    ])
    ax, ay, az = tops[0]
    cz = az + 0.35
    # cap 6.0 x 5.2 overhangs the stack's chamfered top
    grass_cap(a, ax, ay, 3.1, 2.7, cz, seed=21, soil=0.85)
    bush(a, ax - 1.1, ay + 0.8, cz, 1.15, lobes=4)
    bush(a, ax + 1.5, ay + 0.9, cz, 0.9)
    fern(a, ax + 0.6, ay - 0.7, cz, 1.05)
    daisy(a, ax - 1.6, ay - 1.2, cz, 1.5, lift=0.45)
    daisy(a, ax + 2.0, ay - 0.6, cz, 1.45, lift=0.55)
    daisy(a, ax - 0.2, ay + 1.9, cz, 1.4, lift=0.4)
    tuft(a, ax + 0.4, ay + 1.6, cz, 0.85)
    tuft(a, ax - 2.2, ay + 0.2, cz, 0.8)
    bx, by, bz = tops[1]
    fern(a, bx - 0.2, by - 0.2, bz - 0.05, 0.8)
    ex, ey, ez = tops[2]
    tuft(a, ex, ey, ez - 0.05, 0.8)
    fern(a, -4.6, -3.0, BANK_Z - 0.05, 0.7)
    bush(a, 4.0, -3.9, BANK_Z - 0.1, 0.6)
    daisy(a, -2.0, -3.6, BANK_Z - 0.1)
    bl = [(-5.9, -5.2, 2.2, 1.0), (5.6, -5.5, 2.0, 1.1), (6.4, 2.8, 1.4, 1.0), (-6.4, 3.2, 1.3, 1.0)]
    build_boulders(a, bl)
    boulder(a, 1.8, -3.9, BANK_Z - 0.35, 0.6, tall=0.8, n=10)
    socks = shore_foam_sockets(sh) + boulder_foam_sockets(bl)
    x, y = sh.pt(math.radians(220), 0.2)
    socks.append(("vapour", (x, y, WATER_Z + 0.3), 0.6, "ShoreIsletSpray"))
    return finish(kit, a, "variant", "precise", 4000,
                  "Sea Stack (Tall): tall narrow stack of 3 columns ~8 x 7, rock ~15 high (~17 with the grass tuft), on a 20x20 octagonal water slab with a "
                  "thin sand collar and 4 small boulders; precise. VFX: VFX_ShoreIsletFoamRing_N water_foam "
                  f"sockets ({sum(1 for s in socks if s[0] == 'water_foam')}: round the collar waterline every "
                  "~5 studs and one per boulder), VFX_ShoreIsletSpray_N vapour sea-spray haze (0.6) at the "
                  "windward front-left foot. Seabed, collar slope and rock bases below z=1.0 are w03_riverbed.", socks, submerged=True)


def build_low_island(kit):
    a = rocky(kit.flintkit.Asset("ShoreIsletLowIsland", "Terrain", seed=3321))
    rng = a.rng
    sh = Shore(0.0, 0.2, 8.4, 6.0, bdir=math.radians(-90), bamt=1.8, amp=0.04, seed=22)
    W, D = 24.0, 22.0
    water_slab(a, W, D, 5.0, sh, n=56, seed=23)
    angs = sh.angles(56, octagon(W, D, 5.0))
    sand_collar(a, sh, angs)
    icx, icy, ex, ey = 0.0, 1.0, 5.6, 3.4
    cols = []
    N = 11
    for k in range(N):
        phi = TAU * k / N + 0.15
        x, y = icx + math.cos(phi) * ex, icy + math.sin(phi) * ey
        # outward normal of the ellipse -> front of the column
        nx, ny = math.cos(phi) / ex, math.sin(phi) / ey
        L = math.hypot(nx, ny)
        nx, ny = nx / L, ny / L
        u = (-ny, nx)
        h = rng.uniform(2.5, 3.2)
        cols.append((x + nx * 0.3, y + ny * 0.3, u[0], u[1], rng.uniform(3.6, 4.4), 2.8, h, COL_Z0, True, (0, 0)))
    cols.append((5.6, 1.4, 0, 1, 4.4, 3.6, 5.0, COL_Z0, True, (0.0, 0.0)))   # the bigger rock on the right
    cols.append((-5.0, 3.0, 0, -1, 3.6, 3.0, 3.8, COL_Z0, True, (0.0, 0.0)))
    build_columns(a, cols)
    gz = 4.0
    # the turf sits straight on the rock ring (no brown soil band, as on the
    # reference): the band under the grass lip is w03_rock
    poly = grass_cap(a, icx - 0.4, icy + 0.1, 5.6, 3.6, gz, seed=25, soil=0.8, n=20, band=ROCK)
    items = [("bush", -3.4, 1.9, 0.85), ("bush", 1.6, 2.8, 0.8), ("bush", -0.6, -1.0, 0.72),
             ("bush", 3.2, -0.9, 0.62), ("fern", 0.6, 1.0, 0.85), ("fern", -4.6, -0.2, 0.68),
             ("fern", 3.4, 3.4, 0.6)]
    for kind, x, y, s in items:
        (bush if kind == "bush" else fern)(a, x, y, gz, s)
    scatter_daisies(a, poly, gz, 7, 26, avoid=[(x, y, 1.3) for _, x, y, _ in items])
    fern(a, -2.6, -4.4, BANK_Z - 0.1, 0.65)
    daisy(a, 2.6, -5.4, BANK_Z - 0.2)
    for x, y, s in ((-0.6, -5.8, 0.7), (4.0, -4.6, 0.6), (-4.2, -4.9, 0.5)):
        boulder(a, x, y, BANK_Z - 0.4, s, tall=0.8, n=10)
    bl = [(-8.8, -6.4, 2.6, 1.0), (8.4, -6.0, 2.8, 1.05), (9.3, 3.0, 1.6, 1.0), (-9.4, 2.8, 1.8, 1.0),
          (1.4, -9.0, 1.2, 1.0)]
    build_boulders(a, bl)
    socks = shore_foam_sockets(sh) + boulder_foam_sockets(bl)
    return finish(kit, a, "variant", "precise", 5000,
                  "Low Island (Flat): wide low island ~17 x 14 with a 2.5-4 rock rim and a flat grass top (z~4) "
                  "full of bushes, ferns and daisies, a sand beach at the front, 5 boulders; precise. VFX: "
                  f"VFX_ShoreIsletFoamRing_N water_foam sockets ({len(socks)}: round the collar waterline every "
                  "~5 studs and one per boulder). Seabed, collar slope and rock bases below z=1.0 are w03_riverbed.", socks, submerged=True)


def build_stepping_rock(kit):
    a = rocky(kit.flintkit.Asset("ShoreIsletSteppingRock", "Terrain", seed=3331))
    sh = Shore(0.0, 0.3, 2.55, 2.3, amp=0.04, seed=32)
    W = 13.0
    # no sand, no plants: the water covers the boulder's footprint too
    water_slab(a, W, W, 3.0, sh, n=32, seed=33, fill=True)
    dome(a, 0.0, 0.3, BED_Z + 0.1, 4.6, 5.0)
    socks = [("water_foam", (*sh.pt(math.radians(d), 0.5), FOAM_Z), 0.7, "ShoreIsletFoamRing")
             for d in (-110, -10, 80, 170)]
    return finish(kit, a, "variant", "precise", 1500,
                  "Stepping Rock (Minimal): one rounded faceted boulder ~4.6 wide, ~5 tall on a 13x13 octagonal "
                  "water slab, no sand and no plants; precise so players can hop on. VFX: 4 "
                  "VFX_ShoreIsletFoamRing_N water_foam sockets (0.7) ringing the boulder at the waterline; the boulder base below z=1.0 and the seabed are w03_riverbed.", socks, submerged=True)


def build(kit):
    _SOCK_N.clear()
    objs = [build_hero(kit),
            part_grass_cap(kit), part_rock_pieces(kit), part_sand_collar(kit),
            build_sea_stack(kit), build_low_island(kit), build_stepping_rock(kit)]
    return objs
