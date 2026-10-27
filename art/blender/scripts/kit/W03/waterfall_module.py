"""W03 row 2: WATERFALL MODULE, a 32x32 cliff tile with a river pouring into a pool.

A tall cliff of chunky columnar rock prisms (bevelled tops, deep crevices) runs
across the tile with its face toward -Y. A river on the cliff top enters at the
back edge centre (8 wide, water at z=20.0), runs between two grass-capped cliff
halves (grass z=20.5 on a 0.5 soil band) and pours over a notched lip, falling
~19 studs into a round pool (z=1.0, w03_riverbed bed z=0.2) that fills the front ~40% of
the tile and leaves through a 12-wide mouth at the front edge centre (the seam
to the Streambed row). Behind the fall the cliff is a recessed rock notch.

Water and vapour are VFX: the falling curtain is waterfall_curtain beams from
the lip to the pool (VFX_WaterfallCurtain_N), the foam ribbon round the foot is
water_foam sockets (VFX_WaterfallFoamRibbon_N), the splash disc is a
waterfall_mist socket (VFX_WaterfallSplash) plus a vapour haze, and the channel
and pool carry water_flow beams. Only flat water surfaces are meshes.

Assets
  WaterfallModule (hero)            the assembled tile
  WaterfallTopWaterPlane (part)     channel water slab (flow + curtain sockets)
  WaterfallCliffTop (part)          grass-capped cliff-top block
  WaterfallCliffWallA/B/C (parts)   columnar wall prisms ~14 / ~10 / ~6 tall
  WaterfallNarrow / WaterfallWide / WaterfallTwoStep (variants)

Every tile keeps the same seams: channel 8 wide at the back edge centre (z=20)
and a 12-wide pool mouth at the front edge centre (z=1.0). Water faces use the
one w03_water key (exported see-through, no collision); everything under a
water surface (beds, shore slopes, submerged rock) is w03_riverbed, and sand
sits only above the waterline.
"""

import json
import math
import os
import random

import bmesh
import numpy as np
from mathutils import Vector
from mathutils.geometry import delaunay_2d_cdt

SUBJECT = "WaterfallModule"
ROW = 2
# The sheet's SIDE cell looks at the left (-X) side a little from the front, the
# pool on the right and the curtain showing past the cliff face.
SIDE_AZIMUTH = -70
# The W03 sheet palette (shared by all four W03 modules), copied verbatim. The
# existing keys pine, bark, flower_white and flower_yellow come from flintkit's
# PALETTE with the same values (the runner only accepts w03_* keys here).
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
EDGE = 16.0
# ONE base colour per material; the light tops and dark sides of the reference
# come from the lighting, never from the colours.
GRASS = "w03_grass"      # turf on every cap and bank
SOIL = "w03_soil"        # soil band under the grass, tile-edge banks
SAND = "w03_sand"        # the pool's shore collar, only above the waterline
ROCK = "w03_rock"        # every stone above the water: columns, boulders, notch wall
BED = "w03_riverbed"     # everything under a water surface: beds, shore slopes, submerged rock
WATER = "w03_water"      # the one water surface key: every flat slab and its edge skirts
LEAF = "w03_bush"        # bush and fern leaves
TINT_LO, TINT_HI = 0.90, 1.08   # clamp: every material sits at Tint 1 +-~7% (small random variation only)
# Rock Tint: one random value per rock in ROCK_TINT (never by face direction or
# height), +-1.5% per face, centred on 1.0. No material-wide factor: the rock is
# the shared sheet key w03_rock exactly, so the Roblox palette row matches the
# render (a uniform tint multiplier made the exporter's w03_rock row overflow).
ROCK_TINT = (0.96, 1.04)
SIDE_IN = 2.2      # cap side edge sits this far inside the tile; side columns stand in front of it
# the pool-side banks in front of the cliff sit low (1.2, not the sheet's 1.6) so
# the pool reads from the front camera; the 12-wide mouth seam stays at z=1.0
POOL_Z, BED_Z, BANK_Z = 1.0, 0.2, 1.2
MOUTH = 6.0        # half width of the front pool mouth
TURF = 0.45        # thickness of the green turf band on cap edges (over the soil band)
NOTCH = 1.4        # how far the rock wall behind the fall is set back from the lip
LEAN = 1.0         # the curtain beam ends this far out (-Y) from the lip, at the pool


# ---------------------------------------------------------------------------
# low-level helpers
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


_DBG = {}


def dbg(a, label):
    """WF_DEBUG=1: print the triangles added since the previous checkpoint."""
    if not os.environ.get("WF_DEBUG"):
        return
    n = sum(len(f.verts) - 2 for f in a.bm.faces)
    print(f"WF {a.name if hasattr(a, 'name') else ''} {label}: +{n - _DBG.get(id(a), 0)}")
    _DBG[id(a)] = n


def frange(a0, a1, step):
    n = max(1, int(round(abs(a1 - a0) / step)))
    return [a0 + (a1 - a0) * k / n for k in range(n + 1)]


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
        face(a, (t0, b0, b1, t1), mat, tint * a.rng.uniform(0.96, 1.04), var, out=(o[0], o[1], 0))


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
        paint(a, [f], m, t, 0.03)
    return verts


def rock_fn(rng):
    """Every rock facet is w03_rock with a small random Tint (one random value per
    rock, +-3% per face): the light bevelled tops and the dark crevices come from
    the lighting and the geometry, never from the colour."""
    t0 = rng.uniform(ROCK_TINT[0], ROCK_TINT[1])

    def fn(f):
        return ROCK, t0 * rng.uniform(0.985, 1.015)

    return fn


# ---------------------------------------------------------------------------
# rock: columns and boulders
# ---------------------------------------------------------------------------


