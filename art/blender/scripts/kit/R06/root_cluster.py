"""R06 row 4: RootCluster resource node (dirt mound with arching roots)."""
import math
import random

from mathutils import Vector

SUBJECT = "RootCluster"
ROW = 4
HERO_AZIMUTH = -22

PALETTE = {
    "r06_cutwood": ("#E0B27C", 0.85, 0, 0),
    "r06_rootbark": ("#9A6540", 0.9, 0, 0),
    "r06_dirt": ("#6A5047", 0.95, 0, 0),
    "r06_leaf": ("#3F9A2C", 0.7, 0, 0),
}

CHIPS = ["#9A6540", "#E0B27C"]
DIRT = ["#6A5047", "#8A6E62"]


# ---------------------------------------------------------------- helpers

def _catmull(pts, steps):
    """Smooth a control polyline (Catmull-Rom), `steps` samples per span."""
    p = [Vector(x) for x in pts]
    ext = [p[0] * 2 - p[1]] + p + [p[-1] * 2 - p[-2]]
    out = []
    for i in range(1, len(ext) - 2):
        p0, p1, p2, p3 = ext[i - 1], ext[i], ext[i + 1], ext[i + 2]
        for s in range(steps):
            t = s / steps
            t2, t3 = t * t, t * t * t
            out.append(0.5 * ((2 * p1) + (-p0 + p2) * t + (2 * p0 - 5 * p1 + 4 * p2 - p3) * t2
                              + (-p0 + 3 * p1 - 3 * p2 + p3) * t3))
    out.append(p[-1])
    return out


def _frame(t):
    up = Vector((0, 0, 1)) if abs(t.z) < 0.9 else Vector((1, 0, 0))
    n = t.cross(up).normalized()
    b = n.cross(t).normalized()
    return n, b


def root(a, ctrl, r0, r1, sides=6, steps=3, tip_a=True, tip_b=True, cut_a=False,
         mat="r06_rootbark", end_mat="r06_cutwood", rng=None):
    """Tapered faceted root along smoothed control points.

    tip_*: end finishes in a pale chamfered (pencil) tip with a diagonal cut face.
    cut_*: end is a flat pale cut face (log end) instead.
    Returns nothing (materials assigned immediately)."""
    rng = rng or random.Random(3)
    bm = a.bm
    pts = _catmull(ctrl, steps)
    n = len(pts)
    rings = []
    for i, p in enumerate(pts):
        t = (pts[min(i + 1, n - 1)] - pts[max(i - 1, 0)]).normalized()
        nn, bb = _frame(t)
        f = i / (n - 1)
        r = r0 + (r1 - r0) * f
        r *= 1.0 + rng.uniform(-0.06, 0.06)
        ph = 0.3 * i
        ring = [bm.verts.new(p + r * (math.cos(2 * math.pi * j / sides + ph) * nn
                                      + math.sin(2 * math.pi * j / sides + ph) * bb))
                for j in range(sides)]
        rings.append((ring, p, t, r))

    bark_faces, pale_faces = [], []

    def add_tip(ring, p, t, r, sign):
        # chamfered pale tip: a smaller ring a bit further out, then a diagonal cap
        nn, bb = _frame(t)
        d = t * sign
        cut_n = (d + 0.9 * (-bb if sign > 0 else bb)).normalized()
        tip = []
        for j, v in enumerate(ring):
            off = v.co - p
            q = p + d * (0.75 * r) + off * 0.62
            tip.append(bm.verts.new(q))
        # tilt the tip ring onto a diagonal plane
        c = p + d * (0.75 * r)
        for v in tip:
            k = (v.co - c).dot(cut_n)
            v.co -= d * (k / max(0.3, d.dot(cut_n)))
        m = len(ring)
        faces = []
        for j in range(m):
            if sign > 0:
                faces.append(bm.faces.new((ring[j], tip[j], tip[(j + 1) % m], ring[(j + 1) % m])))
            else:
                faces.append(bm.faces.new((tip[j], ring[j], ring[(j + 1) % m], tip[(j + 1) % m])))
        cap = bm.faces.new(tip if sign > 0 else list(reversed(tip)))
        faces.append(cap)
        return faces, tip

    m = sides
    for i in range(n - 1):
        r1_, r2_ = rings[i][0], rings[i + 1][0]
        for j in range(m):
            bark_faces.append(bm.faces.new((r1_[j], r2_[j], r2_[(j + 1) % m], r1_[(j + 1) % m])))
    extra = []
    ring0, p0, t0, rr0 = rings[0]
    ringN, pN, tN, rrN = rings[-1]
    if tip_a:
        fs, vs = add_tip(ring0, p0, t0, rr0, -1)
        pale_faces += fs
        extra += vs
    else:
        f = bm.faces.new(list(reversed(ring0)))
        (pale_faces if cut_a else bark_faces).append(f)
    if tip_b:
        fs, vs = add_tip(ringN, pN, tN, rrN, 1)
        pale_faces += fs
        extra += vs
    else:
        bark_faces.append(bm.faces.new(ringN))
    verts = [v for rg in rings for v in rg[0]] + extra
    a._finish(verts, mat)
    mi = a._mi(end_mat)
    for f in pale_faces:
        f.material_index = mi
    return verts


