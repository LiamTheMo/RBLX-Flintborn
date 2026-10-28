"""V01 row 1: CloverPatch - low clump of three-leaf clover with cream flower heads."""
import math
import random

from mathutils import Matrix, Vector

SUBJECT = "CloverPatch"
ROW = 1
HERO_AZIMUTH = -22
PALETTE = {
    "v01_clover_leaf": ("#2E9A3A", 0.85, 0, 0),  # Clover leaflets (saturated mid green; lighting makes tops brighter)
    "v01_stem": ("#4C9230", 0.85, 0, 0),  # Stems/stalks/joints of every plant
    "v01_brown": ("#8A5530", 0.9, 0, 0),  # Root bases (all plants) and sedge seed spikes
    "v01_cream": ("#EFE6CF", 0.8, 0, 0),  # Clover flower petals and dandelion seed puff
}

LEAF, STEM, BROWN, CREAM = "v01_clover_leaf", "v01_stem", "v01_brown", "v01_cream"
UP = Vector((0, 0, 1))


def _rot_to(d):
    """Euler that turns local +Z onto direction d."""
    return UP.rotation_difference(Vector(d).normalized()).to_euler()


def _cone(a, p1, p2, r1, r2, sides=5, mat=BROWN):
    p1, p2 = Vector(p1), Vector(p2)
    d = p2 - p1
    return a.cyl(r1, r2, d.length, sides=sides, loc=p1, rot=_rot_to(d), mat=mat)


def _leaflet(a, M, L, W, t, cup=0.08, keel=0.05, notch=True, mat=LEAF):
    """Thick faceted heart leaflet. Local: point at origin, runs along +Y, top +Z.
    M is the 4x4 placement matrix."""
    hw = W / 2
    right = [(0.30 * hw * 2, 0.33), (0.50 * hw * 2, 0.66), (0.43 * hw * 2, 0.92), (0.20 * hw * 2, 1.0)]
    if notch:
        mid = [(0.0, 0.88)]
    else:
        right = [(0.26 * hw * 2, 0.28), (0.44 * hw * 2, 0.58), (0.38 * hw * 2, 0.85), (0.16 * hw * 2, 0.99)]
        mid = [(0.0, 1.04)]
    pts = [(0.0, 0.0)] + right + mid + [(-x, y) for x, y in reversed(right)]
    pts = [(x, y * L) for x, y in pts]
    bm = a.bm
    top, bot = [], []
    for x, y in pts:
        lift = cup * min(1.0, abs(x) / hw) + cup * 0.5 * (y / L) ** 2
        top.append(bm.verts.new(M @ Vector((x, y, t / 2 + lift))))
        bot.append(bm.verts.new(M @ Vector((x, y, -t / 2 + lift))))
    ct = bm.verts.new(M @ Vector((0, 0.55 * L, t / 2 + cup * 0.1)))
    cb = bm.verts.new(M @ Vector((0, 0.55 * L, -t / 2 - keel)))
    n = len(pts)
    for i in range(n):
        j = (i + 1) % n
        bm.faces.new((ct, top[i], top[j]))
        bm.faces.new((cb, bot[j], bot[i]))
        bm.faces.new((bot[i], bot[j], top[j], top[i]))
    verts = top + bot + [ct, cb]
    return a._finish(verts, mat)


def _module(a, rng, top, tilt, tilt_az, L, stem_from=None, joint=0.08, yaw0=None):
    """Three leaflets joined at `top`, plane tilted by `tilt` toward azimuth `tilt_az`.
    Optional stem from `stem_from` with a bent joint."""
    top = Vector(top)
    axis = Vector((-math.sin(tilt_az), math.cos(tilt_az), 0))
    R = Matrix.Rotation(tilt, 4, axis) if tilt else Matrix.Identity(4)
    yaw0 = rng.uniform(0, 2 * math.pi) if yaw0 is None else yaw0
    for k in range(3):
        yaw = yaw0 + k * 2 * math.pi / 3 + rng.uniform(-0.18, 0.18)
        pitch = rng.uniform(0.08, 0.32)
        s = rng.uniform(0.9, 1.08)
        M = (Matrix.Translation(top) @ R @ Matrix.Rotation(yaw, 4, "Z")
             @ Matrix.Rotation(pitch, 4, "X"))
        _leaflet(a, M, L * s, L * s * 1.15, L * 0.22, cup=L * 0.15, keel=L * 0.08)
    if stem_from is not None:
        _stem(a, rng, stem_from, top, joint)


def _stem(a, rng, p0, p1, joint=0.08, r=0.045, rseg=5):
    p0, p1 = Vector(p0), Vector(p1)
    mid = p0.lerp(p1, 0.5)
    side = Vector((rng.uniform(-1, 1), rng.uniform(-1, 1), 0))
    if side.length > 1e-4:
        side.normalize()
    mid += side * joint * (p1 - p0).length
    a.tube_loop([p0, mid, p1], r, mat=STEM, rseg=rseg, closed=False)


