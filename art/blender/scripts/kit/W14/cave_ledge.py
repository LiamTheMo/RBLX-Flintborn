"""W14 row 4: CaveLedge -- raised stone platform ledge against a cave wall."""
import math
import random

SUBJECT = "CaveLedge"
ROW = 4
HERO_AZIMUTH = -22
SIDE_AZIMUTH = -90

PALETTE = {
    "w14_rock": ("#8C7F7A", 0.95, 0, 0),
    "w14_sand": ("#C8A88C", 1, 0, 0),
    "w14_moss": ("#5C8A2E", 0.9, 0, 0),
}
R, S, M = "w14_rock", "w14_sand", "w14_moss"
TV = 0.05   # per-part tint variation (rock() adds +-5% per face)


# ---------------------------------------------------------------- 2D helpers

def _outline(cx, cy, ax, ay, n=14, p=0.55, seed=1, chip=0.06):
    """Convex rounded-rectangle-ish outline (superellipse), CCW."""
    rng = random.Random(seed)
    pts = []
    for i in range(n):
        t = 2 * math.pi * i / n + 0.15
        c, s = math.cos(t), math.sin(t)
        k = 1.0 - rng.uniform(0, chip)
        pts.append((cx + k * ax * math.copysign(abs(c) ** p, c),
                    cy + k * ay * math.copysign(abs(s) ** p, s)))
    return pts


def _clip(poly, a, b, c):
    """Keep the part of a convex polygon with a*x + b*y <= c."""
    out = []
    n = len(poly)
    for i in range(n):
        p, q = poly[i], poly[(i + 1) % n]
        dp = a * p[0] + b * p[1] - c
        dq = a * q[0] + b * q[1] - c
        if dp <= 0:
            out.append(p)
        if (dp < 0) != (dq < 0) and dp != dq:
            t = dp / (dp - dq)
            out.append((p[0] + t * (q[0] - p[0]), p[1] + t * (q[1] - p[1])))
    return out


def _shrink(poly, d):
    cx = sum(p[0] for p in poly) / len(poly)
    cy = sum(p[1] for p in poly) / len(poly)
    out = []
    for x, y in poly:
        vx, vy = x - cx, y - cy
        L = math.hypot(vx, vy) or 1
        out.append((x - vx / L * d, y - vy / L * d))
    return out


def _perimeter(outline, step):
    """Points every ~step along a closed outline, with the edge direction angle."""
    out = []
    n = len(outline)
    for i in range(n):
        p, q = outline[i], outline[(i + 1) % n]
        L = math.hypot(q[0] - p[0], q[1] - p[1])
        k = max(1, int(round(L / step)))
        ang = math.atan2(q[1] - p[1], q[0] - p[0])
        for j in range(k):
            t = j / k
            out.append((p[0] + t * (q[0] - p[0]), p[1] + t * (q[1] - p[1]), ang))
    return out


# ---------------------------------------------------------------- 3D helpers

def _jit(a, verts, j, floor=0.0):
    for v in verts:
        v.co.x += a.rng.uniform(-j, j)
        v.co.y += a.rng.uniform(-j, j)
        v.co.z = max(floor, v.co.z + a.rng.uniform(-j, j))


def _col(a, x, y, w, d, h, rz=0.0, z0=0.0, taper=0.8, sides=6, j=0.3, tilt=(0, 0)):
    """Angular rock column: faceted prism, flat-ish chipped top."""
    v = a.cyl(w / 2, w / 2 * taper, h, sides=sides, mat=R, twist=a.rng.uniform(0, 1))
    a.transform(v, loc=(x, y, z0), rot=(tilt[0], tilt[1], rz), scale=(1, d / w, 1))
    _jit(a, v, j, floor=0.0)
    return v

def _rim(a, outline, zc, height, step=3.3, depth=2.6, seed=5, skip=None):
    """Chipped rock edge blocks around a deck, centred at height zc."""
    rng = random.Random(seed)
    for x, y, ang in _perimeter(outline, step):
        if skip and skip(x, y):
            continue
        v = a.box((step * rng.uniform(1.0, 1.2), depth * rng.uniform(0.9, 1.15),
                   height * rng.uniform(0.92, 1.06)), mat=R)
        a.transform(v, loc=(x, y, zc + rng.uniform(-.1, .1)),
                    rot=(rng.uniform(-.07, .07), rng.uniform(-.07, .07), ang + rng.uniform(-.15, .15)))
        _jit(a, v, 0.32, floor=0.0)