def column(a, c, u, w, d, h, z0, all_round=True, bulge=0.45, cham=None, lean=(0.0, 0.0), breaks=None, sub=False):
    """Fat hexagonal basalt-style rock column: the hull of jittered 6-sided
    rings (a flat face or a vertical crease toward the front, at random), 1-2
    mid-height facet breaks (a ring stepped out a little, so the long faces
    kink), and a bevelled crown (the top ring inset by a ~0.8-1 chamfer all
    round, slightly tilted). c = footprint centre, u = unit vector along the
    face, front normal n = (u.y, -u.x); w along u, d along n. lean = (dx, dy)
    offset of the crown over the base (studs, world axes). sub splits every
    side face with a slightly proud mid vertex (chunkier stand-alone parts).
    all_round is kept for older calls: every crown is bevelled all round."""
    rng = a.rng
    n = (u[1], -u[0])
    hw, hd = w / 2, d / 2
    ch = cham if cham is not None else rng.uniform(0.8, 1.05)
    ch = min(ch, hw * 0.42, hd * 0.42, h * 0.3)
    # mostly a vertical crease to the front: two big front planes, one turned to
    # the sun and one away, as the sheet's columns; now and then a flat front face
    rot = (PI / 6 if rng.random() < 0.92 else 0.0) + rng.uniform(-0.16, 0.16)
    rad = [rng.uniform(0.9, 1.08) for _ in range(6)]
    nk = 12 if sub else 6
    sbump = [rng.uniform(1.0, 1.035) for _ in range(6)]

    def P(lu, lv, z):
        t = max(0.0, min(1.0, (z - z0) / max(h, 0.1)))
        return Vector((c[0] + u[0] * lu + n[0] * lv + lean[0] * t,
                       c[1] + u[1] * lu + n[1] * lv + lean[1] * t, z))

    def ring(sc=1.0, inset=0.0, dx=0.0, dy=0.0):
        out = []
        for k in range(nk):
            if sub and k % 2:
                i0, i1 = k // 2, (k // 2 + 1) % 6
                th = rot + TAU * (k / 2) / 6
                r = 0.5 * (rad[i0] + rad[i1]) * math.cos(PI / 6) * sbump[i0]
            else:
                th = rot + TAU * (k // (2 if sub else 1)) / 6
                r = rad[k // (2 if sub else 1)]
            ex, ey = (hw - inset) * sc * r, (hd - inset) * sc * r / 0.87
            out.append((math.cos(th) * ex + dx, math.sin(th) * ey + dy))
        return out

    j = 0.1
    pts = []
    zs = z0 + h - ch
    nb = breaks if breaks is not None else (2 if h > 12 else (1 if h > 4.5 else 0))
    levels = [(z0, 1.03, 0.0, 0.0)]
    fr = sorted(rng.uniform(0.3, 0.8) for _ in range(nb))
    for f in fr:
        levels.append((z0 + (zs - z0) * f, 1.0 + rng.uniform(0.03, 0.07), rng.uniform(-0.25, 0.25) * bulge * 2,
                       rng.uniform(-0.2, 0.25) * bulge * 2))
    levels.append((zs, 0.97, 0.0, 0.0))
    for z, sc, dx, dy in levels:
        for lu, lv in ring(sc, 0.0, dx, dy):
            pts.append(P(lu + rng.uniform(-j, j), lv + rng.uniform(-j, j), z + rng.uniform(-0.06, 0.06)))
    tilt = rng.uniform(-0.25, 0.25) * min(1.0, h / 3)
    for lu, lv in ring(0.97, ch):
        pts.append(P(lu, lv, z0 + h + tilt * lu / hw + rng.uniform(-0.05, 0.05)))
    return hull(a, pts, rock_fn(rng))


def boulder(a, x, y, z, s, tall=1.0, exp=0.6, n=24):
    """Rounded faceted boulder, base at z (s ~ its width)."""
    rng = a.rng
    sx, sy, sz = s * rng.uniform(1.0, 1.2) / 2, s * rng.uniform(0.85, 1.0) / 2, s * 0.92 * tall / 2
    cz = z + s * 0.32 * tall
    pts = []
    sp = lambda v: math.copysign(abs(v) ** exp, v)  # noqa: E731
    for _ in range(n):
        th = rng.uniform(0, TAU)
        ph = math.acos(rng.uniform(-1, 1))
        px, py, pz = math.sin(ph) * math.cos(th), math.sin(ph) * math.sin(th), math.cos(ph)
        r = 1 + rng.uniform(-0.1, 0.1)
        pts.append(Vector((x + sp(px) * sx * r, y + sp(py) * sy * r, max(z - 0.2, cz + sp(pz) * sz * r))))
    return hull(a, pts, rock_fn(rng), facets=6.0)


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
    paint(a, faces, mat, tint if tint is not None else a.rng.uniform(0.96, 1.04), 0.03)


def tuft(a, x, y, z, s=1.0, n=3):
    rng = a.rng
    for i in range(n):
        ang = TAU * i / n + rng.uniform(-0.5, 0.5)
        frond(a, (x + rng.uniform(-0.25, 0.25) * s, y + rng.uniform(-0.25, 0.25) * s, z - 0.05),
              ang, rng.uniform(1.0, 1.35), rng.uniform(0.8, 1.2) * s, 0.3 * s,
              GRASS, droop=0.12)


def turf(a, x, y, z, s=1.0):
    """Rounded grass mound (a flattened faceted blob) on a cap or ledge edge; set
    on a rim it drapes over it, so the grass layer reads thick and soft."""
    rng = a.rng
    a.ico((1.25 * s, 1.0 * s, 0.55 * s), loc=(x, y, z + 0.05 * s), rot=(0, 0, rng.uniform(0, PI)), subdiv=1,
          jitter=0.1, mat=GRASS, face_tint_var=0.04)


def fern(a, x, y, z, s=1.0, k=6):
    rng = a.rng
    for i in range(k):
        ang = TAU * i / k + rng.uniform(-0.25, 0.25)
        frond(a, (x, y, z - 0.05), ang, rng.uniform(0.6, 0.95), rng.uniform(1.6, 2.2) * s,
              0.8 * s, LEAF, droop=0.4)


def bush(a, x, y, z, s=1.0):
    """Round leafy w03_bush clump: two lobes round the base and a crown on top."""
    rng = a.rng
    R = 1.2 * s
    a0 = rng.uniform(0, TAU)
    for i in range(2):
        ang = a0 + PI * i + rng.uniform(-0.35, 0.35)
        r = R * rng.uniform(0.62, 0.76)
        a.ico(r, loc=(x + math.cos(ang) * R * 0.5, y + math.sin(ang) * R * 0.5, z + r * 0.7), subdiv=1,
              jitter=0.12, mat=LEAF, face_tint_var=0.05)
    r = R * rng.uniform(0.62, 0.74)
    a.ico(r, loc=(x + rng.uniform(-0.2, 0.2) * R, y + rng.uniform(-0.2, 0.2) * R, z + R * 1.0), subdiv=1,
          jitter=0.1, mat=LEAF, face_tint_var=0.05)


def star_cone(a, x, y, z, r, h, pts=8, inner=0.62, droop=0.35, mat="pine", rot=0.0):
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
    m = len(ring)
    tops, bots = [], []
    for k in range(m):
        tops.append(bm.faces.new((ring[k], ring[(k + 1) % m], apex)))
        bots.append(bm.faces.new((ring[(k + 1) % m], ring[k], cen)))
    t = rng.uniform(0.95, 1.05)
    paint(a, tops, mat, t, 0.05)
    paint(a, bots, mat, t, 0.05)


def pine(a, x, y, z, s=1.0, tiers=4):
    """Pine ~6.7*s tall: short bark trunk and stacked drooping star tiers."""
    s *= 0.8
    rng = a.rng
    a.cyl(0.42 * s, 0.32 * s, 2.2 * s, 5, loc=(x, y, z - 0.3), mat="bark")
    for k in range(tiers):
        r = (2.3 - 0.36 * k * 5 / tiers) * s
        star_cone(a, x, y, z + (1.5 + 1.15 * k * 5 / tiers) * s, r, 2.3 * s + (0.4 * s if k == tiers - 1 else 0.0),
                  pts=6 if k < 2 else 5,
                  mat="pine", rot=rng.uniform(0, PI))


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
    c = [bm.verts.new((x + math.cos(rot + TAU * i / 3) * 0.17 * s, y + math.sin(rot + TAU * i / 3) * 0.17 * s,
                       zz + 0.06 * s)) for i in range(3)]
    face(a, c, "flower_yellow", 1.0, 0.0, out=(0, 0, 1))


# ---------------------------------------------------------------------------
# water surfaces (falling water, foam, splash, mist and flow are VFX sockets)
# ---------------------------------------------------------------------------


def pool_outline(cx, cy, rx, ry, n=30, seed=0, amp=0.05):
    """Round pool (an ellipse union a 12-wide mouth channel to the front edge),
    from the right mouth corner counter-clockwise to the left mouth corner."""
    rr = random.Random(seed)
    p1, p2 = rr.uniform(0, TAU), rr.uniform(0, TAU)
    thR = math.atan2(-EDGE - cy, MOUTH - cx)
    thL = math.atan2(-EDGE - cy, -MOUTH - cx)
    if thL < thR:
        thL += TAU
    pts = []
    for k in range(n + 1):
        th = thR + (thL - thR) * k / n
        c, s = math.cos(th), math.sin(th)
        re = rx * ry / math.sqrt((ry * c) ** 2 + (rx * s) ** 2)
        re *= 1 + amp * (math.sin(3 * th + p1) + 0.6 * math.sin(5 * th + p2))
        rect = 0.0
        if s < -1e-6:
            lim = [(cy + EDGE) / -s]
            if c > 1e-6:
                lim.append((MOUTH - cx) / c)
            elif c < -1e-6:
                lim.append((-MOUTH - cx) / c)
            rect = min(lim)
        r = max(re, rect)
        pts.append((min(EDGE - 0.6, max(-EDGE + 0.6, cx + c * r)), max(-EDGE, cy + s * r)))
    pts[0] = (MOUTH, -EDGE)
    pts[-1] = (-MOUTH, -EDGE)
    return pts


def pool_water(a, loop, C, z):
    """Flat pool surface, all w03_water (the riverbed under it gives the deep
    cyan through the see-through water). Foam and splash are VFX sockets."""
    bm = a.bm
    rings = [[bm.verts.new((C[0] + (p[0] - C[0]) * s, C[1] + (p[1] - C[1]) * s, z)) for p in loop]
             for s in (1.0, 0.45)]
    n = len(loop)
    for k in range(n):
        k2 = (k + 1) % n
        face(a, (rings[0][k], rings[0][k2], rings[1][k2], rings[1][k]), WATER, 1.0, 0.0, out=(0, 0, 1))
    c = bm.verts.new((C[0], C[1], z))
    for k in range(n):
        face(a, (rings[1][k], rings[1][(k + 1) % n], c), WATER, 1.0, 0.0, out=(0, 0, 1))


def submerge(a, z, inside):
    """Cut the rock faces that cross the water level z where inside(x, y) holds
    (the pool or a channel) and paint the part under the water w03_riverbed: the
    submerged boulder and column bases read deep teal through the water."""
    bm = a.bm
    ri, bi = a._mi(ROCK), a._mi(BED)

    def cen(f):
        c = f.calc_center_median()
        return c.x, c.y

    cut = [f for f in bm.faces if f.material_index == ri and inside(*cen(f))
           and min(v.co.z for v in f.verts) < z - 0.03 and max(v.co.z for v in f.verts) > z + 0.03]
    if cut:
        geom = list(cut) + list({e for f in cut for e in f.edges}) + list({v for f in cut for v in f.verts})
        bmesh.ops.bisect_plane(bm, geom=geom, plane_co=(0, 0, z), plane_no=(0, 0, 1), dist=0.01)
    for f in bm.faces:
        if f.material_index == ri and max(v.co.z for v in f.verts) <= z + 0.02 and inside(*cen(f)):
            f.material_index = bi


# ---------------------------------------------------------------------------
# the tile
# ---------------------------------------------------------------------------


class Tier:
    """One cliff step: grass cap at `top`, water (channel / ledge pool) at `wz`
    between half-widths edge(y) from the rim (front lip, y=rim) to `back`."""

    def __init__(self, top, wz, rim, edge, back, base, amp=0.4, seed=0, steps=(), corner=(0.0, 0.0), proud=2,
                 cracks=2, fwd=1.0, shoulders=True, setback=3.4):
        self.setback = setback       # how far the rock wall behind the face columns sits under the cap
        self.top, self.wz, self.rim_y, self.back, self.base = top, wz, rim, back, base
        self.fwd = fwd               # scale of how far the face columns step out in front of the rim
        self.shoulders = shoulders   # tall grass-topped / bare rock crowns at the cap corners
        self.e = sorted(edge)
        self.amp = amp
        self.corner = corner   # how far the rim pulls back at the left / right outer corners
        self.proud = proud     # proud (stepped-forward) columns per side in front of the face
        self.cracks = cracks   # fern tufts growing out of face crevices per side
        self.hl = self.edge(rim)
        r = random.Random(seed)
        self.p1, self.p2 = r.uniform(0, TAU), r.uniform(0, TAU)
        self.steps = steps
        self.polys = []

    def edge(self, y):
        e = self.e
        if y <= e[0][0]:
            return e[0][1]
        for (y0, h0), (y1, h1) in zip(e, e[1:]):
            if y <= y1:
                return h0 + (h1 - h0) * (y - y0) / (y1 - y0)
        return e[-1][1]

    def rim(self, x):
        ramp = min(1.0, max(0.0, (abs(x) - self.hl - 0.3) / 2.5))
        f = max(0.0, (abs(x) - 8.5) / 7.5)   # outer corners recede: the sides step down in front
        pull = self.corner[0 if x < 0 else 1] * f * f
        return self.rim_y + pull + self.amp * ramp * (math.sin(0.8 * x + self.p1) + 0.5 * math.sin(2.1 * x + self.p2))


def build_tier(a, T, nxt):
    """Caps, soil bands, backing walls, channel water, the recessed notch behind
    the fall and the columns of one tier. nxt: the tier below (None = the pool).
    Returns the y where the fall meets the water below (its foot)."""
    rng = a.rng
    sx = EDGE - SIDE_IN
    wall_bot = (nxt.top - 0.8) if nxt else 0.0
    notch_bot = (nxt.wz - 0.7) if nxt else 0.0
    for side in (-1, 1):
        rim_pts = [(side * x, T.rim(side * x)) for x in frange(sx, T.hl, 1.2)]
        chan = [(side * T.edge(y), y) for y in frange(T.rim_y, T.back, 1.3)]
        poly = Poly(rim_pts + chan[1:] + [(side * sx, T.back)])
        T.polys.append(poly)
        cap(a, poly, T.top, spacing=3.2, seed=int(T.top * 10) + side, jz=0.08)
        # thick turf: a green band (the grass layer seen edge-on) over the soil band
        skirt(a, rim_pts, T.top, T.top - TURF, GRASS, (0, -1), var=0.03)
        skirt(a, rim_pts, T.top - TURF, T.top - TURF - 0.6, SOIL, (0, -1))
        # the rock wall behind the face columns is set back under the cap's soil lip
        # (a soffit closes the overhang), so the gaps between the columns are deep
        # shadowed crevices
        zs = T.top - TURF - 0.6
        sb_pts = [(x, y + T.setback) for x, y in rim_pts]
        skirt(a, sb_pts, zs, wall_bot, ROCK, (0, -1))
        if T.setback > 0.05:
            bm = a.bm
            for (x0, y0), (x1, y1) in zip(rim_pts, rim_pts[1:]):
                face(a, [bm.verts.new(p) for p in ((x0, y0, zs), (x1, y1, zs), (x1, y1 + T.setback, zs),
                                                   (x0, y0 + T.setback, zs))], ROCK, out=(0, 0, -1))
        skirt(a, chan, T.top, T.top - 0.35, GRASS, (-side, 0), var=0.03)
        skirt(a, chan, T.top - 0.35, T.wz, SOIL, (-side, 0))
        skirt(a, chan, T.wz, T.wz - 0.7, BED, (-side, 0))   # the bank under the water
        side_pts = [(side * sx, y) for y in frange(T.rim(side * sx), T.back, 2.0)]
        skirt(a, side_pts, T.top, T.top - TURF, GRASS, (side, 0), var=0.03)
        skirt(a, side_pts, T.top - TURF, T.top - TURF - 0.6, SOIL, (side, 0))
        # rounded turf mounds draping over the front rim and the side edge
        for x in frange(T.hl + 1.3, sx - 0.6, 2.8):
            xx = side * (x + rng.uniform(-0.3, 0.3))
            turf(a, xx, T.rim(xx) + 0.6, T.top, rng.uniform(1.1, 1.4))
        for y in frange(T.rim(side * sx) + 1.4, T.back - 1.2, 3.4):
            turf(a, side * (sx + 0.1), y + rng.uniform(-0.4, 0.4), T.top, rng.uniform(1.0, 1.3))
        # the rock wall behind the side columns (only seen in the crevices between them)
        skirt(a, [(side * sx, T.rim(side * sx)), (side * sx, T.back)], T.top - TURF - 0.6, 0.0, ROCK, (side, 0))
        if T.back >= EDGE - 0.01:
            bk = [(side * sx, EDGE), (side * T.edge(EDGE), EDGE)]
            skirt(a, bk, T.top, T.top - 0.6, SOIL, (0, 1))
            skirt(a, bk, T.top - 0.6, 0.0, ROCK, (0, 1))
    dbg(a, "caps+walls")
    # channel / ledge water: one flat w03_water slab over a w03_riverbed bed
    right = [(T.edge(y), y) for y in frange(T.rim_y, T.back, 1.3)]
    left = [(-x, y) for x, y in reversed(right)]
    cpoly = Poly(right + left)
    T.cpoly = cpoly
    cap(a, cpoly, T.wz, WATER, spacing=4.0, seed=int(T.wz * 7), var=0.0)
    cap(a, cpoly, T.wz - 0.7, BED, spacing=4.0, seed=3)
    if T.back >= EDGE - 0.01:
        bk = [(-T.edge(EDGE), EDGE), (T.edge(EDGE), EDGE)]
        skirt(a, bk, T.wz, T.wz - 0.7, WATER, (0, 1), var=0.0)
        skirt(a, bk, T.wz - 0.7, T.wz - 1.5, BED, (0, 1))   # tile-edge wall under the water skirt
        skirt(a, bk, T.wz - 1.5, 0.0, ROCK, (0, 1))
    lip = [(-T.hl, T.rim_y), (T.hl, T.rim_y)]
    skirt(a, lip, T.wz, T.wz - 0.7, WATER, (0, -1), var=0.0)
    # the notch behind the fall: a rock wall set back NOTCH studs under an
    # overhanging lip, so the curtain beam reads against a shadowed recess
    yb = T.rim_y + NOTCH
    hw = T.hl + 0.6
    skirt(a, [(-hw, yb), (hw, yb)], T.wz - 0.7, notch_bot, ROCK, (0, -1))
    bm = a.bm
    z1 = T.wz - 0.7
    face(a, [bm.verts.new(p) for p in ((-hw, T.rim_y, z1), (hw, T.rim_y, z1), (hw, yb, z1), (-hw, yb, z1))],
         ROCK, out=(0, 0, -1))
    for side in (-1, 1):
        skirt(a, [(side * hw, T.rim_y), (side * hw, yb)], z1, notch_bot, ROCK, (-side, 0))
    dbg(a, "channel")
    foot = T.rim_y - LEAN
    # columns along the front face: narrower prisms of mixed height (no two
    # neighbours alike), each a little yawed and leaning, staggered in depth so
    # the gaps between them read as deep dark crevices
    hs = T.top - T.base
    for side in (-1, 1):
        x = T.hl + 0.15
        k = 0
        prev = None
        seams = []
        while x < EDGE - 1.5:
            # fat hexagonal columns (5-7 wide, 2-3 a side in this row) whose oblique
            # faces meet their neighbours in deep V crevices running back to the
            # set-back wall; the outer one takes the rest of the face
            w = rng.uniform(5.0, 5.8) if k == 0 else rng.uniform(5.4, 6.8)
            if EDGE - x < w + 3.0:
                w = min(7.6, EDGE - x + 0.4)
            xc = side * (x + w / 2)
            d = rng.uniform(4.6, 5.6)
            # beside the notch: near the rim so the curtain shows; then neighbours alternate
            # proud (1.6-2.4 out, lower: a stepped ledge) and recessed (0.4-0.9 out, tall)
            if k == 0:
                fwd = 0.6
            elif k % 2:
                fwd = rng.uniform(1.6, 2.4) * T.fwd
            else:
                fwd = rng.uniform(0.4, 0.9) * T.fwd
            yc = T.rim(xc) - fwd + d / 2
            if k == 0:  # the columns framing the fall poke a little above the grass
                h = hs + rng.uniform(0.8, 1.5)
            elif k % 2:  # proud: a stepped crown a little under the rim
                opts = [o for o in (-3.2, -2.2, -1.4) if prev is None or abs(hs + o - prev) > 0.75]
                h = hs + rng.choice(opts) + rng.uniform(-0.3, 0.3)
            else:  # recessed: bevelled crown above the grass (or just under it)
                opts = [o for o in (-0.9, 0.9, 1.7, 2.5) if prev is None or abs(hs + o - prev) > 0.75]
                h = hs + rng.choice(opts) + rng.uniform(-0.2, 0.2)
            yaw = rng.uniform(-0.2, 0.2)
            lean = (side * rng.uniform(-0.2, 0.3), -rng.uniform(0.0, 0.3))
            column(a, (xc, yc), (math.cos(yaw), math.sin(yaw)), w, d, h, T.base, lean=lean)
            if k > 0 and h < hs - 0.5:
                # a low proud column's top is a ledge in front of the rim: a fern or bush grows there
                zt = T.base + h - 0.12
                yl = T.rim(xc) - fwd * 0.6 + lean[1]
                if rng.random() < 0.5:
                    fern(a, xc + lean[0], yl, zt, 1.0)
                else:
                    bush(a, xc + lean[0], yl, zt, 1.0)
            prev = h
            k += 1
            x += w + rng.uniform(0.4, 0.7)   # a narrow slot to the set-back wall: a dark crevice
            if x < EDGE - 2.0:
                seams.append(side * x)
        # proud columns stepping forward of the face (lower, mixed heights, leaning),
        # each carrying a plant on its bevelled top
        lo, hi = T.hl + 4.0, EDGE - 5.0
        xs = []
        nprd = 0 if hi < lo else (T.proud if hi - lo >= 5.0 * (T.proud - 1) else min(1, T.proud))
        for j in range(nprd):
            for _ in range(20):
                xb = rng.uniform(lo, hi)
                if all(abs(xb - o) > 5.0 for o in xs):
                    break
            xs.append(xb)
        for j, xb in enumerate(sorted(xs)):
            xb *= side
            wb, db = rng.uniform(4.6, 5.6), rng.uniform(3.8, 4.6)
            hb = hs * rng.uniform(0.38, 0.72)
            yc = T.rim(xb) - rng.uniform(3.0, 3.8) * T.fwd + db / 2
            yaw = rng.uniform(-0.2, 0.2)
            column(a, (xb, yc), (math.cos(yaw), math.sin(yaw)), wb, db, hb, T.base, all_round=True,
                   lean=(side * rng.uniform(0.0, 0.4), -rng.uniform(0.0, 0.3)))
            top = T.base + hb - 0.12
            if (j + (side > 0)) % 2 == 0:
                bush(a, xb + rng.uniform(-0.3, 0.3), yc - 0.2, top, 1.15)
            else:
                fern(a, xb, yc - 0.2, top, 0.9)
                tuft(a, xb + 0.8, yc + 0.3, top, 0.9)
        # fern tufts sprouting from the face crevices
        rng.shuffle(seams)
        for xsm in seams[:T.cracks]:
            zz = T.base + hs * rng.uniform(0.35, 0.7)
            fern(a, xsm, T.rim(xsm) - 1.0, zz, 0.95, k=5)
        # side wall columns, facing out of the tile side: alternately proud and
        # recessed, of mixed heights, with dark crevice gaps between them, so the
        # side reads as separate stacked prisms; the lower proud ones carry plants
        dbg(a, "front cols")
        y1 = T.back if T.back < EDGE - 0.01 else EDGE + 0.2
        y0 = T.rim(side * EDGE)
        span = max(1.0, min(y1, EDGE) - y0)
        # one row of narrow (3-4 wide) prisms along the tile side, alternately
        # recessed (1.3-1.7 in from the edge, full height, crowns through or above the
        # grass) and proud (at the edge, lower, stepped: a ledge with a plant), with a
        # gap between neighbours, so the side face reads as separate stacked columns
        # with deep crevices instead of one flat wall
        y = y0 - 0.3
        k = 0
        prev = None
        while y < y1 - 1.2:
            w = rng.uniform(4.8, 6.0)
            if y1 - y < w + 2.6:
                w = min(7.2, y1 - y + 0.3)
            yc = y + w / 2
            proud = k % 2 == 1
            if proud:
                d = rng.uniform(3.8, 4.6)
                outer = EDGE - rng.uniform(0.0, 0.2)
                f = (yc - y0) / span   # lower toward the front (the pool), taller at the back
                h = T.top * (0.42 + 0.3 * min(1.0, f * 1.6)) + rng.uniform(-1.0, 1.0)
                h = max(3.0, min(T.top - 2.0, h))
            else:
                d = rng.uniform(4.0, 4.8)
                outer = EDGE - rng.uniform(1.3, 1.7)
                opts = [o for o in (-0.8, 0.8, 1.6, 2.4) if prev is None or abs(T.top + o - prev) > 0.7]
                h = T.top + rng.choice(opts) + rng.uniform(-0.2, 0.2)
            column(a, (side * (outer - d / 2), yc), (0, side), w, d, h, 0.0, all_round=proud,
                   lean=(-side * rng.uniform(0.0, 0.3), rng.uniform(-0.25, 0.25)) if proud else (0.0, 0.0))
            if proud:
                px = side * (outer - d / 2 + 0.3)
                pick = (k // 2) % 3
                if pick == 0:
                    bush(a, px, yc, h - 0.15, 1.3)
                elif pick == 1:
                    fern(a, px, yc, h - 0.1, 1.2)
                else:
                    turf(a, px, yc, h - 0.05, 1.2)
                    tuft(a, px, yc + 0.6, h - 0.05, 1.1)
            prev = h
            y += w + rng.uniform(0.4, 0.65)   # a narrow slot to the side wall: a dark crevice
            k += 1
        dbg(a, "side cols")
        # ferns and tufts along the top edge of the side cap
        yr0 = T.rim(side * EDGE)
        for f in (0.15, 0.38, 0.62, 0.86):
            yy = yr0 + (min(y1, EDGE) - yr0) * f
            if f in (0.38, 0.86):
                fern(a, side * (sx - 0.6), yy, T.top, 0.85)
            else:
                tuft(a, side * (sx - 0.4), yy, T.top, 1.1)
    dbg(a, "side top plants")
    # stepped front columns (ledges)
    for (x, fwd, w, d, h, plant) in T.steps:
        yc = T.rim(x) - fwd - d / 2
        z0 = T.base if T.base > 0 else 0.0
        column(a, (x, yc), (1, 0), w, d, h, z0, all_round=True)
        top = z0 + h - 0.1
        turf(a, x, yc + 0.2, top, min(1.3, w * 0.3))
        if plant == "bush":
            bush(a, x + rng.uniform(-0.4, 0.4), yc - 0.3, top, 0.95)
        elif plant == "fern":
            fern(a, x, yc - 0.2, top, 0.85)
        elif plant == "tuft":
            tuft(a, x - 0.6, yc, top, 1.0)
            tuft(a, x + 0.7, yc - 0.4, top, 0.8)
    dbg(a, "steps")
    return foot


def build_tile(kit, name, cfg, role="variant"):
    fk = kit.flintkit
    a = fk.Asset(name, "Terrain", seed=cfg["seed"])
    rng = a.rng
    tiers = [Tier(**t) for t in cfg["tiers"]]
    feet = []
    for i, T in enumerate(tiers):
        nxt = tiers[i + 1] if i + 1 < len(tiers) else None
        feet.append(build_tier(a, T, nxt))
    dbg(a, "tiers")
    # shoulders: short rock crowns standing 1.5-3 studs above the top cap (a grass
    # mound, a pine or bare bevelled rock on top), so the cliff's top outline is
    # irregular like the sheet's instead of one flat grass line
    top_t = tiers[0]
    sh_taken = []
    for x, y, dh, kind in cfg.get("shoulders", ()):
        z0 = top_t.top - 3.0
        h = 3.0 + dh
        w, d = rng.uniform(4.6, 5.4), rng.uniform(4.2, 4.8)
        column(a, (x, y), (1, 0), w, d, h, z0, all_round=True, lean=(rng.uniform(-0.2, 0.2), 0.0))
        zt = z0 + h - 0.2
        if kind in ("grass", "pine"):
            turf(a, x, y, zt, 1.55)
            turf(a, x + rng.uniform(-0.6, 0.6), y - 0.7, zt - 0.15, 1.2)
        if kind == "pine":
            pine(a, x, y + 0.2, zt + 0.1, 0.95)
        elif kind == "grass":
            bush(a, x - 0.6, y - 0.4, zt + 0.1, 1.0)
            daisy(a, x + 0.9, y - 1.0, zt + 0.3, 1.5)
        sh_taken.append((x, y, 2.4))
    low = tiers[-1]
    socks = []   # VFX sockets: dicts of kind, loc (tile coords), scale, name, end, width
    # pool and banks
    cx, cy, rx, ry = cfg["pool"]
    pts = pool_outline(cx, cy, rx, ry, seed=cfg["seed"] + 5)
    mouth = [(x, -EDGE) for x in frange(-MOUTH, MOUTH, 2.0)][1:-1]
    loop = pts + mouth
    C = (cx, cy)
    pool_water(a, loop, C, POOL_Z)
    ppoly = Poly(loop)
    cap(a, ppoly, BED_Z, BED, spacing=4.5, seed=11)
    # the low bank round the pool reaches back under the (receding) cliff rim
    back_edge = [(x, low.rim(x) + 0.3 + low.setback) for x in frange(EDGE, -EDGE, 2.0)]
    bank = Poly([(-EDGE, -EDGE)] + list(reversed(pts)) + [(EDGE, -EDGE)] + back_edge)
    # a w03_sand collar along the pool shore, w03_grass behind it
    cap(a, bank, BANK_Z, spacing=2.4, seed=12, jz=0.06,
        matfn=lambda x, y: SAND if ppoly.dist(x, y) < 1.1 else GRASS)
    # the shore: sand only above the waterline, the slope under the water is riverbed
    skirt(a, pts, BANK_Z, POOL_Z, SAND, lambda p: (C[0] - p[0], C[1] - p[1]))
    skirt(a, pts, POOL_Z, BED_Z, BED, lambda p: (C[0] - p[0], C[1] - p[1]))
    for xs in ((-EDGE, -MOUTH), (MOUTH, EDGE)):
        skirt(a, [(xs[0], -EDGE), (xs[1], -EDGE)], BANK_Z, 0.0, SOIL, (0, -1))
    for side in (-1, 1):
        skirt(a, [(side * EDGE, -EDGE), (side * EDGE, low.rim(side * EDGE) + 0.3)], BANK_Z, 0.0, SOIL, (side, 0))
    skirt(a, [(-MOUTH, -EDGE), (MOUTH, -EDGE)], POOL_Z, BED_Z, WATER, (0, -1), var=0.0)
    skirt(a, [(-MOUTH, -EDGE), (MOUTH, -EDGE)], BED_Z, 0.0, BED, (0, -1))

    dbg(a, "pool+banks")
    def ground(x, y):
        for T in tiers:
            if any(p.inside(x, y) for p in T.polys):
                return T.top
        if bank.inside(x, y):
            return BANK_Z
        return None

    # boulders: in the pool (a water_foam socket rings each), on banks or caps
    nf = 0
    for x, y, s in cfg.get("boulders", ()):
        g = ground(x, y)
        if g is None:
            boulder(a, x, y, BED_Z + 0.1, s, n=18 if s > 2.0 else 14)
            nf += 1
            socks.append(dict(kind="water_foam", loc=(x, y - 0.25 * s, POOL_Z + 0.05),
                              scale=round(min(1.1, max(0.5, 0.3 * s)), 2), name=f"VFX_PoolFoam_{nf}"))
        else:
            boulder(a, x, y, g - 0.3, s, tall=0.85)
    for x, y, s in cfg.get("foot_rocks", ()):   # small rubble at the cliff foot (no foam socket)
        g = ground(x, y)
        boulder(a, x, y, (g - 0.15) if g is not None else BED_Z + 0.1, s, tall=0.8, n=12)
    nc = 0
    for T, rocks in zip(tiers, cfg.get("chan_rocks", ())):
        for x, y, s in rocks:
            boulder(a, x, y, T.wz - 0.7, s, tall=0.9)
            nc += 1
            socks.append(dict(kind="water_foam", loc=(x, y - 0.3 * s, T.wz + 0.05), scale=0.4,
                              name=f"VFX_ChannelFoam_{nc}"))
    # submerged rock (pool boulders, column feet in the pool, channel rocks) is riverbed
    submerge(a, POOL_Z, lambda x, y: ppoly.sdist(x, y) > -0.3)
    for T in tiers:
        submerge(a, T.wz, lambda x, y, T=T: T.cpoly.sdist(x, y) > -0.3)
    dbg(a, "boulders")
    # vegetation
    taken = list(sh_taken)
    # plants and rubble only where there is ground (never floating on the pool);
    # the cliff-top pines are ~20% bigger than the foot ones, as on the sheet
    makers = (("pines", lambda x, y, g, s: pine(a, x, y, g, min(s, 1.0) * (1.15 if g > BANK_Z else 1.0)), 1.8),
              ("bushes", lambda x, y, g, s: bush(a, x, y, g, s), 1.2),
              ("ferns", lambda x, y, g, s: fern(a, x, y, g, s), 1.0),
              ("rubble", lambda x, y, g, s: boulder(a, x, y, g - 0.15, s, tall=0.75, n=12), 0.8))
    for key, make, rad in makers:
        for x, y, s in cfg.get(key, ()):
            g = ground(x, y)
            if g is None:
                print(f"WF {name}: skipped {key} at ({x}, {y}): no ground")
                continue
            make(x, y, g, s)
            taken.append((x, y, rad))
    dbg(a, "veg")
    # daisies and tufts scattered near the cap rims and on the banks
    polys = [(p, T.top) for T in tiers for p in T.polys] + [(bank, BANK_Z)]
    for poly, z in polys:
        x0, y0, x1, y1 = poly.bbox()
        nd = cfg.get("daisies", 6) if z > BANK_Z else cfg.get("bank_daisies", 3)
        placed, tries = 0, 0
        while placed < nd and tries < 400:
            tries += 1
            x, y = rng.uniform(x0, x1), rng.uniform(y0, y1)
            sd = poly.sdist(x, y)
            if sd < 0.6 or sd > (4.0 if z > BANK_Z else 2.5) or abs(x) > EDGE - 0.8:
                continue
            if z == BANK_Z and y > low.rim_y - 1.0:
                continue
            if z > BANK_Z and y > y0 + 6.0 and rng.random() < 0.75:
                continue  # most cap daisies along the front rims, facing the camera
            if any((x - px) ** 2 + (y - py) ** 2 < r * r for px, py, r in taken):
                continue
            daisy(a, x, y, z, rng.uniform(1.5, 1.85))
            if rng.random() < 0.3:
                tuft(a, x + rng.uniform(-0.8, 0.8), y + rng.uniform(-0.8, 0.8), z, 0.8)
            taken.append((x, y, 0.9))
            placed += 1
    dbg(a, "daisies")
    if os.environ.get("WF_DEBUG"):
        print(f"WF {name}: {sum(len(f.verts) - 2 for f in a.bm.faces)} tris")
    socks += water_sockets(cfg, tiers, feet)
    return a, socks


def curtain_beams():
    """The stock waterfall_curtain beams tinted the sheet's bright cyan (the
    sheet's curtain is cyan with white streaks, not white): same texture, widths
    and speeds, only the colour sequences change."""
    import vfx
    beams = json.loads(json.dumps(vfx.KINDS["waterfall_curtain"]["beams"]))
    beams[0]["color"] = ["#1CC6FA", "#08A8EC"]           # body: saturated sheet cyan, top to bottom
    beams[0]["transparency"] = [0.0, 0.0, 0.1]
    beams[0]["light_emission"] = 0.15
    beams[1]["color"] = ["#FFFFFF", "#A8ECFD"]           # sheen: the white streaks
    beams[1]["transparency"] = [0.7, 0.6, 0.8]
    return beams


def water_sockets(cfg, tiers, feet):
    """The falling and flowing water as VFX (never meshes), in tile coordinates.
    Per lip: waterfall_curtain beams (VFX_WaterfallCurtain_N) from just in front
    of the lip down to the water below, leaning out LEAN; at each foot a
    waterfall_mist (VFX_WaterfallSplash, the sheet's splash disc), a vapour haze
    and a ring of water_foam (VFX_WaterfallFoamRibbon_N, the foam ribbon); water_flow
    beams lie on the cliff-top channel, the mid ledge pool and the pool to the mouth."""
    out = []
    nc = nr = 0
    last = len(tiers) - 1
    for i, T in enumerate(tiers):
        low = i == last
        fz = POOL_Z if low else tiers[i + 1].wz
        foot = feet[i]
        xs, w = cfg["falls"][i]
        for x in xs:
            nc += 1
            out.append(dict(kind="waterfall_curtain", loc=(x, T.rim_y - 0.25, T.wz + 0.05), scale=1.0,
                            name=f"VFX_WaterfallCurtain_{nc}", end=(x, foot, fz), width=w,
                            over=dict(beams=curtain_beams())))
        tag = "" if low else "_Mid"
        mist, vaps = cfg["mist"][i]
        out.append(dict(kind="waterfall_mist", loc=(0.0, foot - 0.4, fz + 0.5), scale=mist,
                        name=f"VFX_WaterfallSplash{tag}"))
        for j, (vx, vs) in enumerate(vaps):
            out.append(dict(kind="vapour", loc=(vx, foot - 1.2, fz + 2.0), scale=vs,
                            name=f"VFX_WaterfallVapour{tag}" + (f"_{j + 1}" if len(vaps) > 1 else "")))
        hw = max(xs) - min(xs) + w   # the fall's full width
        # foam ribbon: a half ring of water_foam sockets round the impact zone, in front of the face
        nring = cfg["foam_ring"][i]
        rx, ry = hw / 2 + 1.0, 3.2 if low else 2.2
        for k in range(nring):
            th = PI + PI * k / (nring - 1)
            nr += 1
            out.append(dict(kind="water_foam", loc=(rx * math.cos(th), foot - 0.3 + ry * math.sin(th), fz + 0.05),
                            scale=0.7, name=f"VFX_WaterfallFoamRibbon_{nr}"))
        # flow on the water this fall drains: the channel (or ledge basin) behind the lip
        fw = cfg["flow_w"][i]
        out.append(dict(kind="water_flow", loc=(0.0, T.back, T.wz + 0.03), scale=1.0,
                        name=f"VFX_WaterfallFlow_{'Channel' if i == 0 else 'Ledge'}",
                        end=(0.0, T.rim_y, T.wz + 0.03), width=fw))
    # pool: flow from the impact zone out through the mouth, foam along the rim and the mouth sides
    out.append(dict(kind="water_flow", loc=(0.0, feet[-1] - 2.0, POOL_Z + 0.03), scale=1.0,
                    name="VFX_WaterfallFlow_Pool", end=(0.0, -EDGE, POOL_Z + 0.03), width=10.0))
    cx, cy, rx, ry = cfg["pool"]
    rim = [(-MOUTH - 0.6, -EDGE + 0.8), (MOUTH + 0.6, -EDGE + 0.8),
           (cx - rx * 0.86, cy + ry * 0.25), (cx + rx * 0.86, cy + ry * 0.25),
           (cx - rx * 0.8, cy - ry * 0.45), (cx + rx * 0.8, cy - ry * 0.45), (cx - rx * 0.45, cy + ry * 0.75),
           (cx + rx * 0.45, cy + ry * 0.75)]
    for k, (x, y) in enumerate(rim):
        out.append(dict(kind="water_foam", loc=(x, y, POOL_Z + 0.05), scale=0.8, name=f"VFX_PoolRimFoam_{k + 1}"))
    return out


def finish(kit, a, role, collision, budget, notes, sockets=()):
    """Clamp to the tile (nothing outside +-16 or below z=0), write the mesh,
    tag it and attach VFX sockets (dicts with locs/ends in tile coordinates)."""
    for v in a.bm.verts:
        v.co.x = min(max(v.co.x, -EDGE), EDGE)
        v.co.y = min(max(v.co.y, -EDGE), EDGE)
        v.co.z = max(v.co.z, 0.0)
    for f in a.bm.faces:  # Tint is a small random variation: keep it within +-8%
        for lp in f.loops:
            t = min(TINT_HI, max(TINT_LO, lp[a.tint_layer][0]))
            lp[a.tint_layer] = (t, t, t, 1.0)
    xs = [v.co.x for v in a.bm.verts]
    ys = [v.co.y for v in a.bm.verts]
    zs = [v.co.z for v in a.bm.verts]
    off = ((min(xs) + max(xs)) / 2, (min(ys) + max(ys)) / 2, min(zs))
    obj = a.finish()
    kit.tag(obj, role, collision=collision, budget=budget, notes=notes)

    def rel(p):
        return (p[0] - off[0], p[1] - off[1], p[2] - off[2])

    for s in sockets:
        kw = {}
        if s.get("end") is not None:
            kw["end"] = rel(s["end"])
        if s.get("width") is not None:
            kw["width"] = s["width"]
        kw.update(s.get("over", {}))
        kit.vfx.add(obj, s["kind"], rel(s["loc"]), scale=s.get("scale", 1.0), name=s.get("name"), **kw)
    return obj


# ---------------------------------------------------------------------------
# configurations
# ---------------------------------------------------------------------------

HERO = dict(
    seed=3201,
    tiers=[dict(top=20.5, wz=20.0, rim=-1.0, edge=[(-1.0, 4.0), (16.0, 4.0)], back=16.0, base=0.0, seed=1,
                corner=(4.6, 3.6), proud=1, cracks=4,
                steps=[(-13.6, 0.3, 4.6, 4.0, 11.0, "bush"), (-9.6, 0.6, 4.4, 3.8, 6.5, "fern"),
                       (13.8, 0.2, 4.4, 4.0, 6.0, "fern"), (10.0, 0.5, 4.4, 3.8, 9.5, "bush")])],
    pool=(0.0, -8.8, 17.5, 7.6),
    boulders=[(-6.4, -12.6, 3.8), (7.2, -12.8, 3.6), (-11.8, -9.0, 2.6), (12.2, -9.6, 2.4),
              (13.2, -13.6, 1.8), (2.0, -14.6, 1.5), (-2.2, -11.8, 1.3), (-12.2, -13.4, 1.6), (4.0, -10.2, 1.2)],
    chan_rocks=[[(-3.2, 9.0, 1.7), (3.0, 4.5, 1.5)]],
    pines=[(-11.0, 8.5, 1.15), (-6.8, 11.5, 1.05), (-13.0, 2.6, 1.0), (10.0, 9.5, 1.15), (13.0, 3.0, 1.0),
           (7.0, 13.0, 1.05), (-14.4, -14.6, 1.05), (-12.0, -15.2, 0.75)],
    bushes=[(-6.3, -0.4, 0.9), (-9.6, 4.6, 0.85), (6.4, 0.2, 0.85), (10.6, 0.6, 0.9), (-15.0, -12.4, 0.8),
            (-6.2, 6.4, 0.8), (-11.6, -0.6, 0.8), (-12.8, 12.4, 0.75), (12.8, -0.8, 0.8),
            (-5.2, 9.4, 0.75), (5.3, 5.8, 0.8), (12.4, 7.0, 0.8),
            (14.6, -14.4, 0.8), (-8.6, 0.6, 0.95), (8.8, 1.0, 0.95)],
    ferns=[(-14.6, -15.0, 0.8), (8.0, 6.0, 0.8), (-8.6, 0.6, 0.75), (-12.6, 6.0, 0.75), (8.6, 2.6, 0.75),
           (11.0, 13.4, 0.7), (-7.4, 9.6, 0.7), (13.6, -15.2, 0.7), (-14.8, -4.4, 0.7), (14.8, -4.2, 0.7)],
    rubble=[(-8.4, -15.4, 0.9), (9.6, -15.4, 1.0), (11.4, -15.0, 0.7), (-15.2, -13.8, 0.8),
            (-10.6, 2.2, 0.9), (11.8, 4.6, 0.8)],
    daisies=16, bank_daisies=7,
)
HERO["boulders"] += [(-5.7, 3.4, 2.4), (5.8, 9.2, 2.2), (-5.9, 14.6, 1.8)]
# fuller leafy clumps, as on the sheet; the ones along the front rims (facing the camera) biggest
HERO["bushes"] = [(x, y, s + (0.55 if y < 1.5 else 0.25)) for x, y, s in HERO["bushes"]]


def push_back(cfg, new_rim):
    """Move a single-tier tile's cliff face back to rim y=new_rim, squeezing the
    cap items (and the channel edge profile) between the new rim and the back
    edge, so the pool in front gets deeper (the sheet's top view: cap ~45%)."""
    t = cfg["tiers"][0]
    old = t["rim"]

    def m(y):
        return new_rim + (y - old) * (EDGE - new_rim) / (EDGE - old) if y > old - 0.6 else y

    t["rim"] = new_rim
    t["edge"] = [(m(y), h) for y, h in t["edge"]]
    for key in ("pines", "bushes", "ferns", "rubble", "boulders"):
        cfg[key] = [(x, m(y), s) for x, y, s in cfg.get(key, ())]
    cfg["chan_rocks"] = [[(x, m(y), s) for x, y, s in rocks] for rocks in cfg.get("chan_rocks", ())]


push_back(HERO, 1.0)
# a big round pool ~30 x 16.4 filling the front ~45% of the tile out to the side
# edges, small land wedges left only at the front corners and the cliff-foot banks
HERO["pool"] = (0.0, -7.4, 15.0, 8.2)
# rubble round the cliff foot (in the shallows and on the side banks) and leafy
# clumps with daisies along the foot of the wall
HERO["foot_rocks"] = [(-5.6, -1.4, 1.3), (-8.4, -2.6, 1.0), (-10.4, -1.8, 1.4), (5.4, -1.2, 1.2), (8.0, -2.4, 1.1),
                      (10.8, -1.4, 1.3), (-12.8, -3.0, 1.0), (13.0, -3.4, 0.9), (-3.6, -2.4, 0.8),
                      (3.8, -2.6, 0.9)]
HERO["bushes"] += [(-13.6, -1.6, 1.0), (13.8, -1.2, 1.0), (-14.6, -6.0, 0.9), (14.8, -6.4, 0.9)]
HERO["bank_daisies"] = 10
HERO["rubble"] += [(-9.6, -0.2, 1.0), (-10.8, -1.6, 0.7), (10.2, -0.4, 0.9), (15.0, -2.2, 0.8), (-15.0, -3.6, 0.9)]
# the corner pines become pines on raised grass shoulders; bare rock crowns at the back corners
HERO["pines"] = [p for p in HERO["pines"] if not (abs(p[0]) > 12.5 and 3.0 < p[1] < 6.0)]
HERO["shoulders"] = [(-12.4, 5.0, 1.7, "pine"), (12.6, 5.6, 1.8, "grass"), (-10.0, 14.4, 1.6, "rock"),
                     (12.2, 14.2, 2.2, "rock"), (-7.2, 8.4, 1.0, "rock")]
HERO["bushes"] = [b for b in HERO["bushes"] if not (abs(b[0] + 6.2) < 1.5 and abs(b[1] - 7.4) < 1.5)]
HERO["bushes"] += [(-5.4, 12.8, 1.0), (8.2, 12.0, 1.0), (-13.0, 9.6, 1.0), (13.0, 11.2, 0.95), (5.6, 15.0, 0.9)]
HERO["daisies"] = 24

NARROW = dict(
    seed=3211,
    tiers=[dict(top=20.5, wz=20.0, rim=-1.6, edge=[(-1.6, 2.0), (1.6, 2.6), (6.0, 4.0), (16.0, 4.0)], back=16.0,
                base=0.0, seed=2, corner=(3.4, 3.6), proud=0,
                steps=[(-7.6, 0.8, 4.2, 3.2, 14.0, "fern"), (-12.4, 0.6, 4.4, 3.2, 10.0, "bush"),
                       (7.6, 0.9, 4.2, 3.2, 13.0, "bush"), (12.6, 0.6, 4.4, 3.2, 8.0, "fern")])],
    pool=(0.0, -9.0, 14.5, 7.0),
    boulders=[(-4.6, -12.6, 3.0), (5.4, -12.0, 3.0), (-8.6, -8.6, 2.2), (8.6, -9.4, 2.0), (-1.0, -15.0, 1.5)],
    chan_rocks=[[(-3.0, 9.5, 1.5), (2.9, 6.0, 1.4)]],
    pines=[(-10.0, 9.0, 1.3), (-6.0, 12.5, 1.0), (9.5, 8.0, 1.2), (12.5, 13.0, 1.0), (-13.5, -12.0, 0.95)],
    bushes=[(-4.4, 0.0, 0.8), (5.0, 1.0, 0.85), (-12.0, 2.0, 0.8), (13.6, -12.8, 0.8), (-14.0, -6.6, 0.8)],
    ferns=[(12.6, 3.4, 0.8), (14.5, -6.2, 0.75)],
    daisies=5, bank_daisies=4,
)
NARROW["boulders"] += [(-4.6, 5.0, 2.0), (5.2, 10.6, 2.0)]
push_back(NARROW, -0.2)
NARROW["shoulders"] = [(-12.6, 6.0, 2.0, "grass"), (12.4, 5.2, 1.7, "pine"), (-11.0, 14.4, 1.6, "rock")]
NARROW["daisies"] = 8
NARROW["pool"] = (0.0, -8.2, 13.6, 7.6)

WIDE = dict(
    seed=3221,
    tiers=[dict(top=20.5, wz=20.0, rim=-1.2, edge=[(-1.2, 8.0), (4.0, 6.6), (10.0, 4.4), (16.0, 4.0)],
                back=16.0, base=0.0, seed=3, corner=(3.0, 3.6), proud=0,
                steps=[(-10.6, 2.0, 4.4, 3.6, 12.0, "bush"), (-14.2, 1.2, 3.6, 3.4, 7.0, "fern"),
                       (10.6, 2.2, 4.4, 3.6, 10.5, "fern"), (14.2, 1.2, 3.6, 3.4, 6.0, "bush")])],
    pool=(0.0, -8.6, 16.5, 7.4),
    boulders=[(-6.8, -12.8, 3.4), (7.2, -12.4, 3.4), (-12.2, -7.4, 2.4), (12.4, -7.6, 2.6), (0.4, -15.0, 1.6),
              (-3.2, -14.4, 1.5)],
    chan_rocks=[[(-5.6, 2.6, 1.6), (5.2, 4.2, 1.5)]],
    pines=[(-10.6, 8.5, 1.3), (-13.0, 13.0, 1.05), (11.0, 9.0, 1.3), (8.0, 13.4, 1.0), (13.8, 3.4, 0.95),
           (-14.4, -13.0, 0.9)],
    bushes=[(-9.4, 0.6, 0.85), (9.6, 0.0, 0.85), (-13.6, 4.0, 0.8), (14.6, -13.4, 0.8)],
    ferns=[(-6.8, 7.0, 0.8), (7.4, 5.4, 0.8)],
    daisies=6, bank_daisies=3,
)
WIDE["boulders"] += [(-7.6, 3.6, 2.0), (7.4, 9.0, 2.0)]
push_back(WIDE, 0.2)
WIDE["pines"] = [p for p in WIDE["pines"] if not (p[0] > 13 and p[1] < 6)]
WIDE["shoulders"] = [(-12.8, 5.0, 1.7, "pine"), (12.6, 4.8, 1.5, "pine"), (11.6, 14.6, 1.8, "rock")]
WIDE["daisies"] = 8
WIDE["pool"] = (0.0, -7.8, 15.3, 7.8)

TWOSTEP = dict(
    seed=3231,
    tiers=[dict(top=20.5, wz=20.0, rim=2.6, edge=[(2.6, 3.0), (6.0, 3.4), (16.0, 4.0)], back=16.0, base=11.4,
                seed=4, steps=[], proud=0, cracks=1, setback=0.5),
           dict(top=11.5, wz=11.0, rim=-4.8, edge=[(-4.8, 3.0), (-3.6, 5.6), (-1.0, 6.6), (1.0, 6.0), (3.2, 3.6)],
                back=3.2, base=0.0, seed=5, amp=0.3, corner=(1.4, 1.0), proud=0, cracks=1, fwd=0.7,
                steps=[(-8.6, 1.4, 4.4, 3.4, 6.5, "fern"), (9.0, 1.4, 4.4, 3.4, 5.5, "bush")])],
    pool=(0.0, -10.6, 14.2, 5.4),
    boulders=[(-5.6, -13.2, 3.0), (6.0, -13.0, 2.8), (-9.4, -8.6, 2.2), (9.8, -9.0, 2.2), (0.6, -15.2, 1.5)],
    chan_rocks=[[(-2.9, 11.0, 1.4), (2.9, 7.4, 1.3)], [(-4.0, -3.9, 1.6), (4.0, -4.0, 1.5)]],
    pines=[(-10.0, 9.6, 1.25), (-6.5, 13.0, 1.0), (10.0, 10.0, 1.2), (13.0, 5.4, 0.95), (-13.8, -12.6, 0.85)],
    bushes=[(-6.4, 4.4, 0.8), (6.6, 5.0, 0.8), (-8.0, -2.4, 0.8), (8.6, -1.6, 0.85), (12.6, 0.6, 0.8),
            (14.4, -13.4, 0.75)],
    ferns=[(-14.4, -7.0, 0.75)],
    daisies=7, bank_daisies=3,
    shoulders=[(-12.4, 7.0, 2.2, "grass"), (12.0, 13.6, 1.6, "rock")],
)


# per tier: curtain sockets (x positions, beam width), (mist, vapour) scales, channel flow width
# mist = (waterfall_mist scale, [(vapour x, vapour scale), ...]); foam_ring = foam ribbon sockets per foot
HERO.update(falls=[((-2.0, 2.0), 4.5)], mist=[(1.4, [(0.0, 1.1)])], flow_w=[7.0], foam_ring=[8])
NARROW.update(falls=[((0.0,), 4.0)], mist=[(1.0, [(0.0, 0.8)])], flow_w=[3.5], foam_ring=[6])
WIDE.update(falls=[((-6.0, -2.0, 2.0, 6.0), 4.5)], mist=[(1.8, [(-4.0, 1.2), (4.0, 1.2)])], flow_w=[14.0],
            foam_ring=[10])
TWOSTEP.update(falls=[((-1.4, 1.4), 3.5), ((-1.4, 1.4), 3.5)], mist=[(1.1, [(0.0, 0.9)]), (1.2, [(0.0, 0.9)])],
               flow_w=[5.5, 6.0], foam_ring=[6, 7])

VFX_NOTES = ("VFX (water is never a mesh): VFX_WaterfallCurtain_N = waterfall_curtain beams from the lip to the "
             "pool (the sheet's 'Waterfall Mesh (Curtain)'); VFX_WaterfallFoamRibbon_N = a ring of water_foam round "
             "the fall foot (the 'Foam Ribbon'); VFX_WaterfallSplash = waterfall_mist where the fall lands (the "
             "'Splash Disc'); VFX_WaterfallVapour = vapour spray haze above the foot; VFX_PoolFoam_N = water_foam "
             "ringing each pool boulder; VFX_PoolRimFoam_N = water_foam along the pool rim and mouth sides; "
             "VFX_ChannelFoam_N = water_foam at the channel rocks; VFX_WaterfallFlow_Channel / _Pool = water_flow "
             "streaks on the cliff-top channel (back edge -> lip) and the pool (foot -> mouth).")


def build_hero(kit):
    a, socks = build_tile(kit, "WaterfallModule", HERO)
    return finish(kit, a, "hero", "precise", 8000,
                  "32x32 waterfall tile: 8-wide river in at the back centre (z=20), split curtain over an 8-wide "
                  "notched lip into a round pool (z=1.0) leaving by a 12-wide mouth at the front centre. Precise "
                  "for the walkable cliff top, ledges and pool rim (water exports non-colliding). " + VFX_NOTES,
                  socks)


def build_narrow(kit):
    a, socks = build_tile(kit, "WaterfallNarrow", NARROW)
    return finish(kit, a, "variant", "precise", 8000,
                  "Narrow Fall (Single): ~4-wide notch, one curtain beam (width 4), smaller pool; same seams. "
                  + VFX_NOTES, socks)


def build_wide(kit):
    a, socks = build_tile(kit, "WaterfallWide", WIDE)
    return finish(kit, a, "variant", "precise", 8000,
                  "Wide Fall (Single): ~16-wide lip, four curtain beams side by side (width 4.5 each), wide pool, "
                  "mist 1.8 + two vapour sockets (VFX_WaterfallVapour_1/_2), a 10-socket foam ribbon; same seams. "
                  + VFX_NOTES, socks)


def build_twostep(kit):
    a, socks = build_tile(kit, "WaterfallTwoStep", TWOSTEP)
    return finish(kit, a, "variant", "precise", 8000,
                  "Two-Step Fall (Multi Tier): upper curtain (lip y=2.6) into a mid ledge basin (w03_water z=11.0 over riverbed) held by a "
                  "rock lip, lower curtain (lip y=-4.8) into the bottom pool; the _Mid splash/vapour sockets and "
                  "VFX_WaterfallFlow_Ledge sit on the ledge pool. " + VFX_NOTES, socks)


# ---------------------------------------------------------------------------
# parts
# ---------------------------------------------------------------------------


def part_top_water(kit):
    """Flat cliff-top channel slab, as in the hero (top z=20.0 on a bed at 19.3):
    w03_water with a light shallow band along both banks. The flow streaks and
    the fall are sockets: water_flow along the slab, waterfall_curtain at its
    front (-Y) lip, ending at the slab base for the part preview."""
    a = kit.flintkit.Asset("WaterfallTopWaterPlane", "Terrain", seed=3241)
    # one tileable 8-wide channel section, 2.6 long (lay several end to end): the
    # smallest footprint of the parts, so the parts cell sets it in its front row
    # w03_water slab (top 0.7) over its w03_riverbed bed (top 0.2, seen through
    # the water) as in the hero's channel; skirts: water down to the bed, riverbed below
    L, H, B = 1.3, 0.7, 0.2
    ring = [(-4.0, -L), (4.0, -L), (4.0, L), (-4.0, L), (-4.0, -L)]
    bm = a.bm
    face(a, [bm.verts.new((x, y, H)) for x, y in ring[:4]], WATER, var=0.0, out=(0, 0, 1))
    face(a, [bm.verts.new((x, y, B)) for x, y in ring[:4]], BED, var=0.03, out=(0, 0, 1))
    for p, q in zip(ring, ring[1:]):
        mid = ((p[0] + q[0]) / 2, (p[1] + q[1]) / 2)
        skirt(a, [p, q], H, B, WATER, (mid[0], mid[1]), var=0.0)
        skirt(a, [p, q], B, 0.0, BED, (mid[0], mid[1]))
    face(a, [bm.verts.new((x, y, 0.0)) for x, y in ring[:4]], BED, var=0.03, out=(0, 0, -1))
    # the curtain socket ends at the slab's own base level here (in the hero it runs on to the pool)
    socks = [dict(kind="water_flow", loc=(0.0, L - 0.2, H + 0.03), end=(0.0, -L + 0.2, H + 0.03), width=7.0,
                  name="VFX_WaterfallFlow_Channel"),
             dict(kind="waterfall_curtain", loc=(-2.0, -L - 0.25, H + 0.05), end=(-2.0, -L - 1.0, 0.0),
                  width=4.5, name="VFX_WaterfallCurtain_1", over=dict(beams=curtain_beams())),
             dict(kind="waterfall_curtain", loc=(2.0, -L - 0.25, H + 0.05), end=(2.0, -L - 1.0, 0.0),
                  width=4.5, name="VFX_WaterfallCurtain_2", over=dict(beams=curtain_beams()))]
    return finish(kit, a, "part", "none", 400,
                  "flat channel water slab section 8 wide x 2.6 long (w03_water over its w03_riverbed bed), "
                  "tileable end to end along the channel (see-through water, no collision). The sheet's "
                  "'Waterfall Mesh (Curtain)', 'Foam Ribbon' and 'Splash Disc' are not meshes: they are the "
                  "waterfall_curtain, water_foam and waterfall_mist (+vapour) sockets. VFX: VFX_WaterfallFlow_Channel "
                  "= water_flow streaks along the slab toward the lip; VFX_WaterfallCurtain_1/_2 = two waterfall_curtain "
                  "beams (x=-2/+2, width 4.5) from the front lip, their ends at the slab base (move the end down to the pool when the slab "
                  "is placed on a cliff).", socks)


def part_cliff_top(kit):
    a = kit.flintkit.Asset("WaterfallCliffTop", "Terrain", seed=3242)
    rng = a.rng
    H = 5.0
    pts = []
    for k in range(20):
        th = TAU * k / 20
        c, s = math.cos(th), math.sin(th)
        # a cliff-top strip ~7 x 3.2: its footprint is smaller than the wall pieces'
        # and bigger than the water slab's, so the parts grid puts the tall walls in
        # the back row and this block and the slab in front, each in clear view
        r = 1.0 / max(abs(c) / 3.6, abs(s) / 1.6) ** 1.0
        r = min(r, 7.2) * (1 + 0.03 * math.sin(3 * th + 1.0))
        pts.append((c * r * 0.97, s * r * 0.97))
    poly = Poly(pts)
    cap(a, poly, H, spacing=2.4, seed=4, jz=0.08)
    loop = [(p.x, p.y) for p in poly.p] + [(poly.p[0].x, poly.p[0].y)]
    skirt(a, loop, H, H - TURF, GRASS, lambda m: (m[0], m[1]), var=0.03)
    skirt(a, loop, H - TURF, H - TURF - 0.5, SOIL, lambda m: (m[0], m[1]))
    skirt(a, loop, H - TURF - 0.5, 0.6, ROCK, lambda m: (m[0], m[1]))
    for x, w in ((-2.3, 2.6), (0.2, 2.4), (2.5, 2.4)):
        column(a, (x, -0.1), (1, 0), w, 2.8, H - 0.55 - rng.uniform(0.0, 0.5), 0.0, all_round=True)
    for x, y, s in ((-2.2, 0.4, 0.85), (2.0, 0.3, 0.8)):
        bush(a, x, y, H, s)
    fern(a, 0.1, 0.2, H, 0.65)
    for x, y in ((-0.9, -0.9), (0.9, 0.9), (1.4, -0.8), (-3.0, -0.6), (3.0, -0.7), (-0.8, 0.9)):
        daisy(a, x, y, H, rng.uniform(1.0, 1.2))
    for x, y in ((-1.4, -0.4), (2.9, 0.6)):
        tuft(a, x, y, H, 0.8)
    return finish(kit, a, "part", "precise", 4000, "grass-capped cliff-top block (w03_grass turf over a w03_soil "
                  "band, columnar w03_rock sides) with w03_bush bushes and ferns and daisies; precise so players "
                  "can walk on it")


def part_wall(kit, name, w, d, h, seed):
    """A fat hexagonal wall column (each side face split by a proud mid vertex,
    1-2 mid-height facet breaks, bevelled crown) with a chunk of fallen rubble
    leaning on its foot, as the sheet's cliff wall pieces."""
    a = kit.flintkit.Asset(name, "Terrain", seed=seed)
    column(a, (0.0, 0.0), (1, 0), w, d, h, 0.0, breaks=3 if h > 8 else 2, cham=0.85, bulge=0.9)
    rng = a.rng
    side = rng.choice((-1, 1))
    boulder(a, side * w * 0.45, -d * 0.55, 0.0, rng.uniform(1.6, 2.0), tall=0.8, n=14)
    boulder(a, -side * w * 0.2, -d * 0.62, 0.0, rng.uniform(1.0, 1.3), tall=0.75, n=12)
    boulder(a, -side * w * 0.52, -d * 0.3, 0.0, rng.uniform(0.8, 1.0), tall=0.7, n=10)
    boulder(a, side * w * 0.05, -d * 0.75, 0.0, rng.uniform(0.6, 0.8), tall=0.7, n=10)
    return finish(kit, a, "part", "hull", 1500, f"fat hexagonal columnar cliff wall piece ~{h:.0f} tall with a "
                  "bevelled crown and a rubble chunk at its foot; stand in rows along a cliff face")


def build(kit):
    # The sheet's 'Waterfall Mesh (Curtain)', 'Foam Ribbon' and 'Splash Disc' are VFX sockets on the hero and
    # variants (VFX_WaterfallCurtain_N, VFX_WaterfallFoamRibbon_N, VFX_WaterfallSplash), not part meshes.
    # w03_water keeps flintkit's default see-through value (shared by the whole
    # sheet); the w03_riverbed under it gives the deep saturated cyan.
    # Parts-cell layout: the runner's grid packs larger footprints first (left to
    # right, then rows toward the camera). The walls have the largest footprints
    # (A > B > C), so the tall ones fill the back row; the low cliff top and the
    # flat water slab (smallest) follow in the front rows, each in clear view.
    return [build_hero(kit),
            part_top_water(kit), part_cliff_top(kit),
            part_wall(kit, "WaterfallCliffWallA", 6.4, 5.4, 14.0, 3251),
            part_wall(kit, "WaterfallCliffWallB", 6.0, 5.2, 10.0, 3252),
            part_wall(kit, "WaterfallCliffWallC", 5.5, 4.9, 6.0, 3253),
            build_narrow(kit), build_wide(kit), build_twostep(kit)]