def _flower(a, c, scale=1.0, stem_from=None, rng=None):
    """Domed head of petal wedges centred at c (head base ~0.12*scale below c)."""
    c = Vector(c)
    s = scale
    a.cyl(0.19 * s, 0.1 * s, 0.3 * s, sides=7, loc=c - Vector((0, 0, 0.1 * s)), mat=CREAM)
    a.cyl(0.06 * s, 0.13 * s, 0.09 * s, sides=6, loc=c - Vector((0, 0, 0.17 * s)), mat=STEM)
    rings = [(-0.35, 11, 0.0), (0.12, 10, 0.5), (0.58, 7, 0.2), (1.05, 4, 0.6), (1.57, 1, 0.0)]
    for el, cnt, off in rings:
        for k in range(cnt):
            az = (k + off) * 2 * math.pi / cnt
            d = Vector((math.cos(el) * math.cos(az), math.cos(el) * math.sin(az), math.sin(el)))
            base = c + d * 0.1 * s
            a.cyl(0.095 * s, 0.04 * s, 0.18 * s, sides=3, loc=base, rot=_rot_to(d),
                  mat=CREAM, cap=False)
    if stem_from is not None:
        _stem(a, rng or random.Random(1), stem_from, c - Vector((0, 0, 0.17 * s)), 0.05, r=0.045)


def _roots(a, rng, base=(0, 0), knot_h=0.3, knot_r=0.17, n=5, reach=0.65, r=0.055):
    bx, by = base
    a.cyl(knot_r, knot_r * 0.65, knot_h, sides=6, loc=(bx, by, 0), mat=BROWN, twist=0.3)
    az0 = rng.uniform(0, 2 * math.pi)
    for k in range(n):
        az = az0 + k * 2 * math.pi / n + rng.uniform(-0.3, 0.3)
        rr = reach * rng.uniform(0.8, 1.1)
        d = Vector((math.cos(az), math.sin(az), 0))
        p0 = Vector((bx, by, knot_h * 0.5)) + d * knot_r * 0.5
        p1 = Vector((bx, by, 0.06)) + d * rr * 0.5
        p2 = Vector((bx, by, 0.02)) + d * rr
        _cone(a, p0, p1, r, r * 0.65, sides=4)
        _cone(a, p1, p2, r * 0.65, r * 0.15, sides=4)


def _clamp(a):
    for v in a.bm.verts:
        if v.co.z < 0:
            v.co.z = 0.0


def _patch(a, rng, layout, L, base_z=0.22):
    """layout: list of (radius, azimuth, height, tilt)."""
    for rad, az, h, tilt in layout:
        top = Vector((rad * math.cos(az), rad * math.sin(az), h))
        sf = Vector((0.1 * math.cos(az), 0.1 * math.sin(az), base_z))
        _module(a, rng, top, tilt, az, L * rng.uniform(0.92, 1.08), stem_from=sf)


def _ring_layout(rng, specs):
    """specs: list of (count, radius, height, tilt); azimuths evenly spread with jitter."""
    out = []
    for i, (cnt, rad, h, tilt) in enumerate(specs):
        off = rng.uniform(0, 2 * math.pi)
        for k in range(cnt):
            az = off + k * 2 * math.pi / cnt + rng.uniform(-0.25, 0.25)
            out.append((rad * rng.uniform(0.85, 1.1), az, h * rng.uniform(0.92, 1.08), tilt))
    return out


