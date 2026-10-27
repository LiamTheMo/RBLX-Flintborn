"""W16 row 3: RuinColumn -- segmented octagonal ruin column, parts and variants."""
import math
import random

SUBJECT = "RuinColumn"
ROW = 3
HERO_AZIMUTH = -22
SIDE_AZIMUTH = 90

PALETTE = {
    "w16_sandstone": ("#CDA877", 0.9, 0, 0),
    "w16_stone_grey": ("#8F8D86", 0.95, 0, 0),
    "w16_ivy": ("#3F8A1A", 0.8, 0, 0),
    "w16_soil": ("#7A4A2A", 0.95, 0, 0),
}

S, G, IVY, SOIL = "w16_sandstone", "w16_stone_grey", "w16_ivy", "w16_soil"
SEG_W, SEG_H = 3.2, 2.9
TWO_TONE = "w16_soil is the ivy vine stems, a different material from the cut sandstone"


# ---------------------------------------------------------------- helpers
def fin(a, uses_soil=True):
    o = a.finish()
    if uses_soil:
        o["kit_two_tone_ok"] = TWO_TONE
    return o


def floor0(a):
    """Flatten anything that dips below the ground plane."""
    for v in a.bm.verts:
        if v.co.z < 0:
            v.co.z = 0.0


def octo(w, d=None, c=None):
    """Chamfered-square outline (CCW), w wide, d deep, corner chamfer c."""
    d = d or w
    c = c if c is not None else min(w, d) * 0.2
    sx, sy = w / 2, d / 2
    return [(-sx + c, -sy), (sx - c, -sy), (sx, -sy + c), (sx, sy - c),
            (sx - c, sy), (-sx + c, sy), (-sx, sy - c), (-sx, -sy + c)]


def chamfer_block(a, w, h, z0=0.0, x=0.0, y=0.0, rz=0.0, c=None, lip=0.16, mat=S):
    """Octagonal (chamfered-square) stone course with an inset lip on top so
    the step edge reads.  Returns its verts."""
    vs = a.poly_prism(octo(w, c=c), h - lip, loc=(x, y, z0), rot=(0, 0, rz), mat=mat)
    vs += a.poly_prism(octo(w - 0.35, c=(c or w * 0.2) * 0.9), lip, loc=(x, y, z0 + h - lip),
                       rot=(0, 0, rz), mat=mat)
    return vs


def seg(a, w=SEG_W, h=SEG_H, ch=0.16):
    """One octagonal shaft drum at the origin (z 0..h) with inset joint bands
    top and bottom so the joints read as grooves.  Returns verts."""
    c = w * 0.24
    vs = a.poly_prism(octo(w - 0.3, c=c * 0.9), ch, mat=S)
    vs += a.poly_prism(octo(w, c=c), h - 2 * ch, loc=(0, 0, ch), mat=S)
    vs += a.poly_prism(octo(w - 0.3, c=c * 0.9), ch, loc=(0, 0, h - ch), mat=S)
    return vs


def broken_seg(a, rng, w=SEG_W, h=SEG_H, ch=0.16):
    """Shaft drum at the origin whose top is snapped off into a jagged, chipped
    slant.  Returns verts."""
    c = w * 0.24
    vs = a.poly_prism(octo(w - 0.3, c=c * 0.9), ch, mat=S)
    main = a.poly_prism(octo(w, c=c), h - ch, loc=(0, 0, ch), mat=S)
    top = [v for v in main if v.co.z > h - 0.01]
    for i, v in enumerate(top):
        ang = math.atan2(v.co.y, v.co.x)
        drop = 0.15 + 1.2 * (0.5 + 0.5 * math.cos(ang - 0.6)) + (0.45 if i % 2 else 0.0)
        v.co.z -= drop + rng.uniform(0, 0.15)
        if i % 3 == 1:  # chipped corners pulled inwards
            v.co.x *= 0.82
            v.co.y *= 0.82
    return vs + main


def base_plinth(a, x=0.0, y=0.0):
    """Two chunky stacked octagonal base courses (6x6x2, 5x5x1.5) = 3.5 tall."""
    chamfer_block(a, 7.4, 2.3, 0.0, x, y, rz=0.0, c=1.4, lip=0.25)
    chamfer_block(a, 6.0, 1.8, 2.3, x, y, rz=0.05, c=1.15, lip=0.22)
    return 4.1