def leaf(a, base, direction, length=1.2, width=0.5, lift=0.4, mat="r06_leaf"):
    """One pointed, creased leaf blade (closed, 8 tris)."""
    bm = a.bm
    d = Vector(direction)
    d.z = 0
    d.normalize()
    side = Vector((-d.y, d.x, 0))
    base = Vector(base)
    up = Vector((0, 0, 1))
    tipv = base + d * length + up * (lift * length)
    mid = base + d * (length * 0.45) + up * (lift * length * 0.55)
    L = mid + side * (width / 2) - up * 0.06
    R = mid - side * (width / 2) - up * 0.06
    T = mid + up * 0.09
    B = mid - up * 0.03
    vb, vt, vl, vr, vT, vB = (bm.verts.new(x) for x in (base, tipv, L, R, T, B))
    for f in ((vb, vl, vT), (vb, vT, vr), (vT, vl, vt), (vT, vt, vr),
              (vb, vB, vl), (vb, vr, vB), (vB, vt, vl), (vB, vr, vt)):
        bm.faces.new(f)
    verts = [vb, vt, vl, vr, vT, vB]
    a._finish(verts, mat)
    return verts


def leaf_clump(a, loc, count=6, size=1.0, rng=None, stem=0.25):
    rng = rng or random.Random(7)
    x, y, z = loc
    if stem:
        a.cyl(0.07 * size, 0.06 * size, stem * size, sides=4, loc=(x, y, z), mat="r06_leaf")
    zc = z + stem * size
    off = rng.uniform(0, 6.28)
    for k in range(count):
        ang = off + 2 * math.pi * k / count + rng.uniform(-0.2, 0.2)
        d = (math.cos(ang), math.sin(ang), 0)
        leaf(a, (x, y, zc), d, length=size * rng.uniform(1.05, 1.3), width=size * 0.95,
             lift=rng.uniform(0.35, 0.65))
    # one upright centre leaf
    leaf(a, (x, y, zc), (math.cos(off + 1), math.sin(off + 1), 0), length=size * 0.8,
         width=size * 0.45, lift=1.3)



# ------------------------------------------------------------ dirt mound

def surf(x, y, w=5.5, d=4.5, h=4.0):
    """Approximate height of the lumpy mound's envelope at (x, y)."""
    rho2 = (x / w) ** 2 + (y / d) ** 2
    if rho2 >= 1:
        return 0.0
    return h * (1 - rho2) ** 0.42