def build(kit):
    fk = kit.flintkit
    out = []

    # ---- HERO ---------------------------------------------------------
    rng = random.Random(11)
    a = fk.Asset("CloverPatch", "V01 CloverPatch")
    _roots(a, rng, n=6, reach=0.95, r=0.07)
    lay = _ring_layout(rng, [(3, 0.25, 1.62, 0.2), (4, 0.66, 1.28, 0.45), (5, 1.0, 0.72, 0.6)])
    _patch(a, rng, lay, 0.6)
    _flower(a, (0.42, 0.38, 2.05), 1.2, stem_from=(0.05, 0.05, 0.25), rng=rng)
    _flower(a, (-0.2, -0.1, 1.75), 1.15, stem_from=(-0.03, 0.0, 0.25), rng=rng)
    _flower(a, (-0.6, -0.5, 1.4), 1.1, stem_from=(-0.05, -0.05, 0.25), rng=rng)
    _clamp(a)
    o = a.finish()
    out.append(kit.tag(o, "hero", collision="none", budget=3000,
                       notes="Clover clump scatter; no sockets."))

    # ---- PARTS --------------------------------------------------------
    rng = random.Random(21)
    a = fk.Asset("CloverLeafModule", "V01 CloverLeafModule")
    _module(a, rng, (0, 0, 0.75), 0.85, -math.pi / 2, 0.6, stem_from=(0, 0.05, 0.0), yaw0=0.3)
    _clamp(a)
    out.append(kit.tag(a.finish(), "part", collision="none", budget=1500, notes="no sockets"))

    a = fk.Asset("CloverLeaflet", "V01 CloverLeaflet")
    M = Matrix.Rotation(math.pi, 4, "Z") @ Matrix.Rotation(math.radians(70), 4, "X")
    _leaflet(a, Matrix.Translation((0, 0, 0.02)) @ M, 1.0, 0.72, 0.16, cup=0.1, keel=0.09, notch=False)
    _clamp(a)
    out.append(kit.tag(a.finish(), "part", collision="none", budget=1500, notes="underside shown"))

    a = fk.Asset("CloverStem", "V01 CloverStem")
    pts = [(0, 0, 0), (0.02, 0, 0.42), (0.05, 0, 0.8), (0.25, 0, 1.2), (0.38, 0, 1.58)]
    a.tube_loop(pts, 0.065, mat=STEM, rseg=6, closed=False)
    _cone(a, (0.03, 0, 0.72), (0.08, 0, 0.88), 0.1, 0.1, sides=6, mat=STEM)
    _cone(a, (0.35, 0, 1.5), (0.39, 0, 1.62), 0.065, 0.1, sides=6, mat=STEM)
    out.append(kit.tag(a.finish(), "part", collision="none", budget=1500, notes="jointed stalk"))

    a = fk.Asset("CloverFlowerHead", "V01 CloverFlowerHead")
    _flower(a, (0, 0, 0.6), 1.25, stem_from=(0, 0, 0), rng=rng)
    out.append(kit.tag(a.finish(), "part", collision="none", budget=1500, notes="no sockets"))

    a = fk.Asset("CloverRootBase", "V01 CloverRootBase")
    _roots(a, rng, knot_h=0.6, knot_r=0.2, n=6, reach=0.8, r=0.08)
    _clamp(a)
    out.append(kit.tag(a.finish(), "part", collision="none", budget=1500, notes="no sockets"))

    # ---- VARIATIONS ---------------------------------------------------
    rng = random.Random(31)
    a = fk.Asset("CloverSingleSprig", "V01 CloverSingleSprig")
    _roots(a, rng, knot_h=0.15, knot_r=0.08, n=4, reach=0.35, r=0.035)
    _module(a, rng, (-0.18, 0.0, 1.25), 0.2, math.pi, 0.48, stem_from=(0, 0, 0.12))
    _module(a, rng, (0.3, 0.05, 0.85), 0.3, 0.0, 0.44, stem_from=(0.02, 0, 0.12))
    _clamp(a)
    out.append(kit.tag(a.finish(), "variant", collision="none", budget=3000, notes="A. Single Sprig"))

    rng = random.Random(41)
    a = fk.Asset("CloverSpreadPatch", "V01 CloverSpreadPatch")
    _roots(a, rng, knot_h=0.2, knot_r=0.15, n=5, reach=0.7)
    lay = _ring_layout(rng, [(3, 0.35, 0.8, 0.2), (5, 0.95, 0.65, 0.45), (6, 1.55, 0.45, 0.6)])
    lay = [(r, az, h, t) for r, az, h, t in lay]
    for rad, az, h, tilt in lay:
        x, y = 1.12 * rad * math.cos(az), 0.98 * rad * math.sin(az)
        top = Vector((x, y, h))
        _module(a, rng, top, tilt, az, 0.5 * rng.uniform(0.92, 1.08),
                stem_from=(0.1 * math.cos(az), 0.1 * math.sin(az), 0.15))
    _flower(a, (0.55, 0.3, 1.05), 1.1, stem_from=(0.05, 0.03, 0.15), rng=rng)
    _flower(a, (-0.75, -0.35, 0.95), 1.05, stem_from=(-0.05, 0, 0.15), rng=rng)
    _clamp(a)
    out.append(kit.tag(a.finish(), "variant", collision="none", budget=3000, notes="B. Spread Patch"))

    rng = random.Random(51)
    a = fk.Asset("CloverFloweringPatch", "V01 CloverFloweringPatch")
    _roots(a, rng, n=5, reach=0.65)
    lay = _ring_layout(rng, [(3, 0.25, 1.45, 0.25), (6, 0.85, 0.95, 0.55)])
    _patch(a, rng, lay, 0.56)
    for c, s in [((0.35, 0.3, 2.5), 0.95), ((-0.45, 0.15, 2.2), 0.9), ((0.6, -0.4, 1.9), 0.85),
                 ((-0.2, -0.45, 1.6), 0.85), ((-0.85, -0.2, 1.3), 0.8)]:
        _flower(a, c, s * 1.15, stem_from=(c[0] * 0.08, c[1] * 0.08, 0.25), rng=rng)
    _clamp(a)
    out.append(kit.tag(a.finish(), "variant", collision="none", budget=3000, notes="C. Flowering Patch"))
    return out