def cap_stone(a, z=0.0, x=0.0, y=0.0, bosses=True):
    """Flared square capital 5x5x2 with a smaller upper slab. Returns verts."""
    k = 1 / math.sqrt(2)
    vs = a.cyl(3.2 / 2 / k, 5.0 / 2 / k, 0.6, sides=4, loc=(x, y, z), mat=S, twist=math.pi / 4)
    vs += a.stone_block((5.0, 5.0, 0.85), loc=(x, y, z + 0.6 + 0.425), mat=S, bevel=0.16, jitter=0.04)
    vs += a.stone_block((4.0, 4.0, 0.55), loc=(x, y, z + 1.45 + 0.275), mat=S, bevel=0.12, jitter=0.03)
    if bosses:
        for sx in (-1, 1):
            for sy in (-1, 1):
                vs += a.cyl(0.45, 0.38, 0.2, sides=6, loc=(x + sx * 1.5, y + sy * 1.5, z + 2.0), mat=S)
    return vs


def fern(a, loc, rng, n=9, h=1.8):
    h *= 1.35
    """Lush fern clump: a fan of broad tilted blades around a small leaf heart."""
    x, y, z = loc
    for i in range(n):
        th = i / n * 2 * math.pi + rng.uniform(-0.25, 0.25)
        tilt = rng.uniform(0.6, 1.1)
        L = h * rng.uniform(0.8, 1.15)
        a.cyl(0.7, 0.0, L, sides=3, loc=(x, y, z), rot=(tilt, 0, th), mat=IVY)
    a.cyl(0.5, 0.0, h * 1.1, sides=3, loc=(x, y, z), rot=(0.2, 0, rng.uniform(0, 6)), mat=IVY)
    a.leaf_cluster(0.75, loc=(x, y, z + 0.45), mat=IVY, lobes=4, squash=0.6, floor=0.0)


def rubble(a, rng, spots):
    """spots: list of (x, y, size, mat). Tumbled chunky cut blocks."""
    for (x, y, s, mat) in spots:
        s *= 1.3
        sz =(s * rng.uniform(0.95, 1.2), s * rng.uniform(0.85, 1.1), s * rng.uniform(0.7, 0.9))
        rot = (rng.uniform(-0.12, 0.12), rng.uniform(-0.12, 0.12), rng.uniform(0, math.pi))
        a.stone_block(sz, loc=(x, y, sz[2] / 2 - 0.05), rot=rot, mat=mat, bevel=min(sz) * 0.16)


def ivy_climb(a, rng, z0, z1, a0, a1, radius, n, cx=0.0, cy=0.0, lr=(0.72, 0.95),
              vine=True, steps=14):
    """Visible brown vine spiralling up a shaft from angle a0 to a1 (degrees),
    with n small leaf clusters set alternately either side of it."""
    pts = []
    for i in range(steps + 1):
        t = i / steps
        ang = math.radians(a0 + (a1 - a0) * t)
        rr = radius + 0.12
        pts.append((cx + math.cos(ang) * rr, cy + math.sin(ang) * rr,
                    z0 + (z1 - z0) * t + (0.15 if i % 2 else -0.1)))
    if vine:
        a.tube_loop(pts, 0.16, mat=SOIL, rseg=4, closed=False)
    for i in range(n):
        t = (i + 0.5) / n
        side = 14 if i % 2 else -14
        ang = math.radians(a0 + (a1 - a0) * t + side + rng.uniform(-6, 6))
        rr = radius + 0.3
        loc = (cx + math.cos(ang) * rr, cy + math.sin(ang) * rr,
               z0 + (z1 - z0) * t + rng.uniform(-0.25, 0.25))
        a.leaf_cluster(rng.uniform(*lr), loc=loc, mat=IVY, lobes=5, squash=0.7, floor=0.0)


SHAFT_R = SEG_W / 2  # flat-face radius of a drum


def column_stack(a, rng, nseg=4, x=0.0, y=0.0):
    z = base_plinth(a, x, y)
    for i in range(nseg):
        vs = seg(a)
        a.transform(vs, loc=(x + rng.uniform(-0.06, 0.06), y + rng.uniform(-0.06, 0.06), z),
                    rot=(0, 0, rng.uniform(-0.07, 0.07)))
        z += SEG_H
    return z