def mound(a, w, d, h, n_peb=10, top_pebbles=2, seed=1):
    """Lumpy stony dirt mound from many overlapping faceted rock blobs plus
    pebble bumps (all one r06_dirt).  w, d = full width/depth, h = height."""
    rng = random.Random(seed)
    hw, hd = w / 2, d / 2
    k = h / 4.0
    # core
    a.rock((w * 0.72, d * 0.72, h / 0.75), loc=(0, 0, 0), rot=(0, 0, rng.uniform(0, 3)),
           mat="r06_dirt", subdiv=2, rough=0.1, facets=8, sink=0.5)
    # inner ring of large lumps (carry the upper slope)
    n1 = 6
    for i in range(n1):
        ang = 2 * math.pi * i / n1 + rng.uniform(-0.25, 0.25) + 0.3
        rr = rng.uniform(0.42, 0.52)
        x, y = math.cos(ang) * hw * rr, math.sin(ang) * hd * rr
        top = surf(x, y, hw, hd, h) * rng.uniform(0.98, 1.06)
        s = rng.uniform(3.6, 4.4) * k
        a.rock((s, s * 0.85, top / 0.85), loc=(x, y, 0), rot=(0, 0, rng.uniform(0, 3)),
               mat="r06_dirt", subdiv=2, rough=0.07, facets=9, sink=0.3)
    # outer ring of lumps (skirt)
    n2 = 9
    for i in range(n2):
        ang = 2 * math.pi * i / n2 + rng.uniform(-0.2, 0.2)
        rr = rng.uniform(0.72, 0.8)
        x, y = math.cos(ang) * hw * rr, math.sin(ang) * hd * rr
        top = max(0.9, surf(x, y, hw, hd, h) * rng.uniform(1.0, 1.15))
        s = rng.uniform(2.6, 3.3) * min(1.0, k * 1.1)
        a.rock((s, s * 0.85, top / 0.85), loc=(x, y, 0), rot=(0, 0, rng.uniform(0, 3)),
               mat="r06_dirt", subdiv=1, rough=0.08, facets=8, sink=0.3)
    # pebble bumps round the base
    for i in range(n_peb):
        ang = 2 * math.pi * i / n_peb + rng.uniform(-0.25, 0.25)
        x, y = math.cos(ang) * hw * 0.95, math.sin(ang) * hd * 0.95
        s = rng.uniform(1.1, 1.6)
        a.rock((s * rng.uniform(0.9, 1.2), s, s * 0.7), loc=(x, y, 0),
               rot=(0, 0, rng.uniform(0, 3)), mat="r06_dirt", subdiv=1, rough=0.1,
               facets=8, sink=0.3)
    # a few pebbles embedded higher on the mound
    for i in range(top_pebbles):
        ang = rng.uniform(0, 6.28) if i else -1.9
        rr = rng.uniform(0.35, 0.6)
        x, y = math.cos(ang) * hw * rr, math.sin(ang) * hd * rr
        s = rng.uniform(1.0, 1.3)
        z = surf(x, y, hw, hd, h) - s * 0.25
        a.rock((s, s * 0.9, s * 0.7), loc=(x, y, z), rot=(0, 0, rng.uniform(0, 3)),
               mat="r06_dirt", subdiv=1, rough=0.1, facets=8, sink=0.2)


def clamp_floor(a):
    for v in a.bm.verts:
        if v.co.z < 0:
            v.co.z = 0.0


def surf_path(pts2d, lifts, r, w=5.5, d=4.5, h=4.0):
    """First point dives into the mound, middle points ride the surface plus
    `lifts`, last point is the tip just above the ground past the edge."""
    out = []
    n = len(pts2d)
    for k, ((x, y), L) in enumerate(zip(pts2d, lifts)):
        if k == n - 1:
            out.append((x, y, r * 1.0))
        elif k == 0:
            out.append((x, y, max(r, surf(x, y, w, d, h) - r * 0.6)))
        else:
            out.append((x, y, surf(x, y, w, d, h) + r * 0.15 + L))
    return out


# Hero roots: (path, lifts, radius).  Deliberately asymmetric; R1 lies on top of
# R2 at the crown, R4 lies on top of R1 on the back-right.
ROOTS = [
    # R1 big front root: from the back over the crown (lying ON R2), down the front
    ([(0.8, 2.8), (0.4, 1.2), (-0.1, 0.1), (-0.7, -1.9), (-1.0, -3.2), (-1.1, -4.6)],
     [0, 0.1, 0.55, 0.2, 0.05, 0], 1.0, True),
    # R2: from the upper left across the crown, curving round the right shoulder to front-right
    ([(-2.6, 1.6), (-1.2, 0.6), (0.4, 0.1), (2.2, -0.4), (3.4, -1.4), (4.2, -2.9)],
     [0, 0.05, 0.0, 0.1, 0.0, 0], 0.92, True),
    # R3: across the front-left shoulder, sweeping round to the left side, tip on the slope
    ([(0.8, -1.0), (-1.0, -1.9), (-2.8, -1.8), (-4.1, -0.8), (-4.7, 0.6)],
     [0, 0.2, 0.15, 0.05, 0.0], 0.88, False),
    # R4: crown over R2, down the back-right to the ground
    ([(-0.6, 0.0), (1.0, 1.0), (2.6, 1.8), (3.7, 2.4), (4.5, 3.0)],
     [0, 0.5, 0.2, 0.05, 0], 0.88, True),
    # R5: back-left root reaching the ground at the back
    ([(0.6, 0.9), (-1.2, 2.0), (-2.7, 2.6), (-3.8, 3.2)],
     [0, 0.15, 0.05, 0], 0.82, True),
]


# ------------------------------------------------------------------ build

