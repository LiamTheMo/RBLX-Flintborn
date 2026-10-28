"""R05 row 3: FiberShrub - spiky lance-leaf shrub crowned with golden fibre tufts."""
import math

from mathutils import Vector

SUBJECT = "FiberShrub"
ROW = 3
HERO_AZIMUTH = -22

PALETTE = {
    "r05_bark": ("#7A5030", 0.9, 0, 0),  # trunks, forks, branches, stems and stumps for BerryShrub, FiberShrub, ThornShrub
    "r05_fiber_leaf": ("#2E7A24", 0.85, 0, 0),  # FiberShrub long pointed leaves (deeper green)
    "r05_fiber": ("#E2B878", 0.85, 0, 0),  # FiberShrub fibre tufts and bundles (golden cream tan)
}

LEAF = "r05_fiber_leaf"
BARK = "r05_bark"
FIBER = "r05_fiber"


# --------------------------------------------------------------------------- helpers

def _dir(az_deg, el_deg):
    az, el = math.radians(az_deg), math.radians(el_deg)
    return Vector((math.cos(el) * math.cos(az), math.cos(el) * math.sin(az), math.sin(el)))


def _frame(d):
    """Width axis (horizontal, perpendicular to d) and normal axis."""
    d = d.normalized()
    up = Vector((0, 0, 1))
    w = d.cross(up)
    if w.length < 1e-4:
        w = Vector((1, 0, 0))
    w.normalize()
    n = w.cross(d).normalized()
    return d, w, n


def lance_leaf(a, base, az, el, length, width, thick, mat=LEAF, bend=0.12, twist=0.0):
    """Faceted spear leaf: diamond cross-section (edges + raised midrib top and
    bottom) so the crease splits each side into big facets."""
    bm = a.bm
    d, w, n = _frame(_dir(az, el))
    base = Vector(base)
    stations = [(0.0, 0.12), (0.17, 0.74), (0.42, 1.0), (0.66, 0.86), (0.86, 0.46)]
    rings = []
    roll = 0.8 * w.y  # turn the broad face toward the front (-Y)
    for t, s in stations:
        c = base + d * (length * t) - n * (bend * length * t * t)
        ang = roll + twist * t
        ww = w * math.cos(ang) + n * math.sin(ang)
        nn = n * math.cos(ang) - w * math.sin(ang)
        hw = width * 0.5 * s
        ht = thick * 0.5 * (0.35 + 0.65 * s)
        rings.append([
            bm.verts.new(c + ww * hw),
            bm.verts.new(c + nn * ht),
            bm.verts.new(c - ww * hw),
            bm.verts.new(c - nn * ht * 0.6),
        ])
    tip = bm.verts.new(base + d * length - n * (bend * length))
    root = bm.verts.new(base - d * 0.12)
    for r0, r1 in zip(rings, rings[1:]):
        for i in range(4):
            j = (i + 1) % 4
            bm.faces.new((r0[i], r0[j], r1[j], r1[i]))
    last = rings[-1]
    for i in range(4):
        bm.faces.new((last[i], last[(i + 1) % 4], tip))
    first = rings[0]
    for i in range(4):
        bm.faces.new((first[(i + 1) % 4], first[i], root))
    verts = [v for r in rings for v in r] + [tip, root]
    return a._finish(verts, mat)


def blade(a, base, d, length, width, thick, mat, widest=0.45):
    """Narrow sharp diamond spike from base along direction d (closed)."""
    bm = a.bm
    d, w, n = _frame(Vector(d))
    base = Vector(base)
    c = base + d * (length * widest)
    ring = [bm.verts.new(c + w * width * 0.5), bm.verts.new(c + n * thick * 0.5),
            bm.verts.new(c - w * width * 0.5), bm.verts.new(c - n * thick * 0.5)]
    tip = bm.verts.new(base + d * length)
    root = bm.verts.new(base)
    for i in range(4):
        j = (i + 1) % 4
        bm.faces.new((ring[i], ring[j], tip))
        bm.faces.new((ring[j], ring[i], root))
    return a._finish(ring + [tip, root], mat)


def segment(a, p1, p2, r1, r2, mat=BARK, sides=6, cap1=True, cap2=True, rot0=0.0):
    """Tapered faceted log between two points with flat cut ends."""
    bm = a.bm
    p1, p2 = Vector(p1), Vector(p2)
    d = (p2 - p1).normalized()
    ref = Vector((0, 0, 1)) if abs(d.z) < 0.9 else Vector((1, 0, 0))
    u = d.cross(ref).normalized()
    v = d.cross(u).normalized()
    ring1, ring2 = [], []
    for i in range(sides):
        ang = rot0 + 2 * math.pi * i / sides
        off = u * math.cos(ang) + v * math.sin(ang)
        ring1.append(bm.verts.new(p1 + off * r1))
        ring2.append(bm.verts.new(p2 + off * r2))
    for i in range(sides):
        j = (i + 1) % sides
        bm.faces.new((ring1[i], ring1[j], ring2[j], ring2[i]))
    if cap1:
        bm.faces.new(list(reversed(ring1)))
    if cap2:
        bm.faces.new(ring2)
    return a._finish(ring1 + ring2, mat)