# ---------------------------------------------------------------- assets
def build_hero(kit):
    fk = kit.flintkit
    rng = random.Random(1601)
    a = fk.Asset("RuinColumn", "W16 RuinColumn")
    z = column_stack(a, rng, 4)
    cap_stone(a, z)
    ztop = z + 2.2
    # ivy: vine spiralling from the plinth up the left, round the back, to the cap
    ivy_climb(a, rng, 4.0, z + 0.3, 215, -15, SHAFT_R, 24)
    # second, leaf-only strand thickening the curtain down the front-left face
    ivy_climb(a, rng, 5.0, z + 1.4, 165, 245, SHAFT_R, 9, vine=False, lr=(0.8, 1.0), steps=8)
    # leaves on the plinth steps where the vine starts
    for loc in ((-3.0, 1.4, 4.0), (-3.6, -0.6, 2.6), (-2.8, 3.0, 2.4), (-3.8, 2.0, 1.2)):
        a.leaf_cluster(0.85, loc=loc, mat=IVY, lobes=5, squash=0.7, floor=0.0)
    # clumps over the cap's left-back and right edges
    for loc, r in (((-2.4, 1.6, z + 1.2), 1.0), ((-1.0, 2.6, ztop - 0.2), 0.95),
                   ((2.5, 1.4, z + 1.0), 1.0), ((2.6, -0.6, z + 0.5), 0.85),
                   ((1.2, 2.5, ztop - 0.1), 0.9)):
        a.leaf_cluster(r, loc=loc, mat=IVY, lobes=5, squash=0.7)
    # rubble: big chunky block front-left touching the plinth, one stacked on it
    a.stone_block((3.8, 3.4, 3.0), loc=(-3.9, -3.5, 1.5), rot=(0, 0, 0.32), mat=S, bevel=0.38)
    a.stone_block((2.2, 2.0, 1.7), loc=(-4.3, -3.8, 3.7), rot=(0.12, -0.1, 0.9), mat=S, bevel=0.28)
    a.stone_block((2.8, 2.5, 2.2), loc=(3.9, -3.0, 1.1), rot=(0, 0.05, -0.4), mat=S, bevel=0.3)
    rubble(a, rng, [(-4.7, 1.0, 2.0, S), (4.4, 0.6, 1.8, S), (3.8, 3.6, 1.5, S),
                    (0.4, -4.6, 1.5, S), (-1.2, 4.4, 1.3, S), (2.6, -3.4, 0.9, S),
                    (-1.8, -5.9, 0.8, S), (3.2, -5.6, 0.6, G), (-6.5, -2.2, 0.8, S),
                    (6.3, -1.2, 0.7, G), (-3.6, 4.9, 0.7, S), (1.8, 5.4, 0.6, S),
                    (6.0, -4.6, 0.6, S), (-6.2, -5.4, 0.6, G)])
    # lush ferns tucked between the rubble
    for loc in ((-1.6, -4.4, 0), (1.9, -4.6, 0), (-5.4, -1.2, 0), (5.2, -0.9, 0),
                (-4.0, 3.4, 0), (5.6, -3.6, 0), (-6.0, 0.6, 0), (1.6, 4.6, 0)):
        fern(a, loc, rng, n=9, h=1.9)
    floor0(a)
    o = fin(a)
    return kit.tag(o, "hero", collision="hull", budget=6000,
                   notes="Ruin column: 2-tier octagonal plinth, 4 octagonal drums, flared cap; ivy vine, ferns and rubble dressing. No VFX.")