def _plates(a, outline, cuts, z, thick=0.5, gap=0.25, seed=3):
    """Split a convex outline by lines (a, b, c) into sand plates with seams."""
    rng = random.Random(seed)
    cells = [outline]
    for (la, lb, lc) in cuts:
        nxt = []
        for cell in cells:
            for sgn in (1, -1):
                part = _clip(cell, sgn * la, sgn * lb, sgn * lc)
                if len(part) >= 3:
                    nxt.append(part)
        cells = nxt
    for cell in cells:
        h = thick + rng.uniform(-0.08, 0.1)
        a.poly_prism(_shrink(cell, gap), h, loc=(0, 0, z - thick), mat=S)


def _moss(a, x, y, z, r=0.8):
    a.leaf_cluster(r, loc=(x, y, z), mat=M, lobes=6, squash=0.45, facets=1, floor=z)


def _grass(a, x, y, r=1.1):
    a.leaf_cluster(r, loc=(x, y, 0.0), mat=M, lobes=7, squash=0.8, facets=1, floor=0.0)


def _rubble(a, pts, seed=11):
    rng = random.Random(seed)
    for x, y, s in pts:
        a.rock((s * rng.uniform(0.9, 1.3), s, s * 0.7), loc=(x, y, 0),
               rot=(0, 0, rng.uniform(0, 3)), mat=R, subdiv=1, rough=0.1, facets=12)



def _chunk(a, x, y, z0, size, rz=0.0, tilt=0.18, subdiv=1):
    """Angular rock chunk with its base at z0 (clamped >= 0)."""
    a.rock(size, loc=(x, y, max(0.0, z0)),
           rot=(a.rng.uniform(-tilt, tilt), a.rng.uniform(-tilt, tilt), rz), mat=R,
           subdiv=subdiv, rough=0.14, facets=12, sink=0.0 if z0 > 0.05 else 0.1)


def _block(a, x, y, zc, size, rz=0.0, j=0.35, tilt=0.06):
    v = a.box(size, mat=R)
    a.transform(v, loc=(x, y, zc), rot=(a.rng.uniform(-tilt, tilt), a.rng.uniform(-tilt, tilt), rz))
    _jit(a, v, j, floor=0.0)


def _pillar(a, x, y, w, d, h, rz=0.0):
    """Tall angular wall rock: faceted 5-sided body to the ground + angular block crown."""
    hb = h * 0.62
    v = a.cyl(w * 0.52, w * 0.47, hb, sides=6, mat=R, twist=a.rng.uniform(0, 1))
    a.transform(v, loc=(x, y, 0), rot=(0, 0, rz), scale=(1, d / w, 1))
    _jit(a, v, 0.35, floor=0.0)
    # angular icosahedral crown (20 big facets), face-up so it reads as a chipped block
    hc = h - hb + 2.6
    a.rock((w * 1.12, d * 1.08, hc), loc=(x + a.rng.uniform(-.4, .4), y + a.rng.uniform(-.3, .3), hb - 2.6),
           rot=(0.36 + a.rng.uniform(-.1, .1), a.rng.uniform(-.12, .12), rz), mat=R,
           subdiv=1, rough=0.2, facets=12, sink=0.0)


def _deck(a, outline, ztop, cuts, seed, skip_rim=None, rim_h=2.8):
    """Thick sand deck: sand body + seamed sand plates on top + rock rim blocks."""
    a.poly_prism(_shrink(outline, 0.7), 2.2, loc=(0, 0, ztop - 2.9), mat=S)
    _plates(a, _shrink(outline, 0.9), cuts, ztop, thick=0.8, gap=0.22, seed=seed)
    _rim(a, outline, ztop - rim_h / 2 - 0.2, rim_h, step=3.6, depth=2.5, seed=seed + 1, skip=skip_rim)