def fiber_tuft(a, base, scale=1.0, tilt=(0.0, 0.0), spikes=8, seed=0, cup=True):
    """Golden star tuft: an inner ring of tall blades and an outer ring of
    splayed blades, on a small green sepal cup."""
    base = Vector(base)
    tx, ty = tilt
    s = scale
    if cup:
        segment(a, base + Vector((0, 0, -0.15 * s)), base + Vector((tx * 0.2, ty * 0.2, 0.3 * s)),
                0.16 * s, 0.34 * s, mat=LEAF, sides=5)
        for k in range(5):
            az = 72 * k + 20 + seed * 13
            dd = _dir(az, 28)
            blade(a, base + Vector((0, 0, 0.12 * s)), dd, 0.55 * s, 0.32 * s, 0.1 * s, LEAF, 0.4)
    top = base + Vector((tx * 0.25, ty * 0.25, 0.25 * s))
    n_in = max(3, spikes // 2 - 1)
    n_out = spikes - n_in
    for k in range(n_in):
        az = 360.0 * k / n_in + seed * 31
        dd = _dir(az, 72) + Vector((tx, ty, 0))
        blade(a, top, dd, 1.5 * s, 0.6 * s, 0.2 * s, FIBER)
    for k in range(n_out):
        az = 360.0 * (k + 0.5) / n_out + seed * 31
        dd = _dir(az, 38 + 6 * ((k + seed) % 2)) + Vector((tx * 0.5, ty * 0.5, 0))
        blade(a, top, dd, 1.1 * s, 0.55 * s, 0.18 * s, FIBER)


# --------------------------------------------------------------------------- assets

# (azimuth deg, elevation deg, length, width) ; azimuth -90 = front (-Y)
HERO_LEAVES = [
    (90, 80, 6.2, 2.1),     # back centre, tallest
    (55, 72, 5.7, 2.0),
    (125, 72, 5.7, 2.0),
    (22, 64, 5.0, 1.75),    # mid uprights flanking the tufts
    (158, 64, 5.0, 1.75),
    (5, 44, 3.5, 1.8),      # sides
    (175, 44, 3.5, 1.8),
    (-35, 30, 3.4, 1.7),    # front-side, splaying low
    (-145, 30, 3.4, 1.7),
    (68, 30, 3.6, 1.7),     # back-low (gives the ring its depth)
    (112, 32, 3.6, 1.7),
]


def build_hero(kit):
    fk, vfx = kit.flintkit, kit.vfx
    a = fk.Asset("FiberShrub", "R05 FiberShrub")
    # leaves all round the trunk; none straight in front so the stems show
    for i, (az, el, ln, wd) in enumerate(HERO_LEAVES):
        b = _dir(az, 0) * 0.6
        lance_leaf(a, (b.x, b.y, 0.3 + 0.1 * (i % 3)), az, el, ln, wd, 0.75,
                   twist=0.25 * (1 if i % 2 else -1))
    # thick trunk forking ~1.2 up into three tuft stems and a cut back stub
    segment(a, (0, 0, 0), (0, 0, 0.35), 0.95, 0.82, sides=7)
    segment(a, (0, 0, 0.3), (0, -0.05, 1.25), 0.82, 0.7, sides=7, rot0=0.2)
    centre = [(0.05, -0.1, 1.1), (0.1, -0.35, 2.2), (0.1, -0.45, 3.2)]
    left = [(-0.3, -0.1, 1.1), (-0.9, -0.4, 1.9), (-1.3, -0.55, 2.6)]
    right = [(0.3, -0.1, 1.1), (0.95, -0.35, 2.0), (1.35, -0.5, 2.75)]
    for path, r in ((centre, 0.5), (left, 0.46), (right, 0.46)):
        segment(a, path[0], path[1], r, r * 0.85)
        segment(a, path[1], path[2], r * 0.82, r * 0.62, rot0=0.4)
    segment(a, (-0.1, 0.25, 1.1), (-0.45, 0.9, 2.3), 0.38, 0.3)   # cut stub at the back
    segment(a, (0.95, -0.35, 2.0), (1.35, 0.15, 2.55), 0.22, 0.17)  # small side fork
    # tufts crowning the three stems
    fiber_tuft(a, centre[-1], 1.4, (0.0, -0.05), spikes=9, seed=1)
    fiber_tuft(a, left[-1], 1.25, (-0.25, -0.1), spikes=8, seed=2)
    fiber_tuft(a, right[-1], 1.25, (0.25, -0.1), spikes=8, seed=3)
    o = a.finish()
    vfx.add(o, "harvest_hit", (0, -1.5, 3.5), scale=0.5, color=["#E2B878", "#2E7A24"])
    vfx.add(o, "harvest_deplete", (0, 0, 0.4), scale=0.3)
    return kit.tag(o, "hero", collision="hull", budget=3000,
                   notes="Fibre shrub resource node. harvest_hit = tan/green fibre burst on the tufts "
                         "when struck; harvest_deplete = burst at the base when trimmed to the stump.")


def build_leaf(kit):
    a = kit.flintkit.Asset("FiberShrubLeaf", "R05 FiberShrub part")
    lance_leaf(a, (0, 0, 0.3), 0, 12, 4.6, 1.7, 0.8, bend=0.04, twist=0.2)
    o = a.finish()
    return kit.tag(o, "part", collision="none", budget=1500, notes="Single lance leaf.")


def build_tuft(kit):
    a = kit.flintkit.Asset("FiberShrubFiberTuft", "R05 FiberShrub part")
    fiber_tuft(a, (0, 0, 0.15), 1.1, spikes=9, seed=1)
    o = a.finish()
    return kit.tag(o, "part", collision="none", budget=1500,
                   notes="Golden fibre tuft on a green sepal cup.")


def build_fork(kit):
    a = kit.flintkit.Asset("FiberShrubStemFork", "R05 FiberShrub part")
    segment(a, (0, 0, 0), (0, 0, 0.35), 0.7, 0.48, sides=7)
    segment(a, (0, 0, 0.2), (0.1, 0, 1.4), 0.56, 0.48, sides=7)
    segment(a, (0.0, 0, 1.15), (-1.0, -0.1, 2.9), 0.44, 0.32, sides=6, rot0=0.3)
    segment(a, (0.15, 0, 1.1), (1.15, 0.1, 2.5), 0.4, 0.3, sides=6, rot0=0.2)
    o = a.finish()
    return kit.tag(o, "part", collision="box", budget=1500, notes="Y-shaped stem fork.")


def _bundle(a, base, az, tilt_el, s=1.0):
    """Fan of tan spikes bound at a cut stub; lies tilted along azimuth az."""
    base = Vector(base)
    ax = _dir(az, tilt_el)
    stub_end = base + ax * 0.45 * s
    segment(a, base, stub_end, 0.13 * s, 0.17 * s, mat=FIBER, sides=6)
    d, w, n = _frame(ax)
    for k in range(8):
        f = (k - 3.5) / 3.5
        dd = d + w * (0.75 * f) + n * (0.35 * (1 - abs(f)) - 0.05)
        ln = (1.05 - 0.25 * abs(f)) * s
        blade(a, stub_end - ax * 0.1 * s, dd, ln, 0.38 * s, 0.15 * s, FIBER, 0.4)


def build_bundle(kit):
    a = kit.flintkit.Asset("FiberShrubFiberBundle", "R05 FiberShrub drop")
    _bundle(a, (-1.1, 0, 0.24), 20, 35)
    _bundle(a, (0.7, 0.1, 0.24), 30, 35)
    o = a.finish()
    return kit.tag(o, "drop", collision="none", budget=300, notes="Two fibre bundles (x2) in one mesh.")


DEPLETED_LEAVES = [(10, 30, 2.5), (80, 38, 2.4), (150, 28, 2.6), (-130, 24, 2.4), (-40, 26, 2.5)]


def build_depleted(kit):
    fk, vfx = kit.flintkit, kit.vfx
    a = fk.Asset("FiberShrubDepleted", "R05 FiberShrub depleted")
    for i, (az, el, ln) in enumerate(DEPLETED_LEAVES):
        b = _dir(az, 0) * 0.4
        lance_leaf(a, (b.x, b.y, 0.2), az, el, ln, 1.4, 0.55, bend=0.1,
                   twist=0.25 * (1 if i % 2 else -1))
    segment(a, (0, 0, 0), (0, 0, 0.25), 0.78, 0.62, sides=7)
    segment(a, (0, 0, 0.2), (0, 0, 1.2), 0.6, 0.55, sides=7)
    o = a.finish()
    return kit.tag(o, "depleted", collision="box", budget=2000,
                   notes="Trimmed stump with short leaves (the hero's harvest_deplete plays on the swap).")


def build(kit):
    return [
        build_hero(kit),
        build_leaf(kit),
        build_tuft(kit),
        build_fork(kit),
        build_bundle(kit),
        build_depleted(kit),
    ]