def build_parts(kit):
    fk = kit.flintkit
    out = []
    rng = random.Random(1602)

    a = fk.Asset("RuinColumnCap", "W16 RuinColumnCap")
    cap_stone(a, 0.0)
    out.append(kit.tag(a.finish(), "part", collision="box", budget=1500, notes="Flared capital 5x5x2 with upper slab."))

    a = fk.Asset("RuinColumnShaft", "W16 RuinColumnShaft")
    seg(a)
    out.append(kit.tag(a.finish(), "part", collision="hull", budget=1500, notes="Repeating octagonal shaft drum 3.2x3.2x3."))

    a = fk.Asset("RuinColumnBase", "W16 RuinColumnBase")
    chamfer_block(a, 7.0, 1.7, 0.0, c=1.3, lip=0.22)
    chamfer_block(a, 5.7, 1.3, 1.7, rz=0.05, c=1.1, lip=0.2)
    out.append(kit.tag(a.finish(), "part", collision="box", budget=1500, notes="Stacked octagonal base stone 6x6x3."))

    a = fk.Asset("RuinColumnBrokenCap", "W16 RuinColumnBrokenCap")
    for (sz, loc, rot) in (((2.8, 2.6, 1.6), (-1.0, 0.0, 0.8), (0, 0, 0.3)),
                           ((2.2, 2.3, 1.8), (1.4, 0.2, 0.95), (0.12, -0.15, -0.4))):
        vs = a.stone_block(sz, loc=loc, rot=rot, mat=S, bevel=0.14, jitter=0.12)
        hi = max(v.co.z for v in vs)
        for v in vs:
            if v.co.z > hi - 0.3 and rng.random() < 0.55:
                v.co.z -= rng.uniform(0.3, 0.7)
    floor0(a)
    out.append(kit.tag(a.finish(), "part", collision="hull", budget=1500, notes="Broken cap: two chipped chunks."))

    a = fk.Asset("RuinColumnBrokenShaft", "W16 RuinColumnBrokenShaft")
    broken_seg(a, rng)
    out.append(kit.tag(a.finish(), "part", collision="hull", budget=1500, notes="Shaft drum 3.2x3.2x3 with jagged snapped top."))

    a = fk.Asset("RuinColumnIvy", "W16 RuinColumnIvy")
    pts = [(math.sin(t * 1.3) * 0.5, 0.0, t * 0.5) for t in range(11)]
    a.tube_loop(pts, 0.14, mat=SOIL, rseg=4, closed=False)
    for i in range(8):
        zz = 0.5 + i * 0.6
        a.leaf_cluster(0.62 + (0.12 if i % 3 == 0 else 0.0),
                       loc=(math.sin(zz * 2.6) * 0.5 + (0.45 if i % 2 else -0.45), rng.uniform(-0.2, 0.2), zz),
                       mat=IVY, lobes=5, squash=0.7, floor=0.0)
    out.append(kit.tag(a.finish(), "part", collision="none", budget=1500, notes="Separate ivy overlay: vine + 8 leaf clusters, ~5 tall."))
    return out


def build_full(kit):
    fk = kit.flintkit
    rng = random.Random(1603)
    a = fk.Asset("RuinColumnFull", "W16 RuinColumnFull")
    z = column_stack(a, rng, 4)
    cap_stone(a, z)
    ivy_climb(a, rng, 3.4, z + 0.4, 200, 60, SHAFT_R, 13)
    a.leaf_cluster(0.85, loc=(-1.6, 2.2, z + 2.0), mat=IVY, lobes=5, squash=0.7)
    a.leaf_cluster(0.75, loc=(-2.4, 0.8, z + 1.0), mat=IVY, lobes=5, squash=0.7)
    rubble(a, rng, [(3.7, -1.9, 1.2, S), (-3.6, -2.3, 1.0, S), (-0.9, -3.9, 0.7, G), (2.2, 3.5, 0.8, S)])
    fern(a, (2.6, -3.3, 0), rng, n=7, h=1.6)
    fern(a, (-3.6, 0.6, 0), rng, n=7, h=1.6)
    floor0(a)
    return kit.tag(fin(a), "variant", collision="hull", budget=4000,
                   notes="FULL COLUMN: clean 18-stud column, ivy vine up one side.")


def build_stump(kit):
    fk = kit.flintkit
    rng = random.Random(1604)
    a = fk.Asset("RuinColumnStump", "W16 RuinColumnStump")
    z = base_plinth(a)
    vs = seg(a)
    a.transform(vs, loc=(0, 0, z), rot=(0, 0, 0.04))
    vs = broken_seg(a, rng)
    a.transform(vs, loc=(0.05, -0.04, z + SEG_H), rot=(0, 0, -0.06))
    zt = z + 2 * SEG_H
    for loc, r in (((-0.7, 0.6, zt - 0.5), 0.85), ((1.1, -0.4, zt - 1.0), 0.8),
                   ((0.4, 1.4, zt - 0.9), 0.75), ((-1.5, -0.9, zt - 1.3), 0.75),
                   ((-1.7, 1.0, zt - 1.6), 0.7)):
        a.leaf_cluster(r, loc=loc, mat=IVY, lobes=5, squash=0.7)
    ivy_climb(a, rng, 3.5, zt - 1.3, 250, 170, SHAFT_R, 6)
    rubble(a, rng, [(-3.9, -2.6, 1.6, S), (3.8, -2.2, 1.3, S), (2.4, 3.8, 1.1, S),
                    (-1.5, -4.1, 0.8, G), (4.6, 0.8, 0.7, S)])
    for loc in ((-2.4, -3.5, 0), (3.6, -0.4, 0), (1.0, -3.8, 0), (-3.8, 1.4, 0)):
        fern(a, loc, rng, n=7, h=1.7)
    floor0(a)
    return kit.tag(fin(a), "variant", collision="hull", budget=4000,
                   notes="STUMP (BROKEN): base + 2 drums with snapped top, ivy on top.")