def _under(a, deck, ztop, seed, back=None, scale=1.0):
    """Bulky undercut mass: 3 tiers of angular chunks narrowing downwards + solid core."""
    rng = random.Random(seed)
    sk = back or (lambda x, y: False)
    # tier 1: big chunks right under the rim, flush with the deck edge
    for x, y, ang in _perimeter(_shrink(deck, 0.9 * scale), 4.0 * scale):
        if sk(x, y):
            continue
        h = rng.uniform(3.4, 4.3) * scale
        _chunk(a, x, y, ztop - 2.2 - h, (rng.uniform(5.0, 6.2) * scale, 4.8 * scale, h), ang,
               tilt=0.22, subdiv=2)
    # tier 2: hanging chunks recessed further in, reaching low
    for x, y, ang in _perimeter(_shrink(deck, 3.4 * scale), 4.4 * scale):
        if sk(x, y):
            continue
        h = rng.uniform(4.6, 5.8) * scale
        _chunk(a, x, y, max(1.6, ztop - 6.4 * scale - h + 1.6), (rng.uniform(4.8, 5.8) * scale, 5.0 * scale, h),
               ang, tilt=0.22)
    # tier 3: ground columns, ~3+ studs behind the deck edge
    for x, y, ang in _perimeter(_shrink(deck, 5.6 * scale), 5.0 * scale):
        if sk(x, y):
            continue
        _chunk(a, x, y, 0.0, (rng.uniform(4.8, 5.8) * scale, 5.0 * scale, ztop - 3.6), ang, tilt=0.08)
    a.poly_prism(_shrink(deck, 6.5 * scale), ztop - 2.6, loc=(0, 0, 0), mat=R)


# ---------------------------------------------------------------- assets

def _hero(fk):
    a = fk.Asset("CaveLedge", "W14 CaveLedge", tint_var=TV)
    ztop = 9.0
    deck = _outline(1.4, -3.2, 14.6, 9.6, n=13, p=0.78, seed=2, chip=0.1)
    _deck(a, deck, ztop, [(1, 0.32, -5.0), (1, -0.22, 5.5), (0.18, 1, -5.2)], 3,
          skip_rim=lambda x, y: y > 4.0 or x < -11.5)
    _under(a, deck, ztop, 7, back=lambda x, y: y > 3.5 or (x < -10.0 and y > -3.0))
    # back wall (+Y) and left end (-X, back half): highest at the left, down to the ground
    for (x, y, w, d, h, rz) in [(-9.0, 8.4, 7.2, 6.2, 15.6, 0.2), (-3.4, 9.0, 6.6, 5.8, 14.2, -0.3),
                                (2.2, 9.2, 6.8, 5.6, 13.4, 0.4), (7.8, 8.6, 6.4, 5.8, 12.8, -0.2),
                                (12.8, 6.4, 5.8, 5.6, 11.4, 0.5),
                                (-14.4, 4.4, 6.8, 7.0, 16.4, 0.1), (-14.6, -0.8, 6.0, 6.2, 13.8, -0.3)]:
        _pillar(a, x, y, w, d, h, rz)
    # lower boulder pair at the front-left base
    _chunk(a, -12.6, -10.6, 0.0, (5.8, 5.4, 7.4), 0.4, subdiv=2)
    _chunk(a, -8.0, -12.4, 0.0, (4.6, 4.2, 5.2), -0.5, subdiv=2)
    _rubble(a, [(-4.8, -12.6, 1.4), (6.0, -9.5, 1.2), (-16.4, -13.2, 1.1), (12.5, -6.0, 1.3)])
    for (x, y) in [(-8.0, 4.4), (-2.5, 5.6), (4.5, 5.0), (-10.4, -2.0)]:
        _moss(a, x, y, ztop)
    _grass(a, -10.2, -14.2)
    _grass(a, -16.8, -9.0, 0.9)
    _grass(a, 3.5, -9.6, 0.9)
    return a.finish()


def _back_wall(fk):
    a = fk.Asset("CaveLedgeBackWallPanel", "W14 CaveLedge part", tint_var=TV)
    for (x, y, w, h, rz) in [(-7.6, 0.5, 6.0, 14.0, 0.2), (-4.4, -0.7, 5.8, 13.2, -0.3),
                             (-1.2, 0.6, 5.6, 11.8, 0.4), (1.9, -0.6, 5.6, 12.4, -0.2),
                             (5.0, 0.5, 5.2, 11.0, 0.5), (7.9, -0.3, 4.6, 9.2, -0.4)]:
        _pillar(a, x, y, w, 4.8, h, rz)
    _rubble(a, [(9.6, -2.4, 1.0)])
    return a.finish()