def build(kit):
    fk, vfx = kit.flintkit, kit.vfx
    out = []

    # ---- hero
    a = fk.Asset("RootCluster", "R06 RootCluster", tint_var=0.05)
    mound(a, 11, 9, 4.0, n_peb=10, top_pebbles=3, seed=1)
    rng = random.Random(11)
    for pts, lifts, r, ground in ROOTS:
        path = surf_path(pts, lifts, r)
        if not ground:   # tip ends on the slope instead of the ground
            x, y = pts[-1]
            path[-1] = (x, y, surf(x, y) + r * 0.2)
        root(a, path, r, r * 0.8, sides=7, steps=3, tip_a=False, tip_b=True, rng=rng)
    leaf_clump(a, (0.9, 0.6, surf(0.9, 0.6) + 0.35), count=7, size=1.7, rng=rng)
    leaf_clump(a, (2.4, 1.0, surf(2.4, 1.0) + 0.4), count=6, size=1.5, rng=rng)
    leaf_clump(a, (-3.4, -0.4, surf(-3.4, -0.4) + 0.5), count=6, size=1.55, rng=rng)
    clamp_floor(a)
    o = a.finish()
    vfx.add(o, "harvest_hit", (0, -4, 2.5), color=CHIPS)
    vfx.add(o, "harvest_deplete", (0, 0, 0.5), color=DIRT)
    out.append(kit.tag(o, "hero", collision="hull", budget=5000,
                       notes="Root cluster resource node: lumpy dirt mound with thick crossing roots. "
                             "VFX: harvest_hit on the front root arch (wood chips, rootbark/cutwood); "
                             "harvest_deplete at mound base centre (dirt). Not glossy, no glint, no light."))

    # ---- parts
    a = fk.Asset("RootClusterDirtMound", "R06 RootClusterDirtMound", tint_var=0.04)
    mound(a, 10, 8, 4.0, n_peb=7, top_pebbles=2, seed=3)
    clamp_floor(a)
    o = a.finish()
    out.append(kit.tag(o, "part", collision="hull", budget=1500, notes="Lumpy faceted dirt mound alone."))

    a = fk.Asset("RootClusterRoot", "R06 RootClusterRoot")
    arch = [(-2.6, 0, 0.75), (-2.2, 0, 1.9), (-1.1, 0, 2.45), (0.5, 0, 2.3),
            (1.9, 0, 1.55), (2.7, 0, 0.9), (3.1, 0, 0.5)]
    root(a, arch, 0.82, 0.55, sides=7, steps=3, tip_a=True, tip_b=True, rng=random.Random(5))
    clamp_floor(a)
    o = a.finish()
    out.append(kit.tag(o, "part", collision="hull", budget=1500,
                       notes="Single thick asymmetric arched root, pale cut tips."))

    a = fk.Asset("RootClusterLeafModule", "R06 RootClusterLeafModule")
    leaf_clump(a, (0, 0, 0), count=6, size=1.35, rng=random.Random(9), stem=0.35)
    o = a.finish()
    out.append(kit.tag(o, "part", collision="none", budget=1500, notes="Pointed leaf sprout clump."))

    # ---- depleted
    a = fk.Asset("RootClusterExposedMound", "R06 RootClusterExposedMound", tint_var=0.04)
    mound(a, 11, 9, 3.0, n_peb=7, top_pebbles=1, seed=5)
    clamp_floor(a)
    o = a.finish()
    out.append(kit.tag(o, "depleted", collision="hull", budget=2000,
                       notes="Exposed lumpy dirt mound left after the roots are harvested."))

    # ---- drops: logs laid diagonally so the pale front cut end faces the camera
    a = fk.Asset("RootClusterRootBundle", "R06 RootClusterRootBundle")
    a.beam((-1.0, -1.0, 0.62), (1.05, 1.0, 0.45), 0.45, sides=7,
           mat="r06_rootbark", end_mat="r06_cutwood")
    clamp_floor(a)
    o = a.finish()
    out.append(kit.tag(o, "drop", collision="box", budget=300, notes="Root bundle pickup."))

    a = fk.Asset("RootClusterRootBundleForked", "R06 RootClusterRootBundleForked")
    a.beam((-1.0, -1.0, 0.58), (1.05, 1.0, 0.42), 0.42, sides=7,
           mat="r06_rootbark", end_mat="r06_cutwood")
    a.beam((0.1, 0.1, 0.45), (0.35, 1.45, 0.4), 0.28, sides=6,
           mat="r06_rootbark", end_mat="r06_cutwood")
    clamp_floor(a)
    o = a.finish()
    out.append(kit.tag(o, "drop", collision="box", budget=300, notes="Forked root bundle pickup."))
    return out