def build_fallen(kit):
    fk = kit.flintkit
    rng = random.Random(1605)
    a = fk.Asset("RuinColumnFallen", "W16 RuinColumnFallen")
    w = 3.5
    L = 3.3
    x = -7.0
    # broken base stone at the left end
    chamfer_block(a, 4.6, 2.3, 0.0, x=-8.9, y=0.2, rz=0.25, c=0.9)
    # 4 drums lying along +X with staggered joints / gaps
    offs = [(0.0, 0.0), (0.12, 0.08), (-0.1, -0.1), (0.2, 0.16)]
    for i in range(4):
        yo, rz = offs[i]
        vs = seg(a, w=w, h=L)
        a.transform(vs, loc=(x, yo, w / 2 + (0.05 if i == 2 else 0.0)), rot=(0, math.pi / 2, rz))
        x += L + 0.22
    # flared cap with slab rolled off the right end, tipped
    vs = cap_stone(a, 0.0)
    a.transform(vs, loc=(x + 0.5, 0.4, 2.45), rot=(0.18, math.pi / 2 + 0.12, -0.25))
    # rubble at the left end and along the front
    rubble(a, rng, [(-10.6, -2.0, 1.5, S), (-7.6, -3.0, 1.3, S), (-10.2, 2.4, 1.2, S),
                    (-5.0, -3.0, 0.9, G), (-10.9, 0.4, 0.9, S), (1.8, -2.9, 0.9, S),
                    (6.2, -3.4, 0.7, G)])
    # ivy draped over the left half of the shaft, with its vine
    pts = [(-9.0, -1.8, 0.2), (-8.4, -1.5, 1.8), (-7.0, -0.6, w + 0.05), (-5.2, 0.4, w + 0.1),
           (-3.4, -0.4, w + 0.1), (-1.6, -1.3, w - 0.2), (0.2, -1.8, 2.6), (1.0, -1.9, 1.2)]
    a.tube_loop(pts, 0.15, mat=SOIL, rseg=4, closed=False)
    for (xx, yy, zz, rr) in [(-8.6, -1.2, 1.8, 0.8), (-7.4, -0.4, 3.7, 0.8), (-6.2, 0.6, 3.8, 0.75),
                             (-5.0, -0.6, 3.9, 0.75), (-3.8, 0.4, 3.8, 0.7), (-2.6, -0.9, 3.7, 0.7),
                             (-1.2, -1.5, 3.2, 0.65), (0.4, -1.9, 2.2, 0.65), (-6.2, -1.9, 2.1, 0.75),
                             (-9.4, 1.6, 1.7, 0.8), (-4.4, 1.7, 2.8, 0.7), (4.2, 1.6, 3.4, 0.6)]:
        a.leaf_cluster(rr + 0.2, loc=(xx, yy, zz), mat=IVY, lobes=5, squash=0.7, floor=0.0)
    for loc in ((-5.8, -2.6, 0), (-0.8, -2.6, 0), (4.0, -2.6, 0), (-9.6, -0.2, 0),
                (4.6, 2.6, 0), (-10.8, -2.6, 0)):
        fern(a, loc, rng, n=7, h=1.7)
    floor0(a)
    return kit.tag(fin(a), "variant", collision="hull", budget=4000,
                   notes="FALLEN COLUMN: 4 drums lying along X (~14 long), cap rolled off the right end, base stone + rubble + ivy at left.")


def build(kit):
    out = [build_hero(kit)]
    out += build_parts(kit)
    out += [build_full(kit), build_stump(kit), build_fallen(kit)]
    return out