def _slab(fk):
    a = fk.Asset("CaveLedgePlatformSlab", "W14 CaveLedge part", tint_var=TV)
    out = _outline(0, 0, 11.4, 7.4, n=12, p=0.3, seed=4, chip=0.03)
    _deck(a, out, 3.2, [(1, 0.3, -3.5), (1, -0.25, 4.0), (0.2, 1, 0.3)], 6, rim_h=2.4)
    rng = random.Random(9)
    for x, y, ang in _perimeter(_shrink(out, 2.5), 4.6):
        _chunk(a, x, y, 0.0, (rng.uniform(4.4, 5.4), 4.2, 1.6), ang, tilt=0.05)
    return a.finish()


def _corner(fk):
    a = fk.Asset("CaveLedgeCornerFiller", "W14 CaveLedge part", tint_var=TV)
    _block(a, -1.7, 0.0, 4.5, (3.8, 6.8, 9.0), 0.08, j=0.45)
    _block(a, 1.8, -0.2, 3.7, (3.6, 6.4, 7.4), -0.1, j=0.45)
    _block(a, 0.2, 0.3, 8.6, (4.2, 4.8, 1.6), 0.4, j=0.3, tilt=0.15)
    return a.finish()


def _corner_small(fk):
    a = fk.Asset("CaveLedgeCornerFillerSmall", "W14 CaveLedge part", tint_var=TV)
    a.rock((3.6, 4.4, 6.2), loc=(-0.6, 0, 0), rot=(0, 0.15, 0.2), mat=R, subdiv=1, facets=16)
    a.rock((3.0, 3.6, 4.0), loc=(1.3, -0.3, 0), rot=(0, -0.12, -0.5), mat=R, subdiv=1, facets=16)
    return a.finish()


def _wall_ledge(fk):
    a = fk.Asset("CaveLedgeWall", "W14 CaveLedge variant", tint_var=TV)
    ztop = 7.5
    deck = _outline(1.0, -3.6, 13.0, 7.6, n=12, p=0.75, seed=12, chip=0.08)
    _deck(a, deck, ztop, [(1, 0.3, -3.5), (1, -0.25, 6.0), (0.2, 1, -4.0)], 13,
          skip_rim=lambda x, y: y > 2.0 or x < -10.0)
    _under(a, deck, ztop, 15, back=lambda x, y: y > 2.0 or (x < -8.0 and y > -5.0), scale=0.9)
    for (x, y, w, d, h, rz) in [(-8.0, 6.6, 7.0, 6.0, 16.0, 0.2), (-2.0, 7.2, 6.8, 5.8, 15.2, -0.3),
                                (4.2, 7.0, 6.8, 5.8, 14.6, 0.4), (10.0, 6.2, 6.2, 5.6, 13.6, -0.2),
                                (-13.2, 2.6, 6.4, 6.6, 16.0, 0.1), (-13.4, -3.6, 5.6, 6.0, 13.6, -0.2)]:
        _pillar(a, x, y, w, d, h, rz)
    for (x, y) in [(-7.0, 2.2), (4.0, 2.6)]:
        _moss(a, x, y, ztop, 0.7)
    _grass(a, -11.0, -10.8, 0.9)
    _rubble(a, [(-8.5, -12.0, 1.3), (9.0, -10.0, 1.1)])
    return a.finish()


def _span(fk):
    a = fk.Asset("CaveLedgeSpan", "W14 CaveLedge variant", tint_var=TV)
    ztop = 10.8
    deck = [(-13.0, -3.6), (-6, -4.1), (0, -3.9), (6, -4.1), (13.0, -3.6),
            (13.6, 0), (13.0, 3.6), (6, 4.1), (0, 3.9), (-6, 4.1), (-13.0, 3.6), (-13.6, 0)]
    _deck(a, deck, ztop, [(1, 0.3, -6.0), (1, -0.25, 0.5), (1, 0.3, 6.5)], 21, rim_h=2.4,
          skip_rim=lambda x, y: abs(x) < 8.5)
    # arch ring: 9 chunky voussoirs around a ~14 wide x 7.5 tall opening; they form the
    # front/back faces of the span (no rim there) so the curve reads clearly
    A, B, t = 6.2, 6.8, 3.4
    n = 11
    for i in range(n):
        th = math.pi * (i + 0.5) / n
        px, pz = (A + t / 2) * math.cos(th), (B + t / 2) * math.sin(th)
        phi = math.pi / 2 - th
        a.ico((1.75, 5.8, t * 0.62), loc=(px, a.rng.uniform(-.2, .2), pz),
              rot=(0, phi, a.rng.uniform(-.08, .08)), mat=R, subdiv=1, jitter=0.18)
    # spandrel fill between the arch shoulders and the deck
    for sx in (-1, 1):
        _chunk(a, sx * 9.8, 0.0, 4.8, (4.6, 10.0, 5.4), sx * 0.3)
        _chunk(a, sx * 7.2, 0.2, 6.6, (3.6, 10.0, 3.6), -sx * 0.3, tilt=0.1)
    # chunky boulder piers at both ends
    for sx in (-1, 1):
        _chunk(a, sx * 12.0, 0.0, 0.0, (7.0, 10.0, 7.2), sx * 0.3, subdiv=2)
        _chunk(a, sx * 11.6, 0.2, 5.2, (6.0, 8.6, 5.0), -sx * 0.4)
        _chunk(a, sx * 8.4, -0.3, 0.0, (3.6, 9.4, 3.8), sx * 0.6)
        _chunk(a, sx * 14.4, -2.2, 0.0, (3.2, 3.4, 3.4), sx, subdiv=1)
    _rubble(a, [(-4.8, -4.4, 1.1), (5.2, 4.2, 1.0), (15.2, 2.8, 1.0)])
    _grass(a, -9.0, -4.4, 0.9)
    _grass(a, 10.5, 4.4, 0.8)
    return a.finish()


def _pit_rim(fk):
    a = fk.Asset("CaveLedgePitRim", "W14 CaveLedge variant", tint_var=TV)
    rng = random.Random(31)
    n = 14
    rc = 13.0
    for i in range(n):
        t = 2 * math.pi * i / n
        _col(a, rc * math.cos(t), rc * math.sin(t), 6.0, 5.6, 4.4, t + math.pi / 2,
             taper=0.94, sides=6, j=0.3)
        t2 = t + math.pi / n
        _col(a, rc * math.cos(t2), rc * math.sin(t2), 5.8, 5.4, 3.0, t2 + math.pi / 2,
             z0=4.0, taper=0.92, sides=6, j=0.25)
        v = a.box((5.8, 6.0, 1.1), mat=R)
        tt = t + rng.uniform(-.03, .03)
        a.transform(v, loc=(rc * math.cos(tt), rc * math.sin(tt), 7.3),
                    rot=(rng.uniform(-.03, .03), rng.uniform(-.03, .03), tt + math.pi / 2))
        _jit(a, v, 0.18)
    for (x, y) in [(10.0, -12.5), (-14.5, -6.0)]:
        _grass(a, x, y, 0.9)
    _rubble(a, [(15.5, 4.0, 1.2), (-6.0, -15.6, 1.0)])
    return a.finish()


def build(kit):
    fk = kit.flintkit
    return [
        kit.tag(_hero(fk), "hero", collision="precise", budget=7000,
                notes="Raised cave ledge: thick sand plate deck on a bulky undercut rock mass, "
                      "angular rock wall at +Y and the back-left. No VFX."),
        kit.tag(_back_wall(fk), "part", collision="hull", budget=1500,
                notes="Back wall panel: merged cluster of 5 tall angular rocks, left tallest."),
        kit.tag(_slab(fk), "part", collision="precise", budget=1500,
                notes="Walkable sand plate slab with rock edge blocks and chunky rock underside."),
        kit.tag(_corner(fk), "part", collision="hull", budget=900,
                notes="Corner filler, blocky 2-rock block (left block in the reference)."),
        kit.tag(_corner_small(fk), "part", collision="hull", budget=700,
                notes="Small angled corner filler (right-hand wedge in the reference)."),
        kit.tag(_wall_ledge(fk), "variant", collision="precise", budget=6000,
                notes="A. Wall Ledge (Attached)"),
        kit.tag(_span(fk), "variant", collision="precise", budget=6000,
                notes="B. Natural Span (Freestanding): arch opening ~14x8."),
        kit.tag(_pit_rim(fk), "variant", collision="precise", budget=6000,
                notes="C. Pit Rim (Encircling): open centre, no floor."),
    ]
